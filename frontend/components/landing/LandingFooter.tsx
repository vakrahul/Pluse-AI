import Link from "next/link";

export function LandingFooter() {
  return (
    <footer className="border-t border-clinical-border bg-clinical-bg py-12">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 sm:flex-row">
        <div className="font-display text-xl text-clinical-ink">PulseIQ</div>
        <p className="text-sm text-clinical-muted">Healthcare sales intelligence · Governed analytics · HCP-centric</p>
        <Link href="/dashboard" className="text-sm font-medium text-pulse-600 hover:text-pulse-700">
          Enter platform →
        </Link>
      </div>
    </footer>
  );
}
