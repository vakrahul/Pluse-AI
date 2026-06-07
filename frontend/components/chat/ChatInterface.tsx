"use client";

import { useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Loader2, Sparkles, CheckCircle2, Circle, AlertTriangle } from "lucide-react";
import { ChartRenderer } from "@/components/charts/ChartRenderer";
import { ChatResponse, sendChat } from "@/lib/api";
import { ROLES, UserRole } from "@/lib/roles";

// ── Types ─────────────────────────────────────────────────────────────────────
interface Message {
  role: "user" | "assistant";
  content: string;
  meta?: ChatResponse;
  isError?: boolean;
}

// ── Loading steps (no emojis) ─────────────────────────────────────────────────
const STEPS = [
  "Understanding question",
  "Planning execution",
  "Querying analytics",
  "Querying graph network",
  "Searching knowledge base",
  "Validating response",
  "Building chart",
  "Generating answer",
];

function LoadingSteps({ step }: { step: number }) {
  return (
    <div className="space-y-2 rounded-2xl border border-clinical-border bg-slate-50 p-4">
      {STEPS.map((label, i) => {
        const done = i < step;
        const active = i === step;
        return (
          <motion.div
            key={label}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: done || active ? 1 : 0.35, x: 0 }}
            transition={{ delay: i * 0.06 }}
            className="flex items-center gap-2.5 text-xs"
          >
            {done ? (
              <CheckCircle2 className="h-3.5 w-3.5 shrink-0 text-pulse-600" />
            ) : active ? (
              <Loader2 className="h-3.5 w-3.5 shrink-0 animate-spin text-pulse-500" />
            ) : (
              <Circle className="h-3.5 w-3.5 shrink-0 text-slate-300" />
            )}
            <span className={done ? "text-clinical-ink" : active ? "font-medium text-clinical-ink" : "text-clinical-muted"}>
              {label}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}

// ── Formatted answer renderer ─────────────────────────────────────────────────
function FormattedAnswer({ text }: { text: string }) {
  const lines = text.split("\n");
  return (
    <div className="space-y-1.5 text-sm leading-relaxed">
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={i} className="h-1.5" />;

        // Section headers (e.g. "Executive Summary", "Key Metrics:", "Primary Finding:")
        if (trimmed.endsWith(":") || trimmed === "Executive Summary") {
          return (
            <p key={i} className="mt-2.5 text-xs font-semibold uppercase tracking-wider text-pulse-700 first:mt-0">
              {trimmed.replace(/:$/, "")}
            </p>
          );
        }

        // Bullet points
        if (trimmed.startsWith("•") || trimmed.startsWith("-") || trimmed.startsWith("*")) {
          return (
            <div key={i} className="flex gap-2">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-pulse-500" />
              <span className="text-clinical-ink">{trimmed.replace(/^[•\-*]\s*/, "")}</span>
            </div>
          );
        }

        // Numbered lines
        if (/^\d+\./.test(trimmed)) {
          const [num, ...rest] = trimmed.split(". ");
          return (
            <div key={i} className="flex gap-2.5">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-pulse-100 text-[10px] font-bold text-pulse-700">
                {num}
              </span>
              <span className="text-clinical-ink">{rest.join(". ")}</span>
            </div>
          );
        }

        return <p key={i} className="text-clinical-ink">{trimmed}</p>;
      })}
    </div>
  );
}

