"""LLM service.

Three execution modes (auto-selected at startup):
  1. `hf_api`    — call HuggingFace Inference API (set USE_HF_INFERENCE_API=true).
                   Best for a demo without GPU.
  2. `local_lora`— load base model + LoRA adapter from LORA_ADAPTER_PATH.
                   Used after fine-tuning.
  3. `local_base`— load base model only (no fine-tuning).

Falls back gracefully if imports fail (e.g. torch not installed) — service
returns a clear error rather than crashing the whole API.
"""
from __future__ import annotations

import json
import re
from typing import Optional

import httpx
from loguru import logger

from app.config import Settings
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ItineraryRequest,
    ItineraryResponse,
    ItineraryDay,
    ItineraryActivity,
    ToolCall,
)
from app.prompts.system_prompts import SYSTEM_PROMPT, ITINERARY_PROMPT
from app.services.memory import ConversationMemory
from app.services.rag_service import RAGService
from app.services import tool_router


class LLMService:
    def __init__(self, settings: Settings, rag: RAGService):
        self.settings = settings
        self.rag = rag
        self.memory = ConversationMemory()
        self.ready = False
        self.mode: str = "uninitialized"
        self._tokenizer = None
        self._model = None

    # ---------- Lifecycle ----------

    def initialize(self) -> None:
        if self.settings.use_hf_inference_api and self.settings.hf_api_token:
            self.mode = "hf_api"
            self.ready = True
            logger.info("LLM mode: HuggingFace Inference API")
            return

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
        except ImportError as e:
            logger.error(f"transformers/torch not available: {e}. Set USE_HF_INFERENCE_API=true.")
            self.mode = "unavailable"
            return

        try:
            logger.info(f"Loading base model: {self.settings.base_model}")
            tokenizer = AutoTokenizer.from_pretrained(self.settings.base_model)
            dtype = torch.float16 if torch.cuda.is_available() else torch.float32
            model = AutoModelForCausalLM.from_pretrained(
                self.settings.base_model,
                torch_dtype=dtype,
                device_map="auto" if torch.cuda.is_available() else None,
            )

            if self.settings.has_local_adapter:
                from peft import PeftModel
                logger.info(f"Loading LoRA adapter: {self.settings.lora_adapter_path}")
                model = PeftModel.from_pretrained(model, self.settings.lora_adapter_path)
                self.mode = "local_lora"
            else:
                self.mode = "local_base"

            self._tokenizer = tokenizer
            self._model = model
            self.ready = True
            logger.info(f"LLM mode: {self.mode}")
        except Exception as e:
            logger.exception(f"Failed to load local model: {e}")
            self.mode = "unavailable"

    def reset_session(self, session_id: str) -> None:
        self.memory.reset(session_id)

    # ---------- Public API ----------

    async def chat(self, req: ChatRequest) -> ChatResponse:
        # 1. Append user message to memory
        self.memory.append(req.session_id, "user", req.message)

        # 2. Decide if we should call a tool
        tool_calls: list[ToolCall] = []
        tc = await tool_router.maybe_run_tool(req.message)
        if tc:
            tool_calls.append(tc)

        # 3. Pull RAG context
        rag_hits = self.rag.query(req.message, k=4)
        rag_block = "\n".join(f"- {h.page_content}" for h in rag_hits) if rag_hits else ""

        # 4. Build prompt
        history = self.memory.history(req.session_id)
        prompt = self._build_chat_prompt(
            history=history,
            preferences=req.preferences.model_dump() if req.preferences else None,
            rag_block=rag_block,
            tool_block="\n".join(tool_router.format_tool_result_for_llm(t) for t in tool_calls),
        )

        # 5. Generate
        reply = await self._generate(prompt, max_new_tokens=512, temperature=0.7)

        # 6. Persist assistant turn
        self.memory.append(req.session_id, "assistant", reply)

        return ChatResponse(
            session_id=req.session_id,
            reply=reply,
            tool_calls=tool_calls,
            citations=[h.metadata.get("source", "kb") for h in rag_hits],
        )

    async def generate_itinerary(self, req: ItineraryRequest) -> ItineraryResponse:
        prefs_block = self._format_prefs(req.preferences.model_dump() if req.preferences else None)
        rag_hits = self.rag.query(f"top things to do in {req.destination}", k=6)
        context = "\n".join(f"- {h.page_content}" for h in rag_hits) if rag_hits else "(no extra context)"

        prompt = ITINERARY_PROMPT.format(
            days=req.days,
            destination=req.destination,
            preferences=prefs_block,
            context=context,
        )
        raw = await self._generate(prompt, max_new_tokens=1500, temperature=0.6)
        parsed = self._extract_json(raw)

        if not parsed or "itinerary" not in parsed:
            # Fallback: deterministic skeleton so the demo never crashes
            return self._fallback_itinerary(req)

        days_out = []
        for d in parsed["itinerary"][: req.days]:
            days_out.append(
                ItineraryDay(
                    day=d.get("day", len(days_out) + 1),
                    title=d.get("title", f"Day {len(days_out) + 1}"),
                    activities=[ItineraryActivity(**a) for a in d.get("activities", [])],
                )
            )
        return ItineraryResponse(
            destination=req.destination,
            days=req.days,
            summary=parsed.get("summary", f"{req.days}-day trip to {req.destination}"),
            itinerary=days_out,
        )

    # ---------- Internals ----------

    def _build_chat_prompt(
        self,
        history,
        preferences: Optional[dict],
        rag_block: str,
        tool_block: str,
    ) -> str:
        parts = [SYSTEM_PROMPT]
        if preferences:
            parts.append(f"\n[User preferences]\n{self._format_prefs(preferences)}")
        if rag_block:
            parts.append(f"\n[Knowledge base]\n{rag_block}")
        if tool_block:
            parts.append(f"\n[Live tool results]\n{tool_block}")

        parts.append("\n[Conversation]")
        for m in history:
            tag = "User" if m.role == "user" else "Assistant"
            parts.append(f"{tag}: {m.content}")
        parts.append("Assistant:")
        return "\n".join(parts)

    @staticmethod
    def _format_prefs(prefs: Optional[dict]) -> str:
        if not prefs:
            return "(none specified)"
        lines = []
        for k, v in prefs.items():
            if v in (None, [], ""):
                continue
            lines.append(f"- {k}: {v if not isinstance(v, list) else ', '.join(v)}")
        return "\n".join(lines) or "(none specified)"

    @staticmethod
    def _extract_json(text: str) -> Optional[dict]:
        # Try to grab first {...} block
        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None

    def _fallback_itinerary(self, req: ItineraryRequest) -> ItineraryResponse:
        days = []
        for i in range(req.days):
            days.append(ItineraryDay(
                day=i + 1,
                title=f"Day {i+1} in {req.destination}",
                activities=[
                    ItineraryActivity(time="Morning", title="Explore city center", description="Walking tour of historic landmarks.", estimated_cost="$"),
                    ItineraryActivity(time="Afternoon", title="Local cuisine", description="Try a regional specialty for lunch.", estimated_cost="$$"),
                    ItineraryActivity(time="Evening", title="Sunset viewpoint", description="Wind down with a view.", estimated_cost="$"),
                ],
            ))
        return ItineraryResponse(
            destination=req.destination,
            days=req.days,
            summary=f"A relaxed {req.days}-day exploration of {req.destination}.",
            itinerary=days,
        )

    # ---------- Generation backends ----------

    async def _generate(self, prompt: str, max_new_tokens: int, temperature: float) -> str:
        if self.mode == "hf_api":
            return await self._generate_hf_api(prompt, max_new_tokens, temperature)
        if self.mode in ("local_base", "local_lora"):
            return self._generate_local(prompt, max_new_tokens, temperature)
        return "I'm sorry, the LLM is not available right now. Please configure HF_API_TOKEN or run on a machine with GPU."

    async def _generate_hf_api(self, prompt: str, max_new_tokens: int, temperature: float) -> str:
        # OpenAI-compatible chat completions via HF Inference Providers router.
        # The legacy /models/{id} endpoint was deprecated in late 2025.
        url = "https://router.huggingface.co/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.hf_api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.settings.base_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_new_tokens,
            "temperature": temperature,
        }
        try:
            async with httpx.AsyncClient(timeout=90) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                choices = data.get("choices") or []
                if choices and "message" in choices[0]:
                    return (choices[0]["message"].get("content") or "").strip()
                return str(data)
        except httpx.HTTPStatusError as e:
            logger.error(f"HF router returned {e.response.status_code}: {e.response.text[:300]}")
            return f"⚠️ Inference API error ({e.response.status_code}). Check the backend logs."
        except Exception as e:
            logger.exception(f"HF Inference API call failed: {e}")
            return "I'm having trouble reaching the language model right now. Please try again."

    def _generate_local(self, prompt: str, max_new_tokens: int, temperature: float) -> str:
        import torch
        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
        with torch.no_grad():
            output = self._model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9,
                pad_token_id=self._tokenizer.eos_token_id,
            )
        text = self._tokenizer.decode(output[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return text.strip()
