"use client";

import { motion } from "framer-motion";

const tiers = [
  { name: "Gold", count: 100, pct: 10, color: "bg-amber-500", text: "text-amber-800", bg: "bg-amber-50" },
  { name: "Silver", count: 300, pct: 30, color: "bg-slate-400", text: "text-slate-700", bg: "bg-slate-50" },
  { name: "Bronze", count: 600, pct: 60, color: "bg-orange-700", text: "text-orange-900", bg: "bg-orange-50" },
];

export function HcpPipeline({ liveGold }: { liveGold?: number }) {
  const data = tiers.map((t) =>
    t.name === "Gold" && liveGold ? { ...t, count: liveGold } : t
  );

  return (
    <div className="rounded-2xl border border-clinical-border bg-white p-6 shadow-sm">
      <h3 className="font-semibold text-clinical-ink">HCP Tier Pipeline</h3>
      <p className="mt-1 text-sm text-clinical-muted">Segmentation across 1,000 healthcare professionals</p>

      <div className="mt-6 space-y-4">
        {data.map((tier, i) => (
          <div key={tier.name}>
            <div className="mb-1.5 flex justify-between text-sm">
              <span className={`font-medium ${tier.text}`}>{tier.name}</span>
              <span className="text-clinical-muted">{tier.count} HCPs · {tier.pct}%</span>
            </div>
            <div className={`h-2.5 overflow-hidden rounded-full ${tier.bg}`}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${tier.pct}%` }}
                transition={{ delay: 0.3 + i * 0.15, duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                className={`h-full rounded-full ${tier.color}`}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-3 gap-3 border-t border-clinical-border pt-4 text-center">
        {["Cardiology", "Diabetes", "Oncology"].map((spec, i) => (
          <motion.div
            key={spec}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 + i * 0.1 }}
          >
            <p className="text-xs text-clinical-muted">{spec}</p>
            <p className="font-semibold text-clinical-ink">{[150, 120, 100][i]}</p>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
