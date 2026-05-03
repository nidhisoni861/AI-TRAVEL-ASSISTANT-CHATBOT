"use client";

import dynamic from "next/dynamic";

const DashboardView = dynamic(() => import("@/features/dashboard/components/DashboardView"), {
  ssr: false,
});

export default function Page() {
  return <DashboardView />;
}
