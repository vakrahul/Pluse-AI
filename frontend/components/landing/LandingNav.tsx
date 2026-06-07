"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Activity } from "lucide-react";

export function LandingNav() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-clinical-ink/80 backdrop-blur-md"
    >
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-pulse-600">
            <Activity className="h-5 w-5 text-white" strokeWidth={2.5} />
          </div>
          <div>
            <span className="font-display text-lg text-white">PulseIQ</span>
            <span className="ml-2 hidden text-xs text-slate-400 sm:inline">Healthcare Intelligence</span>
          </div>
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <a href="#workflow" className="text-slate-300 transition hover:text-white">How it works</a>
          <a href="#perspectives" className="text-slate-300 transition hover:text-white">Perspectives</a>
          <Link
            href="/dashboard"
            className="rounded-lg bg-pulse-600 px-4 py-2 font-medium text-white transition hover:bg-pulse-500"
          >
            Enter Platform
          </Link>
        </nav>
      </div>
    </motion.header>
  );
}
