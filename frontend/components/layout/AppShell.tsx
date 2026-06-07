"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, BarChart3, LayoutDashboard, MessageSquare } from "lucide-react";
import { clsx } from "clsx";

const nav = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "HCP Copilot", icon: MessageSquare },
  { href: "/analytics", label: "Metrics", icon: BarChart3 },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-60 flex-col border-r border-clinical-border bg-white lg:flex">
        <div className="flex items-center gap-2.5 border-b border-clinical-border px-5 py-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-pulse-600">
            <Activity className="h-4 w-4 text-white" />
          </div>
          <div>
            <Link href="/" className="font-display text-lg text-clinical-ink hover:text-pulse-700">
              PulseIQ
            </Link>
            <p className="text-[10px] uppercase tracking-wider text-clinical-muted">Intelligence</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 p-3">
          {nav.map((item) => {
            const active = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  active
                    ? "bg-pulse-50 text-pulse-800 shadow-sm"
                    : "text-clinical-muted hover:bg-slate-50 hover:text-clinical-ink"
                )}
              >
                <item.icon className={clsx("h-4 w-4", active && "text-pulse-600")} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-clinical-border p-4">
          <Link href="/" className="text-xs text-clinical-muted hover:text-pulse-600">
            ← Back to home
          </Link>
        </div>
      </aside>

      <div className="flex flex-1 flex-col lg:pl-60">
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-clinical-border bg-white/90 px-4 py-3 backdrop-blur-md lg:hidden">
          <Link href="/" className="font-display text-lg">PulseIQ</Link>
          <nav className="flex gap-3 text-sm">
            {nav.map((item) => (
              <Link key={item.href} href={item.href} className="text-clinical-muted hover:text-pulse-600">
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="flex-1 p-4 sm:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
