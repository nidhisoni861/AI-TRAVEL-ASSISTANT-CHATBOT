"use client";

import { useRef, useState } from "react";
import { LeftSidebar } from "@/components/layout/LeftSidebar";
import { PremiumMap } from "@/features/maps/components/PremiumMap";
import { FloatingAssistant } from "@/features/travel/components/FloatingAssistant";
import { LiveTranslation } from "@/features/translator/components/LiveTranslation";
import { DashboardStats } from "./DashboardStats";
import {
  dashboardCopyByLanguage,
  defaultDashboardCopy,
  initialBookingPrices,
  optimizedBookingPrices,
} from "../data/dashboard-copy";
import type { SupportedLanguage } from "../types/dashboard.types";
import { RefinedItinerary } from "@/features/travel/components/RefinedItinerary";
import { SavedTripsWidget } from "@/features/travel/components/SavedTripsWidget";
import { TravelInsights } from "@/features/travel/components/TravelInsights";
import { TravelOperations } from "@/features/travel/components/TravelOperations";

export default function DashboardView() {
  const [activeSection, setActiveSection] = useState("overview");
  const [assistantOpen, setAssistantOpen] = useState(true);
  const [pageLanguage, setPageLanguage] = useState<SupportedLanguage>("English");
  const [activeStopId, setActiveStopId] = useState(1);
  const [budget, setBudget] = useState(1500);
  const [bookingPrices, setBookingPrices] = useState(initialBookingPrices);
  const copy = dashboardCopyByLanguage[pageLanguage] ?? defaultDashboardCopy;

  const sectionRefs = {
    overview: useRef<HTMLDivElement>(null),
    "trip-planner": useRef<HTMLDivElement>(null),
    "map-route": useRef<HTMLDivElement>(null),
    translation: useRef<HTMLDivElement>(null),
    "saved-trips": useRef<HTMLDivElement>(null),
  };

  const handleSectionChange = (section: string) => {
    setActiveSection(section);
    sectionRefs[section as keyof typeof sectionRefs]?.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  const handleLanguageChange = (language: string) => {
    if (language in dashboardCopyByLanguage) {
      setPageLanguage(language as SupportedLanguage);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#eef3fb] text-slate-950">
      <LeftSidebar activeSection={activeSection} onSectionChange={handleSectionChange} pageLanguage={pageLanguage} onLanguageChange={handleLanguageChange} />

      <main className="h-screen flex-1 overflow-y-auto">
        <div className={`mx-auto max-w-[1660px] space-y-6 p-6 ${assistantOpen ? "2xl:pr-[500px]" : ""}`}>
          <section ref={sectionRefs.overview}>
            <div className="mb-5 flex items-end justify-between gap-4">
              <div>
                <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_14px_rgba(52,211,153,.85)]" />
                  {copy.eyebrow}
                </div>
                <h1 className="text-3xl font-bold tracking-tight text-slate-950">{copy.title}</h1>
                <p className="mt-1 text-sm text-slate-600">
                  {copy.body}
                </p>
              </div>
              <div className="rounded-full border border-blue-200 bg-white/80 px-4 py-2 text-xs font-semibold text-blue-700 shadow-sm">
                {copy.sync}
              </div>
            </div>
            <DashboardStats />
          </section>

          <section ref={sectionRefs["trip-planner"]} className="grid scroll-mt-6 grid-cols-12 gap-6">
            <div ref={sectionRefs["map-route"]} className="col-span-12 grid gap-6 xl:col-span-7">
              <PremiumMap activeStopId={activeStopId} onStopFocus={setActiveStopId} />
              <TravelOperations bookingPrices={bookingPrices} />
            </div>
            <div className="col-span-12 xl:col-span-5">
              <RefinedItinerary activeStopId={activeStopId} onStopChange={setActiveStopId} />
            </div>
          </section>

          <section ref={sectionRefs.translation} className="grid scroll-mt-6 grid-cols-12 gap-6 pb-8">
            <div className="col-span-12 xl:col-span-6">
              <LiveTranslation />
            </div>
            <div ref={sectionRefs["saved-trips"]} className="col-span-12 grid gap-6 xl:col-span-6">
              <SavedTripsWidget />
              <TravelInsights />
            </div>
          </section>
        </div>
      </main>

      <FloatingAssistant
        isOpen={assistantOpen}
        onToggle={() => setAssistantOpen(!assistantOpen)}
        onSetBudget={setBudget}
        onOptimizePrices={() =>
          setBookingPrices(optimizedBookingPrices)
        }
        onFocusStop={setActiveStopId}
      />
    </div>
  );
}
