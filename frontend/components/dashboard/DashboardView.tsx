"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend, LabelList,
} from "recharts";
import {
  Pill, Users, TrendingUp,
} from "lucide-react";
import { RoleSelector } from "./RoleSelector";
import { KpiCard } from "./KpiCard";
import { ROLES, UserRole } from "@/lib/roles";
import { executeQuery } from "@/lib/api";

// ── colour palette ──────────────────────────────────────────────────────────
const PALETTE = ["#0d9488", "#0f766e", "#14b8a6", "#2dd4bf", "#5eead4", "#134e4a"];
const NEUTRAL = "#64748b";
const sharedTooltip = {
  contentStyle: {
    borderRadius: 10,
    border: "1px solid #e2e8f0",
    boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
    fontSize: 12,
  },
};
const sharedAxis = {
  tick: { fontSize: 11, fill: NEUTRAL },
  axisLine: { stroke: "#e2e8f0" },
  tickLine: false as const,
};
const sharedGrid = { strokeDasharray: "3 3", stroke: "#f1f5f9", vertical: false };

function fmt(n: number, type: "currency" | "number" | "percent" = "number"): string {
  if (type === "currency") {
    if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`;
    if (n >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
    return `$${n.toLocaleString()}`;
  }
  if (type === "percent") return `${n.toFixed(1)}%`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K`;
  return n.toLocaleString();
}

const TIER_COLORS: Record<string, string> = {
  Gold: "#b45309",
  Silver: "#64748b",
  Bronze: "#92400e",
};

// ── component ────────────────────────────────────────────────────────────────
export function DashboardView() {
  const searchParams = useSearchParams();
  const initialRole = (searchParams.get("role") as UserRole) || "analyst";
  const [role, setRole] = useState<UserRole>(ROLES[initialRole] ? initialRole : "analyst");
  const config = ROLES[role];

  // Live KPI state
  const [totalSales, setTotalSales] = useState(128_400_000);
  const [totalRx, setTotalRx] = useState(892_000);
  const [totalHcps, setTotalHcps] = useState(1000);
  const [goldCount, setGoldCount] = useState(100);
  const [loading, setLoading] = useState(true);

  // Live chart data
  const [tierChartData, setTierChartData] = useState<{ tier: string; count: number }[]>([]);
  const [specialtyChartData, setSpecialtyChartData] = useState<{ name: string; hcps: number }[]>([]);

  useEffect(() => {
    setLoading(true);
    loadLiveData().finally(() => setLoading(false));
  }, [role]);

  async function loadLiveData() {
    try {
      const [salesRes, rxRes, hcpRes, goldRes, tierRes, specRes] = await Promise.all([
        executeQuery({ measures: ["SalesFact.totalSales"], limit: 1 }),
        executeQuery({ measures: ["PrescriptionFact.totalPrescriptions"], limit: 1 }),
        executeQuery({ measures: ["HcpMaster.count"], limit: 1 }),
        executeQuery({
          measures: ["HcpMaster.count"],
          dimensions: ["HcpMaster.tier"],
          filters: [{ member: "HcpMaster.tier", operator: "equals", values: ["Gold"] }],
          limit: 1,
        }),
        // Live tier breakdown for donut chart
        executeQuery({
          measures: ["HcpMaster.count"],
          dimensions: ["HcpMaster.tier"],
          limit: 10,
        }),
        // Live specialty breakdown for bar chart
        executeQuery({
          measures: ["HcpMaster.count"],
          dimensions: ["HcpMaster.specialty"],
          limit: 10,
        }),
      ]);

      const sales = Number(salesRes?.data?.[0]?.["SalesFact.totalSales"] ?? 0);
      if (sales > 0) setTotalSales(sales);

      const rx = Number(rxRes?.data?.[0]?.["PrescriptionFact.totalPrescriptions"] ?? 0);
      if (rx > 0) setTotalRx(rx);

      const hcps = Number(hcpRes?.data?.[0]?.["HcpMaster.count"] ?? 0);
      if (hcps > 0) setTotalHcps(hcps);

      const gold = Number(goldRes?.data?.[0]?.["HcpMaster.count"] ?? 0);
      if (gold > 0) setGoldCount(gold);

      // Build tier chart data from live query
      if (tierRes?.data?.length) {
        const mapped = tierRes.data
          .map((row: Record<string, unknown>) => ({
            tier: String(row["HcpMaster.tier"] ?? ""),
            count: Number(row["HcpMaster.count"] ?? 0),
          }))
          .filter((r) => r.tier && r.count > 0);
        if (mapped.length) setTierChartData(mapped);
      }

      // Build specialty chart data from live query
      if (specRes?.data?.length) {
        const mapped = specRes.data
          .map((row: Record<string, unknown>) => ({
            name: String(row["HcpMaster.specialty"] ?? ""),
            hcps: Number(row["HcpMaster.count"] ?? 0),
          }))
          .filter((r) => r.name && r.hcps > 0)
          .sort((a, b) => b.hcps - a.hcps)
          .slice(0, 7);
        if (mapped.length) setSpecialtyChartData(mapped);
      }
    } catch {
      /* use defaults */
    }
  }


  const kpis = [
    { label: "Total Prescriptions", value: totalRx, format: "number" as const, icon: Pill, color: "blue" },
    { label: "Total HCPs", value: totalHcps, format: "number" as const, icon: Users, color: "indigo" },
    { label: "Gold Tier HCPs", value: goldCount, format: "number" as const, icon: TrendingUp, color: "amber" },
  ];

  const SectionTitle = ({ children, sub }: { children: React.ReactNode; sub?: string }) => (
    <div className="mb-4">
      <h2 className="text-base font-semibold text-clinical-ink">{children}</h2>
      {sub && <p className="mt-0.5 text-xs text-clinical-muted">{sub}</p>}
    </div>
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"
      >
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-pulse-600">
            {config.label}
          </p>
          <h1 className="mt-1 font-display text-3xl text-clinical-ink sm:text-4xl">
            {config.title}
          </h1>
          <p className="mt-1 max-w-xl text-sm text-clinical-muted">{config.description}</p>
        </div>
        <RoleSelector active={role} onChange={setRole} />
      </motion.div>

      {/* KPI Cards */}
      <AnimatePresence mode="wait">
        <motion.div
          key={role}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.35 }}
          className="grid gap-4 sm:grid-cols-3"
        >
          {kpis.map((kpi, i) => (
            <KpiCard
              key={kpi.label}
              label={kpi.label}
              value={kpi.value}
              format={kpi.format}
              icon={kpi.icon}
              delay={i * 0.08}
              loading={loading}
            />
          ))}
        </motion.div>
      </AnimatePresence>


      {/* Charts row */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="chart-card">
          <SectionTitle sub="By classification tier">HCP Segmentation</SectionTitle>
          {loading ? (
            <div className="flex h-60 items-center justify-center">
              <div className="h-32 w-32 animate-pulse rounded-full bg-slate-100" />
            </div>
          ) : tierChartData.length === 0 ? (
            <p className="py-12 text-center text-sm text-clinical-muted">No tier data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie
                  data={tierChartData}
                  dataKey="count"
                  nameKey="tier"
                  cx="50%"
                  cy="45%"
                  outerRadius={90}
                  innerRadius={48}
                  paddingAngle={3}
                >
                  {tierChartData.map((row) => (
                    <Cell key={row.tier} fill={TIER_COLORS[row.tier] ?? "#0d9488"} stroke="none" />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={sharedTooltip.contentStyle}
                  formatter={(v) => [`${v} HCPs`]}
                />
                <Legend
                  wrapperStyle={{ fontSize: 11, color: NEUTRAL }}
                  iconType="circle"
                  iconSize={7}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Charts row 2 */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Specialty Distribution */}
        <div className="chart-card lg:col-span-2">
          <SectionTitle sub="Number of HCPs per therapeutic area">
            HCPs by Specialty
          </SectionTitle>
          {loading ? (
            <div className="space-y-2 py-4">
              {[80, 65, 55, 45, 35].map((w, i) => (
                <div key={i} className="h-6 animate-pulse rounded bg-slate-100" style={{ width: `${w}%` }} />
              ))}
            </div>
          ) : specialtyChartData.length === 0 ? (
            <p className="py-12 text-center text-sm text-clinical-muted">No specialty data available</p>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart
                data={specialtyChartData}
                layout="vertical"
                margin={{ top: 4, right: 40, bottom: 0, left: 0 }}
              >
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
              <XAxis type="number" {...sharedAxis} tickFormatter={(v) => String(v)} />
              <YAxis type="category" dataKey="name" {...sharedAxis} width={88} />
              <Tooltip contentStyle={sharedTooltip.contentStyle} />
              <Bar dataKey="hcps" fill="#0d9488" radius={[0, 5, 5, 0]} maxBarSize={28}>
                <LabelList
                  dataKey="hcps"
                  position="right"
                  style={{ fontSize: 11, fill: NEUTRAL }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          )}
        </div>

        {/* Quick Questions */}
        <motion.div
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="chart-card"
        >
          <SectionTitle sub={`Tailored for ${config.label}`}>
            Quick Questions
          </SectionTitle>
          <ul className="space-y-2">
            {config.sampleQuestions.slice(0, 4).map((q) => (
              <li key={q}>
                <Link
                  href={`/chat?q=${encodeURIComponent(q)}&role=${role}`}
                  className="block rounded-lg border border-clinical-border px-3 py-2.5 text-sm text-clinical-ink transition hover:border-pulse-300 hover:bg-pulse-50/50"
                >
                  {q}
                </Link>
              </li>
            ))}
          </ul>
          <Link
            href={`/chat?role=${role}`}
            className="mt-4 inline-flex text-sm font-medium text-pulse-600 hover:text-pulse-700"
          >
            Open HCP Copilot →
          </Link>
        </motion.div>
      </div>

      {/* Pipeline Flow */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="rounded-2xl border border-clinical-border bg-gradient-to-r from-pulse-50 to-white p-6"
      >
        <h3 className="text-sm font-semibold text-clinical-ink">Agent Pipeline</h3>
        <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
          {["Question", "Intent Detection", "Query Planning", "Cube · Neo4j · RAG", "Validation", "Chart + Answer"].map(
            (step, i, arr) => (
              <span key={step} className="flex items-center gap-2">
                <span className="rounded-lg border border-clinical-border bg-white px-3 py-1.5 text-xs font-medium text-clinical-ink shadow-sm">
                  {step}
                </span>
                {i < arr.length - 1 && <span className="text-clinical-muted">→</span>}
              </span>
            )
          )}
        </div>
      </motion.div>
    </div>
  );
}
