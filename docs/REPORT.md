# Project Report — AI Travel Assistant Chatbot

> **Course**: Applied Artificial Intelligence — Final Year Project 5
> **Institution**: SRH Hochschule
> **Team**: <add up to 4 names>
> **Date**: <month / year>

---

## 1. Abstract

A short paragraph (~150 words) covering: motivation, the model used (Gemma 2B, fine-tuned with QLoRA), the application surface (multi-turn chat with live travel APIs and RAG), key results, and a one-line conclusion.

## 2. Introduction

### 2.1 Problem statement
Why do travelers need a domain-specialized chatbot? Discuss limitations of generic LLMs (hallucinated prices, outdated POI info, poor multi-turn planning).

### 2.2 Objectives
1. Fine-tune a small open-weight model on travel-domain instruction data.
2. Combine the fine-tuned model with retrieval-augmented generation (RAG) over a curated travel knowledge base.
3. Integrate live data sources (flights, weather, attractions) via a tool-routing layer.
4. Deliver a usable web application with multi-turn chat and a simulated booking flow.

### 2.3 Scope
- **In scope**: Gemma 2B QLoRA fine-tuning, RAG, three live APIs, simulated booking, Next.js UI.
- **Out of scope**: real payment processing, full visa workflows, image generation.

## 3. Related Work

A few short paragraphs:
- Pre-trained LLMs in tourism (cite recent papers — Liu et al. 2023 on travel chatbots, Brown et al. on LLMs).
- LoRA / QLoRA — Hu et al. 2022, Dettmers et al. 2023.
- Retrieval-augmented generation — Lewis et al. 2020.
- Commercial systems for context: Booking.com Smart Filter, Mindtrip, Layla.

## 4. Methodology

### 4.1 Architecture
Insert architecture diagram (the one in `README.md` works; recreate as a proper figure in draw.io / Excalidraw).

### 4.2 Model selection
Justify Gemma 2B over LLaMA 3.1 8B / Mistral 7B for this project:
- Fits a free-tier T4 GPU end-to-end (training + inference).
- Strong instruction-following baseline.
- Permissive license for academic use.

### 4.3 Dataset
- **Sources**: Bitext travel chatbot dataset (~26k Q-A pairs), Wikivoyage city pages, hand-curated examples.
- **Preprocessing**: deduplication, length filtering, chat-template formatting.
- **Final size**: <fill in> training + <fill in> validation.

### 4.4 Fine-tuning (QLoRA)
- Base model loaded in **4-bit NF4** quantization.
- LoRA on attention + MLP projections (`q,k,v,o,gate,up,down`).
- Hyperparameters: rank=16, α=32, lr=2e-4, batch=2×4 grad-accum, 3 epochs, cosine schedule.
- Hardware: Google Colab T4 (16 GB VRAM).
- Training time: <fill in>.

### 4.5 Retrieval-Augmented Generation
- Vector store: ChromaDB (persistent, local).
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2` (384-dim, fast, free).
- Top-k=4 retrieval per query.
- Knowledge base: 20 hand-curated destination summaries + travel tips (extensible).

### 4.6 Tool routing
A deterministic intent classifier dispatches user messages to live API calls:
- weather → OpenWeatherMap
- flights → Amadeus Self-Service
- places (attractions/restaurants/hotels) → Google Places
- itinerary generation → LLM-only path with structured-JSON output

Tool results are formatted as a context block and re-fed to the LLM for the final natural-language reply.

### 4.7 Multi-turn conversation
In-process conversation memory, keyed by session_id, with a sliding window of 20 turns to bound prompt length.

## 5. System Implementation

### 5.1 Backend (FastAPI)
List endpoints:
- `POST /chat` — multi-turn chat
- `POST /flights/search`, `POST /flights/book`
- `POST /weather`, `POST /places`, `POST /itinerary`
- `GET /health`

### 5.2 Frontend (Next.js 14)
- Component breakdown: ChatInterface, Message, ChatInput, PreferencesPanel, FlightList, WeatherCard, PlacesGrid.
- State management: React local state + server-side proxy via `lib/api.ts`.

### 5.3 Deployment
For demo: locally on team laptop. For optional hosting:
- Backend → HuggingFace Spaces (free, includes GPU optional)
- Frontend → Vercel (free)
- Vector DB → Chroma file persisted with the backend container

## 6. Evaluation

### 6.1 Quantitative
- **Perplexity** on held-out validation set: base vs. fine-tuned.
- **BLEU / ROUGE-L** vs. reference answers (small held-out set).
- **Tool-call accuracy** (manually labeled 100-question set): does intent classifier dispatch the right tool?
- **Latency**: median + p95 for chat and itinerary endpoints.

### 6.2 Qualitative — GPT-4 grader
Run a 50-question rubric scoring (1-5 each):
- Helpfulness
- Factual correctness
- Personalization
- Hallucination rate

Compare three configurations: base Gemma, base Gemma + RAG, fine-tuned Gemma + RAG.

### 6.3 User study
If time allows, run a 5-user think-aloud session and record SUS (System Usability Scale).

## 7. Results
Tables and charts. Discuss what worked, what didn't.

## 8. Discussion
- **Strengths**: end-to-end working system, real APIs, multi-turn, runs on a free GPU.
- **Limitations**: small fine-tuning corpus, no real payment, RAG corpus is ~20 docs.
- **Future work**: scale RAG to thousands of docs, add visa lookup tool, voice input, mobile app.

## 9. Conclusion
Three-sentence wrap-up.

## 10. Team Contributions

| Member | Role | Contributions |
|--------|------|---------------|
| Member 1 | Backend / ML | Fine-tuning pipeline, LLM service, RAG |
| Member 2 | Backend / Integrations | Amadeus, OWM, Places services |
| Member 3 | Frontend | Next.js UI, components, UX |
| Member 4 | Data / Eval / Report | Dataset curation, evaluation, documentation |

## 11. References
APA-style references for all cited papers and data sources.

---

### Appendices
- **A.** Full prompt templates (`backend/app/prompts/`).
- **B.** Sample conversation transcripts.
- **C.** Hyperparameter search log.
- **D.** API endpoint OpenAPI spec (auto-generated at `/docs`).
