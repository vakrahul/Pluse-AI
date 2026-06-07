"use client";

import { motion } from "framer-motion";
import { AnimatedNumber } from "@/components/ui/AnimatedNumber";
import { LucideIcon } from "lucide-react";

export function KpiCard({
  label,
  value,
  format,
  icon: Icon,
  delay = 0,
  subtitle,
  loading,
}: {
  label: string;
  value: number;
  format?: "currency" | "percent" | "number";
  icon: LucideIcon;
  delay?: number;
  subtitle?: string;
  loading?: boolean;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className="relative overflow-hidden rounded-2xl border border-clinical-border bg-white p-5 shadow-sm transition hover:shadow-md"
    >
      {/* Subtle gradient accent */}
      <div className="pointer-events-none absolute -right-6 -top-6 h-20 w-20 rounded-full bg-pulse-400/8" />

      <div className="flex items-start justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-clinical-muted">{label}</p>
        <div className="rounded-lg bg-pulse-50 p-2 ring-1 ring-pulse-100">
          <Icon className="h-3.5 w-3.5 text-pulse-600" />
        </div>
      </div>

      {loading ? (
        <div className="mt-3 h-8 w-28 animate-pulse rounded-lg bg-slate-100" />
      ) : (
        <p className="mt-3 font-display text-3xl tracking-tight text-clinical-ink">
          <AnimatedNumber value={value} format={format} />
        </p>
      )}

      {subtitle && (
        <p className="mt-1.5 text-xs text-clinical-muted">{subtitle}</p>
      )}
    </motion.div>
  );
}
