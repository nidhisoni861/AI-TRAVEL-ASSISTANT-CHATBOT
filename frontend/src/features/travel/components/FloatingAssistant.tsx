import { useEffect, useRef, useState } from "react";
import { Bot, Brain, ChevronDown, Hotel, MapPinned, Maximize2, Mic, Minus, Route, Send, Sparkles, Wallet, X } from "lucide-react";
import { assistantScrollbarStyle, modelOptions, type ModelKey } from "../data/assistant-options";

interface FloatingAssistantProps {
  isOpen: boolean;
  onToggle: () => void;
  onSetBudget: (budget: number) => void;
  onOptimizePrices: () => void;
  onFocusStop: (stopId: number) => void;
}

export function FloatingAssistant({ isOpen, onToggle, onSetBudget, onOptimizePrices, onFocusStop }: FloatingAssistantProps) {
  const [selectedModel, setSelectedModel] = useState<ModelKey>("travel");
  const [showDropdown, setShowDropdown] = useState(false);
  const [showLatest, setShowLatest] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [messages, setMessages] = useState<Array<{ role: "assistant" | "user"; text: string }>>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const latestRef = useRef<HTMLDivElement>(null);
  const selectedModelMeta = modelOptions.find((model) => model.key === selectedModel) ?? modelOptions[1];

  const scrollToLatest = () => latestRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });

  useEffect(() => {
    requestAnimationFrame(scrollToLatest);
  }, [messages]);

  const handleScroll = () => {
    const node = scrollRef.current;
    if (!node) return;
    setShowLatest(node.scrollHeight - node.scrollTop - node.clientHeight > 80);
  };

  const runAssistantAction = (action: "budget" | "prices" | "map" | "hotels") => {
    const actionMap = {
      budget: {
        user: "Set my trip budget to EUR 1,200 and rebalance the dashboard.",
        assistant: "I set the assistant target budget to EUR 1,200. Budget widgets now use the new constraint.",
        effect: () => onSetBudget(1200),
      },
      prices: {
        user: "Find cheaper tickets and transport options.",
        assistant: "I optimized ticket and transport estimates. Booking prices were reduced where cheaper options are realistic.",
        effect: onOptimizePrices,
      },
      map: {
        user: "Show Louvre Museum on the map.",
        assistant: "I focused the map on Louvre Museum and highlighted the matching itinerary stop.",
        effect: () => onFocusStop(2),
      },
      hotels: {
        user: "Ask me what kind of hotel I prefer.",
        assistant: "What hotel style should I use: budget, boutique, family-friendly, or closest to the route?",
        effect: () => undefined,
      },
    };

    const selected = actionMap[action];
    selected.effect();
    setMessages((items) => [...items, { role: "user", text: selected.user }, { role: "assistant", text: selected.assistant }]);
  };

  const sendMessage = () => {
    if (!input.trim()) return;
    setMessages((items) => [
      ...items,
      { role: "user", text: input },
      { role: "assistant", text: "I can update the visible dashboard once connected to your backend assistant endpoint. For now, use the quick actions to simulate dashboard control." },
    ]);
    setInput("");
  };

  const assistantWindowClassName = isMaximized
    ? "fixed inset-4 z-50 flex flex-col rounded-[26px] border border-white/80 bg-white shadow-[0_32px_90px_rgba(15,23,42,.28),0_0_42px_rgba(99,102,241,.25)]"
    : "fixed bottom-6 right-6 z-50 flex h-[min(820px,calc(100vh-48px))] w-[min(470px,calc(100vw-48px))] flex-col rounded-[26px] border border-white/80 bg-white shadow-[0_32px_90px_rgba(15,23,42,.28),0_0_42px_rgba(99,102,241,.25)]";

  if (!isOpen) {
    return (
      <button onClick={onToggle} className="fixed bottom-6 right-6 z-50 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 via-indigo-500 to-violet-500 text-white shadow-2xl shadow-blue-500/40 transition hover:scale-105">
        <Bot className="h-8 w-8" />
        <span className="absolute -right-0.5 -top-0.5 h-4 w-4 rounded-full border-2 border-white bg-emerald-400 shadow-[0_0_16px_rgba(52,211,153,.9)]" />
      </button>
    );
  }

  return (
    <>
      <section className={assistantWindowClassName}>
        <header className="relative rounded-t-[26px] border-b border-slate-100 bg-[linear-gradient(135deg,#0f172a,#111827_56%,#172554)] px-4 py-3 text-white">
          <div className="flex items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/10 ring-1 ring-white/15">
                <Sparkles className="h-5 w-5 text-blue-200" />
              </div>
              <div className="min-w-0">
                <h2 className="text-sm font-bold">AI Assistant</h2>
                <div className="mt-0.5 flex items-center gap-1.5 text-[11px] text-slate-300">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                  Ready to plan worldwide
                </div>
              </div>
            </div>

            <div className="flex shrink-0 items-center gap-1.5">
              <div className="relative z-50">
                <button onClick={() => setShowDropdown((open) => !open)} className="flex min-w-[150px] items-center justify-between gap-2 rounded-xl border border-white/10 bg-white/10 px-3 py-2 text-xs font-semibold text-white hover:bg-white/15">
                  <span className="flex items-center gap-2">
                    {selectedModel === "travel" ? <Sparkles className="h-3.5 w-3.5 text-blue-200" /> : <Brain className="h-3.5 w-3.5" />}
                    {selectedModelMeta.label}
                  </span>
                  <ChevronDown className="h-3.5 w-3.5" />
                </button>
                {showDropdown && (
                  <div className="absolute right-0 top-11 z-[70] w-64 rounded-2xl border border-slate-200 bg-white p-1 text-slate-900 shadow-2xl">
                    {modelOptions.map((model) => {
                      const Icon = model.key === "travel" ? Sparkles : Brain;
                      const isSelected = selectedModel === model.key;
                      return (
                        <button key={model.key} onClick={() => { setSelectedModel(model.key); setShowDropdown(false); }} className={`flex w-full items-start gap-3 rounded-xl px-3 py-3 text-left transition ${isSelected ? "bg-blue-50 text-blue-700" : "hover:bg-slate-50"}`}>
                          <Icon className="mt-0.5 h-4 w-4" />
                          <span>
                            <span className="block text-sm font-bold">{model.label}</span>
                            <span className="block text-xs text-slate-500">{model.helper}</span>
                          </span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
              <button onClick={onToggle} title="Minimize assistant" className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-300 hover:bg-white/10">
                <Minus className="h-4 w-4" />
              </button>
              <button onClick={() => setIsMaximized((value) => !value)} title={isMaximized ? "Restore assistant" : "Maximize assistant"} className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-300 hover:bg-white/10">
                <Maximize2 className="h-4 w-4" />
              </button>
              <button onClick={onToggle} className="flex h-8 w-8 items-center justify-center rounded-lg text-slate-300 hover:bg-rose-500/20 hover:text-rose-200">
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        </header>

        <div className="relative min-h-0 flex-1 overflow-hidden bg-gradient-to-b from-slate-50 to-white">
          <div ref={scrollRef} onScroll={handleScroll} className="assistant-scroll h-full overflow-y-auto">
            {messages.length === 0 ? (
              <div className="flex min-h-full flex-col justify-start p-5 pt-12">
                <div className="rounded-3xl border border-blue-100 bg-white p-5 text-center shadow-sm">
                  <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 to-violet-500 text-white">
                    <Bot className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-950">Where should we go?</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    Ask for any city or country. I can ask follow-up questions, adjust budgets, optimize prices, and focus dashboard widgets.
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-3 p-5">
                {messages.map((message, index) => (
                  <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[86%] rounded-3xl px-4 py-3 text-sm leading-6 shadow-sm ${message.role === "user" ? "rounded-tr-lg bg-gradient-to-br from-blue-600 to-indigo-600 text-white" : "rounded-tl-lg border border-slate-100 bg-white text-slate-700"}`}>
                      {message.text}
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div ref={latestRef} className="h-4" />
          </div>

          {showLatest && (
            <button onClick={scrollToLatest} className="absolute bottom-3 left-1/2 z-30 -translate-x-1/2 rounded-full bg-slate-950 px-3 py-1.5 text-xs font-semibold text-white shadow-xl">
              Scroll to latest
            </button>
          )}
        </div>

        <footer className="rounded-b-[26px] border-t border-slate-100 bg-white p-4">
          <div className="mb-2 grid grid-cols-2 gap-2">
            <button onClick={() => runAssistantAction("budget")} className="flex items-center gap-2 rounded-xl bg-emerald-50 px-3 py-2 text-xs font-bold text-emerald-700"><Wallet className="h-4 w-4" /> Set EUR 1,200</button>
            <button onClick={() => runAssistantAction("prices")} className="flex items-center gap-2 rounded-xl bg-blue-50 px-3 py-2 text-xs font-bold text-blue-700"><Hotel className="h-4 w-4" /> Optimize prices</button>
            <button onClick={() => runAssistantAction("map")} className="flex items-center gap-2 rounded-xl bg-orange-50 px-3 py-2 text-xs font-bold text-orange-700"><MapPinned className="h-4 w-4" /> Focus Louvre</button>
            <button onClick={() => runAssistantAction("hotels")} className="flex items-center gap-2 rounded-xl bg-violet-50 px-3 py-2 text-xs font-bold text-violet-700"><Route className="h-4 w-4" /> Ask question</button>
          </div>
          <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 p-2">
            <input value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => event.key === "Enter" && sendMessage()} className="min-w-0 flex-1 bg-transparent px-2 text-sm outline-none" placeholder="Ask the assistant to plan any destination..." />
            <button className="flex h-9 w-9 items-center justify-center rounded-xl bg-white text-slate-500 shadow-sm"><Mic className="h-4 w-4" /></button>
            <button onClick={sendMessage} className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/25"><Send className="h-4 w-4" /></button>
          </div>
        </footer>
      </section>

      <style>{assistantScrollbarStyle}</style>
    </>
  );
}
