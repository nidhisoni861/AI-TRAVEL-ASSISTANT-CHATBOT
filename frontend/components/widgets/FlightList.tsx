"use client";

import { Plane, ArrowRight } from "lucide-react";
import { useState } from "react";
import { bookFlight } from "@/lib/api";
import type { FlightOffer } from "@/lib/types";

interface Props {
  offers: FlightOffer[];
  origin?: string;
  destination?: string;
}

export function FlightList({ offers, origin, destination }: Props) {
  const [bookingId, setBookingId] = useState<string | null>(null);
  const [confirmed, setConfirmed] = useState<{ id: string; ref: string } | null>(null);

  async function handleBook(offer: FlightOffer) {
    setBookingId(offer.id);
    try {
      const res = await bookFlight({
        item_id: offer.id,
        passenger_name: "Demo User",
        email: "demo@example.com",
      });
      setConfirmed({ id: offer.id, ref: res.booking_reference });
    } catch (e) {
      alert("Booking failed");
    } finally {
      setBookingId(null);
    }
  }

  if (!offers?.length) return null;

  return (
    <div className="rounded-2xl bg-white border border-slate-200 p-4 my-2 animate-fade-in">
      <div className="flex items-center gap-2 text-sm text-slate-500 mb-3">
        <Plane size={16} className="text-brand-500" />
        <span className="font-medium text-slate-700">Flight options</span>
        {origin && destination && (
          <span className="text-xs">· {origin} <ArrowRight className="inline" size={12} /> {destination}</span>
        )}
      </div>
      <div className="space-y-2">
        {offers.slice(0, 5).map((o) => (
          <div key={o.id} className="flex items-center justify-between rounded-xl border border-slate-100 px-3 py-2 hover:bg-slate-50">
            <div>
              <div className="font-medium">{o.airline}</div>
              <div className="text-xs text-slate-500">
                {fmtTime(o.departure)} → {fmtTime(o.arrival)} · {o.duration.replace("PT", "").toLowerCase()} · {o.stops} stops
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="font-semibold text-slate-800">{o.currency} {o.price_total.toFixed(0)}</div>
              </div>
              {confirmed?.id === o.id ? (
                <span className="text-xs px-2 py-1 rounded-md bg-emerald-100 text-emerald-700 font-medium">
                  ✓ {confirmed.ref}
                </span>
              ) : (
                <button
                  onClick={() => handleBook(o)}
                  disabled={bookingId === o.id}
                  className="px-3 py-1.5 text-xs rounded-md bg-brand-600 text-white font-medium hover:bg-brand-700 disabled:opacity-50"
                >
                  {bookingId === o.id ? "Booking…" : "Book"}
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-2 text-[11px] text-slate-400">Demo booking — no real payment is processed.</div>
    </div>
  );
}

function fmtTime(iso: string) {
  try {
    return iso.slice(11, 16);
  } catch {
    return iso;
  }
}
