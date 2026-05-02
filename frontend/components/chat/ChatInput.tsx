"use client";

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import { Send, Mic, MicOff } from "lucide-react";
import { useSpeechRecognition } from "@/lib/speech";

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState("");
  const ta = useRef<HTMLTextAreaElement>(null);
  const { supported: micSupported, listening, transcript, error, start, stop, reset } =
    useSpeechRecognition();

  // While listening, show interim transcript live in the textarea.
  useEffect(() => {
    if (listening) {
      setValue(transcript);
      autoresize();
    }
  }, [listening, transcript]);

  // When listening ends with a non-empty transcript, send it.
  useEffect(() => {
    if (!listening && transcript.trim()) {
      const text = transcript.trim();
      reset();
      onSend(text);
      setValue("");
      if (ta.current) ta.current.style.height = "auto";
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [listening]);

  function submit() {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
    if (ta.current) ta.current.style.height = "auto";
  }

  function onKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function autoresize() {
    if (!ta.current) return;
    ta.current.style.height = "auto";
    ta.current.style.height = Math.min(ta.current.scrollHeight, 160) + "px";
  }

  function toggleMic() {
    if (listening) stop();
    else start();
  }

  return (
    <div>
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-2 flex gap-2 items-end">
        <textarea
          ref={ta}
          rows={1}
          value={value}
          disabled={disabled}
          onChange={(e) => { setValue(e.target.value); autoresize(); }}
          onKeyDown={onKey}
          placeholder={listening ? "Listening… speak now" : "Where would you like to go?  e.g. 'Plan a 4-day trip to Tokyo'"}
          className="flex-1 resize-none bg-transparent border-0 outline-none text-[15px] px-2 py-2 placeholder-slate-400 max-h-40"
        />

        {micSupported && (
          <button
            type="button"
            onClick={toggleMic}
            disabled={disabled}
            title={listening ? "Stop listening" : "Voice input"}
            aria-label={listening ? "Stop listening" : "Start voice input"}
            className={`h-9 w-9 grid place-items-center rounded-xl transition disabled:opacity-40 disabled:cursor-not-allowed ${
              listening
                ? "bg-red-500 text-white animate-pulse-soft hover:bg-red-600"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            {listening ? <MicOff size={16} /> : <Mic size={16} />}
          </button>
        )}

        <button
          type="button"
          onClick={submit}
          disabled={disabled || !value.trim()}
          className="h-9 w-9 grid place-items-center rounded-xl bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
          aria-label="Send"
        >
          <Send size={16} />
        </button>
      </div>

      {error && (
        <div className="mt-1 text-[11px] text-red-500 text-center">{error}</div>
      )}
      {!micSupported && (
        <div className="mt-1 text-[11px] text-slate-400 text-center">
          Voice input requires Chrome or Edge.
        </div>
      )}
    </div>
  );
}
