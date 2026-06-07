"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Stethoscope } from "lucide-react";
import { HeartTrail } from "./HeartTrail";

export function Hero() {
  return (
    <section className="relative min-h-screen overflow-hidden bg-clinical-ink pt-24 text-white">
      <div className="absolute inset-0 grid-clinical opacity-30" />
      <div className="absolute -right-32 top-32 h-96 w-96 rounded-full bg-pulse-600/10 blur-3xl" />
      <div className="absolute -left-20 bottom-20 h-72 w-72 rounded-full bg-teal-400/5 blur-3xl" />
      <div className="landing-shimmer" />

      <div className="relative mx-auto max-w-6xl px-6 pb-20 pt-16">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="max-w-3xl"
        >
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-pulse-500/30 bg-pulse-500/10 px-4 py-1.5 text-sm text-pulse-300">
            <Stethoscope className="h-4 w-4" />
            Pharma &amp; Healthcare Sales Intelligence
          </div>

          <h1 className="font-display text-5xl leading-tight tracking-tight sm:text-6xl lg:text-7xl">
            Ask your data.
            <br />
            <span className="text-pulse-400">Know every HCP.</span>
          </h1>

          <p className="mt-6 max-w-xl text-lg leading-relaxed text-slate-400">
            PulseIQ connects governed sales analytics, prescriber networks, and compliance knowledge —
            so field teams, managers, and analysts get answers in plain language.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              href="/dashboard"
              className="group inline-flex items-center gap-2 rounded-xl bg-pulse-600 px-6 py-3.5 font-semibold text-white shadow-lg shadow-pulse-900/30 transition hover:bg-pulse-500"
            >
              Open Dashboard
              <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
            </Link>
            <Link
              href="/chat"
              className="inline-flex items-center gap-2 rounded-xl border border-slate-600 px-6 py-3.5 font-medium text-slate-200 transition hover:border-pulse-500 hover:text-white"
            >
              Try HCP Copilot
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 1 }}
          className="mt-20"
        >
          <HeartTrail className="h-16 w-full" />

        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.7 }}
          className="mt-12 grid gap-4 sm:grid-cols-3"
        >
          {[
            { stat: "1,000", label: "HCP profiles", sub: "Cardiology, Diabetes, Oncology" },
            { stat: "125K+", label: "Sales & Rx events", sub: "Governed star schema" },
            { stat: "4", label: "Role perspectives", sub: "Rep · Manager · Med Affairs · Analyst" },
          ].map((item, i) => (
            <motion.div
              key={item.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + i * 0.1 }}
              className="rounded-2xl border border-slate-700/50 bg-slate-800/40 p-5 backdrop-blur-sm"
            >
              <div className="font-display text-3xl text-pulse-400">{item.stat}</div>
              <div className="mt-1 font-medium text-white">{item.label}</div>
              <div className="mt-0.5 text-sm text-slate-500">{item.sub}</div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
