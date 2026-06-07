"use client";

import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Area, AreaChart,
  LabelList,
} from "recharts";
import type { ChartSpec } from "@/lib/api";

const PALETTE = [
  "#0d9488", "#0f766e", "#14b8a6", "#2dd4bf",
  "#5eead4", "#134e4a", "#0284c7", "#0369a1",
];

const NEUTRAL = "#64748b";

function formatValue(v: unknown): string {
  const n = Number(v);
  if (isNaN(n)) return String(v);
  if (Math.abs(n) >= 1_000_000_000) return `$${(n / 1_000_000_000).toFixed(1)}B`;
  if (Math.abs(n) >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (Math.abs(n) >= 1_000) return n.toLocaleString();
  return n.toFixed(n % 1 === 0 ? 0 : 2);
}

const sharedTooltip = {
  contentStyle: {
    borderRadius: 10,
    border: "1px solid #e2e8f0",
    boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
    fontSize: 12,
    color: "#0f172a",
  },
  cursor: { fill: "rgba(13,148,136,0.06)" },
};

const sharedAxis = {
  tick: { fontSize: 11, fill: NEUTRAL, fontFamily: "var(--font-sans)" },
  axisLine: { stroke: "#e2e8f0" },
  tickLine: false as const,
};

const sharedGrid = { strokeDasharray: "3 3", stroke: "#f1f5f9", vertical: false };

export function ChartRenderer({ spec }: { spec: ChartSpec }) {
  if (!spec?.data?.length) return null;

  const { type, data, xKey, yKeys, title } = spec;

  return (
    <div className="chart-card">
      <div className="mb-4 flex items-start justify-between">
        <div>
          <h3 className="text-sm font-semibold text-clinical-ink">{title}</h3>
          <p className="mt-0.5 text-xs text-clinical-muted">{data.length} data points</p>
        </div>
        <span className="rounded-md bg-pulse-50 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-pulse-700">
          {type}
        </span>
      </div>

      <ResponsiveContainer width="100%" height={280}>
        {type === "line" ? (
          <AreaChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }}>
            <defs>
              {yKeys.map((key, i) => (
                <linearGradient key={key} id={`grad-${i}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={PALETTE[i % PALETTE.length]} stopOpacity={0.18} />
                  <stop offset="95%" stopColor={PALETTE[i % PALETTE.length]} stopOpacity={0} />
                </linearGradient>
              ))}
            </defs>
            <CartesianGrid {...sharedGrid} />
            <XAxis dataKey={xKey} {...sharedAxis} />
            <YAxis {...sharedAxis} tickFormatter={formatValue} width={60} />
            <Tooltip {...sharedTooltip} formatter={(v) => formatValue(v)} />
            <Legend
              wrapperStyle={{ fontSize: 11, paddingTop: 12, color: NEUTRAL }}
              iconType="circle"
              iconSize={7}
            />
            {yKeys.map((key, i) => (
              <Area
                key={key}
                type="monotone"
                dataKey={key}
                stroke={PALETTE[i % PALETTE.length]}
                strokeWidth={2.5}
                fill={`url(#grad-${i})`}
                dot={false}
                activeDot={{ r: 5, strokeWidth: 0 }}
              />
            ))}
          </AreaChart>
        ) : type === "pie" ? (
          <PieChart margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
            <Pie
              data={data}
              dataKey={yKeys[0]}
              nameKey={xKey}
              cx="50%"
              cy="50%"
              outerRadius={100}
              innerRadius={50}
              paddingAngle={3}
              label={({ name, percent }) =>
                `${name} ${(percent * 100).toFixed(0)}%`
              }
              labelLine={false}
            >
              {data.map((_, i) => (
                <Cell key={i} fill={PALETTE[i % PALETTE.length]} stroke="none" />
              ))}
            </Pie>
            <Tooltip
              contentStyle={sharedTooltip.contentStyle}
              formatter={(v) => formatValue(v)}
            />
            <Legend
              wrapperStyle={{ fontSize: 11, color: NEUTRAL }}
              iconType="circle"
              iconSize={7}
            />
          </PieChart>
        ) : (
          <BarChart data={data} margin={{ top: 4, right: 8, bottom: 0, left: 0 }} barCategoryGap="32%">
            <CartesianGrid {...sharedGrid} />
            <XAxis dataKey={xKey} {...sharedAxis} />
            <YAxis {...sharedAxis} tickFormatter={formatValue} width={60} />
            <Tooltip {...sharedTooltip} formatter={(v) => formatValue(v)} />
            <Legend
              wrapperStyle={{ fontSize: 11, paddingTop: 12, color: NEUTRAL }}
              iconType="circle"
              iconSize={7}
            />
            {yKeys.map((key, i) => (
              <Bar
                key={key}
                dataKey={key}
                fill={PALETTE[i % PALETTE.length]}
                radius={[5, 5, 0, 0]}
                maxBarSize={56}
              >
                {data.length <= 6 && (
                  <LabelList
                    dataKey={key}
                    position="top"
                    formatter={formatValue}
                    style={{ fontSize: 10, fill: NEUTRAL }}
                  />
                )}
              </Bar>
            ))}
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
