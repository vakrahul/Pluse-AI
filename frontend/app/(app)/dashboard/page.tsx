import { Suspense } from "react";
import { DashboardView } from "@/components/dashboard/DashboardView";

export default function DashboardPage() {
  return (
    <Suspense fallback={<div className="animate-pulse text-clinical-muted">Loading dashboard...</div>}>
      <DashboardView />
    </Suspense>
  );
}
