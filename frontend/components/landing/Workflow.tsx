"use client";

import { FadeIn } from "@/components/ui/FadeIn";
import { Database, GitBranch, MessageSquare, Shield } from "lucide-react";

const steps = [
  {
    icon: MessageSquare,
    title: "Ask in natural language",
    desc: "\"Show top cardiologists in Bangalore\" or \"Why is this HCP Gold tier?\"",
    color: "bg-pulse-100 text-pulse-700",
  },
  {
    icon: GitBranch,
    title: "Routed to the right engine",
    desc: "Analytics → Cube · Relationships → Neo4j · Policies → ChromaDB RAG",
    color: "bg-amber-100 text-amber-800",
  },
  {
    icon: Database,
    title: "Governed enterprise data",
    desc: "1,000 HCPs, 125K+ fact rows. Metrics from Cube — never invented.",
    color: "bg-sky-100 text-sky-800",
  },
  {
    icon: Shield,
    title: "Validated & compliant",
    desc: "SQL guardrails, audit trail, compliance policies enforced via RAG.",
    color: "bg-emerald-100 text-emerald-800",
  },
];

export function Workflow() {
  return (
    <section id="workflow" className="bg-clinical-bg py-24">
      <div className="mx-auto max-w-6xl px-6">
        <FadeIn>
          <p className="text-sm font-semibold uppercase tracking-widest text-pulse-600">End-to-end flow</p>
          <h2 className="mt-2 font-display text-4xl text-clinical-ink">From question to trusted answer</h2>
        </FadeIn>

        <div className="mt-14 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, i) => (
            <FadeIn key={step.title} delay={i * 0.1}>
              <div className="group relative h-full rounded-2xl border border-clinical-border bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
                <div className={`inline-flex rounded-xl p-3 ${step.color}`}>
                  <step.icon className="h-5 w-5" />
                </div>
                <div className="absolute right-6 top-6 font-display text-4xl text-slate-100 transition group-hover:text-pulse-100">
                  {i + 1}
                </div>
                <h3 className="mt-4 font-semibold text-clinical-ink">{step.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-clinical-muted">{step.desc}</p>
              </div>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
