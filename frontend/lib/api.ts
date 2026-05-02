import { BACKEND } from "./utils";
import type { UserPreferences } from "./types";

export interface SendChatArgs {
  sessionId: string;
  message: string;
  preferences?: UserPreferences;
}

export async function sendChat({ sessionId, message, preferences }: SendChatArgs) {
  const res = await fetch(`${BACKEND}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      preferences: preferences ?? null,
    }),
  });
  if (!res.ok) throw new Error(`Chat request failed: ${res.status}`);
  return res.json();
}

export async function resetSession(sessionId: string) {
  await fetch(`${BACKEND}/chat/${sessionId}`, { method: "DELETE" });
}

export interface ItineraryArgs {
  destination: string;
  days: number;
  preferences?: UserPreferences;
}

export async function generateItinerary({ destination, days, preferences }: ItineraryArgs) {
  const res = await fetch(`${BACKEND}/itinerary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ destination, days, preferences }),
  });
  if (!res.ok) throw new Error(`Itinerary failed: ${res.status}`);
  return res.json();
}

export async function bookFlight(args: {
  item_id: string;
  passenger_name: string;
  email: string;
}) {
  const res = await fetch(`${BACKEND}/flights/book`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type: "flight", ...args }),
  });
  if (!res.ok) throw new Error(`Booking failed: ${res.status}`);
  return res.json();
}
