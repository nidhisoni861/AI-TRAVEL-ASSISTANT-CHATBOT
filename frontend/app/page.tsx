"use client";

import dynamic from "next/dynamic";

// Chat is fully interactive (Web Speech API uses `window`). Disabling SSR
// avoids hydration mismatches between server (no window) and client.
const ChatInterface = dynamic(
  () => import("@/components/chat/ChatInterface").then((m) => m.ChatInterface),
  { ssr: false, loading: () => (
    <div className="h-full grid place-items-center text-slate-400 text-sm">Loading Wanderly…</div>
  ) },
);

export default function Home() {
  return (
    <main className="h-screen flex flex-col">
      <ChatInterface />
    </main>
  );
}
