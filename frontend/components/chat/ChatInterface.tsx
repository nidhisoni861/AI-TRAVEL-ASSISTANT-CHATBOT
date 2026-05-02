"use client";

import { useEffect, useRef, useState } from "react";
import { RefreshCw, Plane, Volume2, VolumeX } from "lucide-react";
import { Message } from "./Message";
import { ChatInput } from "./ChatInput";
import { PreferencesPanel } from "./PreferencesPanel";
import { sendChat, resetSession } from "@/lib/api";
import { newSessionId, BACKEND, detectLanguage } from "@/lib/utils";
import { useSpeechSynthesis } from "@/lib/speech";
import type { ChatMessage, UserPreferences } from "@/lib/types";

const STARTERS = [
  "Plan a 4-day food tour of Tokyo",
  "What's the weather in Reykjavik?",
  "Find flights from FRA to CDG",
  "Best things to do in Barcelona",
];

const SEED: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "👋 Hi, I'm **Wanderly** — your AI travel assistant.\n\nTell me where you'd like to go and I can build itineraries, search live flights, check weather, and find attractions or restaurants. Try one of the prompts below or ask anything.\n\n🎤 Click the mic to speak instead of typing.",
};

export function ChatInterface() {
  const [sessionId, setSessionId] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([SEED]);
  const [prefs, setPrefs] = useState<UserPreferences>({});
  const [busy, setBusy] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const tts = useSpeechSynthesis();
  const lastSpokenIdRef = useRef<string | null>(null);

  useEffect(() => { setSessionId(newSessionId()); }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  // Auto-speak the latest assistant reply when toggle is on.
  useEffect(() => {
    if (!autoSpeak || !tts.supported) return;
    const last = messages[messages.length - 1];
    if (
      last &&
      last.role === "assistant" &&
      !last.pending &&
      last.content &&
      last.id !== lastSpokenIdRef.current
    ) {
      lastSpokenIdRef.current = last.id;
      tts.speak(last.content, detectLanguage(last.content));
    }
  }, [messages, autoSpeak, tts]);

  function toggleAutoSpeak() {
    if (autoSpeak) {
      tts.stop();
      setAutoSpeak(false);
    } else {
      setAutoSpeak(true);
    }
  }

  async function handleSend(text: string) {
    if (!sessionId) return;
    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: "user", content: text };
    const pendingMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "",
      pending: true,
    };
    setMessages((m) => [...m, userMsg, pendingMsg]);
    setBusy(true);
    try {
      const res = await sendChat({ sessionId, message: text, preferences: prefs });
      setMessages((m) =>
        m.map((msg) =>
          msg.id === pendingMsg.id
            ? {
                ...msg,
                content: res.reply || "(no response)",
                toolCalls: res.tool_calls ?? [],
                citations: res.citations ?? [],
                pending: false,
              }
            : msg,
        ),
      );
    } catch (err) {
      setMessages((m) =>
        m.map((msg) =>
          msg.id === pendingMsg.id
            ? { ...msg, content: `⚠️ Sorry, the backend is unreachable at ${BACKEND}. Is FastAPI running there?`, pending: false }
            : msg,
        ),
      );
    } finally {
      setBusy(false);
    }
  }

  async function handleReset() {
    tts.stop();
    if (sessionId) await resetSession(sessionId).catch(() => {});
    setSessionId(newSessionId());
    setMessages([SEED]);
    lastSpokenIdRef.current = null;
  }

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto w-full px-4">
      {/* Header */}
      <div className="flex items-center justify-between py-4">
        <div className="flex items-center gap-2">
          <div className="h-9 w-9 rounded-xl bg-brand-600 grid place-items-center text-white">
            <Plane size={18} />
          </div>
          <div>
            <div className="font-semibold text-slate-800 leading-tight">Wanderly</div>
            <div className="text-[11px] text-slate-500">AI Travel Assistant · fine-tuned Gemma + RAG</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {tts.supported && (
            <button
              type="button"
              onClick={toggleAutoSpeak}
              title={autoSpeak ? "Auto-speak on (click to mute)" : "Auto-speak off"}
              className={`inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border transition ${
                autoSpeak
                  ? "bg-brand-50 border-brand-300 text-brand-700"
                  : "bg-white border-slate-200 text-slate-600 hover:bg-slate-50"
              }`}
            >
              {autoSpeak ? <Volume2 size={14} /> : <VolumeX size={14} />}
              {autoSpeak ? "Voice on" : "Voice off"}
            </button>
          )}
          <PreferencesPanel prefs={prefs} onChange={setPrefs} />
          <button
            type="button"
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50"
          >
            <RefreshCw size={14} /> New chat
          </button>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-4 py-3 pr-1">
        {messages.map((m) => <Message key={m.id} msg={m} />)}
      </div>

      {/* Starters */}
      {messages.length === 1 && (
        <div className="flex flex-wrap gap-2 my-3">
          {STARTERS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => handleSend(s)}
              className="text-xs px-3 py-1.5 rounded-full bg-white border border-slate-200 hover:border-brand-300 hover:bg-brand-50 text-slate-700"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="py-4">
        <ChatInput onSend={handleSend} disabled={busy} />
        <div className="text-[11px] text-slate-400 text-center mt-2">
          Tip: open Preferences to personalize answers (budget, interests, dietary).
        </div>
      </div>
    </div>
  );
}