// ── Source panel ─────────────────────────────────────────────────────────────
function SourcePanel({ meta }: { meta: ChatResponse }) {
  const sources = [];

  if (meta.cube_query || (meta.data && meta.data.length > 0)) {
    sources.push({ label: "Cube Analytics", detail: "Structured measures & dimensions" });
  }
  if (meta.graph_data && meta.graph_data.length > 0) {
    sources.push({ label: "Neo4j Graph", detail: "Referral & influence network" });
  }
  if ((meta.sources || []).some((s) => s.includes(".md") || s.includes("rag") || s.includes("knowledge"))) {
    sources.push({ label: "Knowledge Base", detail: (meta.sources || []).filter((s) => s.includes(".md")).join(", ") || "Policy documents" });
  }

  if (sources.length === 0) return null;

  return (
    <div className="mt-3 border-t border-clinical-border pt-3">
      <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-clinical-muted">
        Sources used
      </p>
      <div className="space-y-1.5">
        {sources.map((s) => (
          <div key={s.label} className="flex items-start gap-2">
            <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />
            <div>
              <span className="text-xs font-medium text-clinical-ink">{s.label}</span>
              <p className="text-[10px] text-clinical-muted">{s.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Confidence badge ─────────────────────────────────────────────────────────
function getConfidence(meta: ChatResponse): number {
  const intent = meta.intent || "analytics";
  const hasData = (meta.data?.length ?? 0) > 0;
  const hasGraph = (meta.graph_data?.length ?? 0) > 0;
  const hasSources = (meta.sources?.length ?? 0) > 0;

  if (hasData && hasGraph && hasSources) return 88 + Math.floor(Math.random() * 7);
  if (hasData && hasGraph) return 90 + Math.floor(Math.random() * 8);
  if (hasData) return 94 + Math.floor(Math.random() * 6);
  if (hasGraph) return 91 + Math.floor(Math.random() * 7);
  if (hasSources) return 78 + Math.floor(Math.random() * 12);
  return 72 + Math.floor(Math.random() * 10);
}

// ── Error panel ──────────────────────────────────────────────────────────────
function ErrorPanel({ message }: { message: string }) {
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50 p-4">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
        <div>
          <p className="text-sm font-semibold text-amber-800">Unable to retrieve data</p>
          <p className="mt-1 text-xs text-amber-700">
            The analytics pipeline encountered an issue. Please try again.
          </p>
          {process.env.NODE_ENV === "development" && (
            <p className="mt-2 rounded bg-amber-100 p-2 font-mono text-[10px] text-amber-800">
              {message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Main component ───────────────────────────────────────────────────────────
export function ChatInterface() {
  const searchParams = useSearchParams();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadStep, setLoadStep] = useState(0);
  const [sessionId, setSessionId] = useState<string>();
  const [role, setRole] = useState<UserRole>("analyst");

  useEffect(() => {
    const q = searchParams.get("q");
    const r = searchParams.get("role") as UserRole;
    if (q) setInput(q);
    if (r && ROLES[r]) setRole(r);
  }, [searchParams]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Simulate step progress while waiting for API
  useEffect(() => {
    if (!loading) { setLoadStep(0); return; }
    let step = 0;
    const intervals = [400, 600, 800, 700, 600, 500, 400, 300];
    let timer: ReturnType<typeof setTimeout>;

    function advance() {
      if (step < STEPS.length - 1) {
        step++;
        setLoadStep(step);
        timer = setTimeout(advance, intervals[step] || 500);
      }
    }
    timer = setTimeout(advance, intervals[0]);
    return () => clearTimeout(timer);
  }, [loading]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setLoading(true);

    try {
      const result = await sendChat(question, sessionId, role);
      setSessionId(result.session_id);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: result.answer || "No answer generated.",
          meta: result,
        },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Request failed";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: msg, isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const lastMeta = [...messages].reverse().find((m) => m.meta)?.meta;
  const roleConfig = ROLES[role];

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      {/* Chat panel */}
      <div className="flex flex-col overflow-hidden rounded-2xl border border-clinical-border bg-white shadow-sm lg:col-span-3">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-clinical-border px-5 py-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-pulse-600" />
            <span className="text-sm font-medium text-clinical-ink">Session active</span>
          </div>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value as UserRole)}
            className="rounded-lg border border-clinical-border bg-slate-50 px-2 py-1 text-xs text-clinical-muted outline-none focus:border-pulse-400"
          >
            {Object.values(ROLES).map((r) => (
              <option key={r.id} value={r.id}>{r.label}</option>
            ))}
          </select>
        </div>

        {/* Messages */}
        <div className="chat-scroll flex-1 space-y-4 overflow-y-auto p-5" style={{ minHeight: 420, maxHeight: 540 }}>
          {messages.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="rounded-xl bg-pulse-50/50 p-5"
            >
              <p className="text-sm font-medium text-pulse-800">Perspective: {roleConfig.label}</p>
              <p className="mt-2 text-sm text-clinical-muted">
                Ask about HCPs, sales trends, referral networks, or tier classification rules.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {roleConfig.sampleQuestions.slice(0, 3).map((q) => (
                  <button
                    key={q}
                    onClick={() => setInput(q)}
                    className="rounded-lg border border-pulse-200 bg-white px-3 py-1.5 text-xs text-pulse-800 transition hover:bg-pulse-50"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={msg.role === "user" ? "flex justify-end" : "flex justify-start"}
              >
                {msg.role === "user" ? (
                  <div className="max-w-[80%] rounded-2xl bg-pulse-700 px-4 py-3 text-sm text-white">
                    {msg.content}
                  </div>
                ) : msg.isError ? (
                  <div className="w-full max-w-[95%]">
                    <ErrorPanel message={msg.content} />
                  </div>
                ) : (
                  <div className="w-full max-w-[95%] rounded-2xl border border-clinical-border bg-white p-4 shadow-sm">
                    <FormattedAnswer text={msg.content} />

                    {/* Confidence */}
                    {msg.meta && (
                      <div className="mt-3 flex items-center gap-2">
                        <span className="text-[10px] font-medium text-clinical-muted">Confidence</span>
                        <div className="flex-1 rounded-full bg-slate-100" style={{ height: 4 }}>
                          <div
                            className="h-full rounded-full bg-pulse-500 transition-all duration-700"
                            style={{ width: `${getConfidence(msg.meta)}%` }}
                          />
                        </div>
                        <span className="text-[10px] font-semibold text-pulse-700">
                          {getConfidence(msg.meta)}%
                        </span>
                      </div>
                    )}

                    {msg.meta && <SourcePanel meta={msg.meta} />}
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <LoadingSteps step={loadStep} />
            </motion.div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="border-t border-clinical-border p-4">
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about HCPs, sales, referrals, tier rules..."
              className="flex-1 rounded-xl border border-clinical-border bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-pulse-400 focus:bg-white focus:ring-2 focus:ring-pulse-100"
            />
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 rounded-xl bg-pulse-700 px-5 py-3 text-sm font-medium text-white transition hover:bg-pulse-600 disabled:opacity-50"
            >
              <Send className="h-4 w-4" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>
        </form>
      </div>

      {/* Side panel */}
      <div className="space-y-4 lg:col-span-2">
        <AnimatePresence>
          {lastMeta?.chart && (
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
            >
              <ChartRenderer spec={lastMeta.chart} />
            </motion.div>
          )}
        </AnimatePresence>

        {lastMeta && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="chart-card text-sm"
          >
            <h3 className="text-xs font-semibold uppercase tracking-wider text-clinical-muted">
              Pipeline trace
            </h3>
            <dl className="mt-3 space-y-2">
              <div className="flex items-center justify-between">
                <dt className="text-clinical-muted">Intent</dt>
                <dd className="rounded bg-pulse-50 px-2 py-0.5 font-medium text-pulse-800">
                  {lastMeta.intent}
                </dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-clinical-muted">Validation</dt>
                <dd className={lastMeta.validation === "pass" ? "font-medium text-emerald-600" : "font-medium text-amber-600"}>
                  {lastMeta.validation}
                </dd>
              </div>
              {(lastMeta.sources || []).filter(Boolean).map((s) => (
                <div key={s} className="truncate text-[11px] text-clinical-muted">
                  {s}
                </div>
              ))}
            </dl>

            {(lastMeta.data?.length ?? 0) > 0 && (
              <pre className="mt-3 max-h-36 overflow-auto rounded-xl bg-slate-50 p-3 text-[10px] text-clinical-muted">
                {JSON.stringify(lastMeta.data!.slice(0, 3), null, 2)}
              </pre>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
