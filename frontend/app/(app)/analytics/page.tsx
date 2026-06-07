"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getMeasures } from "@/lib/api";
import { FadeIn } from "@/components/ui/FadeIn";

export default function AnalyticsPage() {
  const [metrics, setMetrics] = useState<Array<{ name: string; cube_measure: string; business_definition: string }>>([]);

  useEffect(() => {
    getMeasures().then((data) => setMetrics(data.metrics || [])).catch(() => {});
  }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <FadeIn>
        <p className="text-sm font-medium text-pulse-600">Governed metrics</p>
        <h1 className="font-display text-3xl text-clinical-ink">Cube semantic layer</h1>
        <p className="mt-2 text-clinical-muted">
          Agents may only reference these measures. No invented KPIs.
        </p>
      </FadeIn>

      <div className="grid gap-4 md:grid-cols-2">
        {metrics.map((m, i) => (
          <motion.div
            key={m.name}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            className="rounded-2xl border border-clinical-border bg-white p-5 shadow-sm"
          >
            <code className="rounded bg-pulse-50 px-2 py-0.5 text-sm font-semibold text-pulse-800">
              {m.cube_measure}
            </code>
            <p className="mt-3 text-sm leading-relaxed text-clinical-muted">{m.business_definition}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
