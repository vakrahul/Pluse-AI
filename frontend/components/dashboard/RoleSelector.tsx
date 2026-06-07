"use client";

import { motion } from "framer-motion";
import { ROLE_LIST, UserRole } from "@/lib/roles";
import { clsx } from "clsx";

export function RoleSelector({ active, onChange }: { active: UserRole; onChange: (r: UserRole) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {ROLE_LIST.map((role) => (
        <button
          key={role.id}
          onClick={() => onChange(role.id)}
          className={clsx(
            "relative rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-300",
            active === role.id
              ? "text-white shadow-md"
              : "bg-white text-clinical-muted hover:bg-slate-50 hover:text-clinical-ink border border-clinical-border"
          )}
        >
          {active === role.id && (
            <motion.div
              layoutId="role-pill"
              className="absolute inset-0 rounded-xl bg-pulse-700"
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
            />
          )}
          <span className="relative z-10">{role.label}</span>
        </button>
      ))}
    </div>
  );
}
