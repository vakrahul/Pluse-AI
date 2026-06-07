"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { FadeIn } from "@/components/ui/FadeIn";
import { ROLE_LIST } from "@/lib/roles";
import { ArrowUpRight } from "lucide-react";

export function Perspectives() {
  return (
    <section id="perspectives" className="border-t border-clinical-border bg-white py-24">
      <div className="mx-auto max-w-6xl px-6">
        <FadeIn>
          <p className="text-sm font-semibold uppercase tracking-widest text-pulse-600">Role-based views</p>
          <h2 className="mt-2 font-display text-4xl text-clinical-ink">One platform, four perspectives</h2>
          <p className="mt-3 max-w-2xl text-clinical-muted">
            Each role sees relevant KPIs, workflows, and sample questions — not a one-size-fits-all dashboard.
          </p>
        </FadeIn>

        <div className="mt-12 grid gap-5 md:grid-cols-2">
          {ROLE_LIST.map((role, i) => (
            <FadeIn key={role.id} delay={i * 0.08}>
              <Link href={`/dashboard?role=${role.id}`}>
                <motion.article
                  whileHover={{ y: -4 }}
                  transition={{ type: "spring", stiffness: 400, damping: 25 }}
                  className="block h-full rounded-2xl border border-clinical-border p-6 transition hover:border-pulse-300 hover:shadow-lg"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                        {role.label}
                      </span>
                      <h3 className="mt-3 text-lg font-semibold text-clinical-ink">{role.title}</h3>
                    </div>
                    <ArrowUpRight className="h-5 w-5 text-slate-300" />
                  </div>
                  <p className="mt-2 text-sm text-clinical-muted">{role.description}</p>
                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {role.focus.map((f) => (
                      <span key={f} className="rounded-full bg-pulse-50 px-2.5 py-0.5 text-xs text-pulse-700">
                        {f}
                      </span>
                    ))}
                  </div>
                </motion.article>
              </Link>
            </FadeIn>
          ))}
        </div>
      </div>
    </section>
  );
}
