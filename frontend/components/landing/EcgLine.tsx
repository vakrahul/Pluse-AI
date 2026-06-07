"use client";

export function EcgLine({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 1200 80" className={className} preserveAspectRatio="none">
      <path
        d="M0,40 L80,40 L100,40 L110,20 L120,60 L130,40 L200,40 L220,40 L230,10 L240,70 L250,40 L400,40 L420,40 L430,25 L440,55 L450,40 L600,40 L620,40 L630,15 L640,65 L650,40 L800,40 L820,40 L830,30 L840,50 L850,40 L1000,40 L1020,40 L1030,5 L1040,75 L1050,40 L1200,40"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray="1200"
        className="animate-ecg text-pulse-500/60"
      />
    </svg>
  );
}
