"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, Sparkles, Volume2, Square } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSpeechSynthesis } from "@/lib/speech";
import { WeatherCard } from "@/components/widgets/WeatherCard";
import { FlightList } from "@/components/widgets/FlightList";
import { PlacesGrid } from "@/components/widgets/PlacesGrid";
import type { ChatMessage } from "@/lib/types";

export function Message({ msg, autoSpeak }: { msg: ChatMessage; autoSpeak?: boolean }) {
  const isUser = msg.role === "user";
  const tts = useSpeechSynthesis();

  const speakThis = () => tts.speak(msg.content);
  const stopSpeaking = () => tts.stop();

  return (
    <div className={cn("flex gap-3 animate-fade-in", isUser && "flex-row-reverse")}>
      <div
        className={cn(
          "h-8 w-8 rounded-full grid place-items-center shrink-0",
          isUser ? "bg-slate-200 text-slate-700" : "bg-brand-600 text-white",
        )}
      >
        {isUser ? <User size={16} /> : <Sparkles size={16} />}
      </div>

      <div className={cn("max-w-[85%] flex flex-col", isUser && "items-end")}>
        <div
          className={cn(
            "rounded-2xl px-4 py-2.5 prose-chat text-[15px] leading-relaxed",
            isUser
              ? "bg-brand-600 text-white rounded-tr-sm"
              : "bg-white border border-slate-200 text-slate-800 rounded-tl-sm",
            msg.pending && "animate-pulse-soft",
          )}
        >
          {msg.pending ? (
            <span className="text-slate-400">Thinking…</span>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
          )}
        </div>

        {/* TTS button (assistant messages only) */}
        {!isUser && !msg.pending && tts.supported && msg.content && (
          <button
            type="button"
            onClick={tts.speaking ? stopSpeaking : speakThis}
            title={tts.speaking ? "Stop speaking" : "Read aloud"}
            aria-label={tts.speaking ? "Stop speaking" : "Read aloud"}
            className="mt-1 self-start inline-flex items-center gap-1 text-[11px] text-slate-500 hover:text-brand-600 px-2 py-0.5 rounded-md hover:bg-brand-50"
          >
            {tts.speaking ? <Square size={12} fill="currentColor" /> : <Volume2 size={12} />}
            <span>{tts.speaking ? "Stop" : "Read aloud"}</span>
          </button>
        )}

        {/* Tool result widgets */}
        {!isUser && msg.toolCalls?.map((tc, i) => {
          if (tc.tool === "weather") return <WeatherCard key={i} data={tc.result} />;
          if (tc.tool === "flight_search") {
            return (
              <FlightList
                key={i}
                offers={tc.result.offers}
                origin={tc.args.origin as string}
                destination={tc.args.destination as string}
              />
            );
          }
          if (tc.tool === "places") {
            return (
              <PlacesGrid
                key={i}
                places={tc.result.places}
                location={tc.args.location as string}
                category={tc.args.category as string}
              />
            );
          }
          return null;
        })}

        {!isUser && msg.citations && msg.citations.length > 0 && (
          <div className="mt-1 text-[11px] text-slate-400">
            sources: {Array.from(new Set(msg.citations)).join(", ")}
          </div>
        )}
      </div>
    </div>
  );
}
