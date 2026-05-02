"use client";

import { useCallback, useEffect, useRef, useState } from "react";

// Web Speech API types (Chrome/Edge expose `webkitSpeechRecognition`).
type SpeechRecognitionResult = {
  isFinal: boolean;
  [index: number]: { transcript: string };
};
type SpeechRecognitionEvent = {
  resultIndex: number;
  results: { length: number; [index: number]: SpeechRecognitionResult };
};
type SpeechRecognitionInstance = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((e: SpeechRecognitionEvent) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
};

function getRecognitionCtor(): { new (): SpeechRecognitionInstance } | null {
  if (typeof window === "undefined") return null;
  const w = window as any;
  return w.SpeechRecognition || w.webkitSpeechRecognition || null;
}

/**
 * Mic input — streams interim transcript, returns final on stop.
 */
export function useSpeechRecognition(opts?: { lang?: string }) {
  const [supported, setSupported] = useState(false);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recRef = useRef<SpeechRecognitionInstance | null>(null);

  useEffect(() => {
    setSupported(!!getRecognitionCtor());
  }, []);

  const start = useCallback(() => {
    const Ctor = getRecognitionCtor();
    if (!Ctor) {
      setError("Voice input is not supported in this browser. Use Chrome or Edge.");
      return;
    }
    setError(null);
    setTranscript("");
    const rec = new Ctor();
    rec.continuous = false;
    rec.interimResults = true;
    rec.lang = opts?.lang ?? "en-US";

    rec.onresult = (e) => {
      let text = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        text += e.results[i][0].transcript;
      }
      setTranscript(text);
    };
    rec.onerror = (e) => {
      setError(e.error || "Speech recognition failed");
      setListening(false);
    };
    rec.onend = () => setListening(false);

    recRef.current = rec;
    try {
      rec.start();
      setListening(true);
    } catch (e: any) {
      setError(e?.message || "Could not start microphone");
    }
  }, [opts?.lang]);

  const stop = useCallback(() => {
    recRef.current?.stop();
    setListening(false);
  }, []);

  const reset = useCallback(() => {
    setTranscript("");
    setError(null);
  }, []);

  return { supported, listening, transcript, error, start, stop, reset };
}

/**
 * Text-to-speech using SpeechSynthesis.
 * Strips markdown so the spoken output sounds natural.
 */
export function stripMarkdownForTTS(md: string): string {
  return md
    .replace(/```[\s\S]*?```/g, "")            // code blocks
    .replace(/`([^`]+)`/g, "$1")                // inline code
    .replace(/!\[[^\]]*\]\([^)]+\)/g, "")       // images
    .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")    // links
    .replace(/^#+\s+/gm, "")                    // headings
    .replace(/(\*\*|__)(.*?)\1/g, "$2")         // bold
    .replace(/(\*|_)(.*?)\1/g, "$2")            // italic
    .replace(/^[-*+]\s+/gm, "")                 // bullets
    .replace(/^\d+\.\s+/gm, "")                 // numbered lists
    .replace(/\|/g, " ")                        // tables
    .replace(/\s{2,}/g, " ")
    .trim();
}

export function useSpeechSynthesis() {
  const [supported, setSupported] = useState(false);
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    setSupported(typeof window !== "undefined" && "speechSynthesis" in window);
  }, []);

  const speak = useCallback((text: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    const synth = window.speechSynthesis;
    synth.cancel();
    const clean = stripMarkdownForTTS(text);
    if (!clean) return;
    const u = new SpeechSynthesisUtterance(clean);
    u.rate = 1.0;
    u.pitch = 1.0;
    u.lang = "en-US";
    // prefer a non-default English voice if one is available
    const voices = synth.getVoices();
    const preferred =
      voices.find((v) => /en[-_]US/i.test(v.lang) && /female|samantha|jenny|aria/i.test(v.name)) ||
      voices.find((v) => /en[-_]US/i.test(v.lang)) ||
      voices.find((v) => /^en/i.test(v.lang));
    if (preferred) u.voice = preferred;
    u.onstart = () => setSpeaking(true);
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    synth.speak(u);
  }, []);

  const stop = useCallback(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      setSpeaking(false);
    }
  }, []);

  return { supported, speaking, speak, stop };
}
