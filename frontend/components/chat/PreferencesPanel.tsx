"use client";

import { useState } from "react";
import { Settings, X } from "lucide-react";
import type { UserPreferences } from "@/lib/types";

interface Props {
  prefs: UserPreferences;
  onChange: (p: UserPreferences) => void;
}

const INTEREST_OPTIONS = ["food", "history", "nature", "adventure", "art", "nightlife", "shopping", "wellness"];

export function PreferencesPanel({ prefs, onChange }: Props) {
  const [open, setOpen] = useState(false);

  function toggleInterest(i: string) {
    const next = prefs.interests?.includes(i)
      ? prefs.interests.filter((x) => x !== i)
      : [...(prefs.interests ?? []), i];
    onChange({ ...prefs, interests: next });
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50"
      >
        <Settings size={14} /> Preferences
      </button>

      {open && (
        <div className="fixed inset-0 z-50 bg-black/30 grid place-items-center p-4" onClick={() => setOpen(false)}>
          <div className="bg-white rounded-2xl p-5 w-full max-w-md shadow-xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold">Travel preferences</h3>
              <button onClick={() => setOpen(false)} className="text-slate-400 hover:text-slate-700"><X size={18} /></button>
            </div>

            <Section title="Budget">
              <Pills
                options={["budget", "mid-range", "luxury"]}
                value={prefs.budget}
                onChange={(v) => onChange({ ...prefs, budget: v as any })}
              />
            </Section>

            <Section title="Travel style">
              <Pills
                options={["solo", "couple", "family", "group"]}
                value={prefs.travel_style}
                onChange={(v) => onChange({ ...prefs, travel_style: v as any })}
              />
            </Section>

            <Section title="Pace">
              <Pills
                options={["relaxed", "balanced", "packed"]}
                value={prefs.pace}
                onChange={(v) => onChange({ ...prefs, pace: v as any })}
              />
            </Section>

            <Section title="Interests">
              <div className="flex flex-wrap gap-1.5">
                {INTEREST_OPTIONS.map((i) => (
                  <button
                    key={i}
                    onClick={() => toggleInterest(i)}
                    className={`px-2.5 py-1 text-xs rounded-full border ${
                      prefs.interests?.includes(i)
                        ? "bg-brand-600 text-white border-brand-600"
                        : "bg-white text-slate-600 border-slate-200 hover:border-slate-300"
                    }`}
                  >
                    {i}
                  </button>
                ))}
              </div>
            </Section>

            <button
              onClick={() => setOpen(false)}
              className="w-full mt-3 px-4 py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-4">
      <div className="text-xs uppercase tracking-wide text-slate-500 mb-1.5">{title}</div>
      {children}
    </div>
  );
}

function Pills({ options, value, onChange }: { options: string[]; value?: string; onChange: (v: string) => void }) {
  return (
    <div className="flex gap-1.5 flex-wrap">
      {options.map((o) => (
        <button
          key={o}
          onClick={() => onChange(o)}
          className={`px-2.5 py-1 text-xs rounded-full border capitalize ${
            value === o
              ? "bg-brand-600 text-white border-brand-600"
              : "bg-white text-slate-600 border-slate-200 hover:border-slate-300"
          }`}
        >
          {o}
        </button>
      ))}
    </div>
  );
}
