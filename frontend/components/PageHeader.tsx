import React from "react";

export default function PageHeader() {
  return (
    <div className="space-y-2">
      <p className="text-[11px] uppercase tracking-[0.15em] text-muted font-medium">
        Stats &bull; House &mdash; Players
      </p>
      <h1 className="text-[38px] font-normal text-dark leading-tight font-serif">
        Liquidity, competition, and agent activity
      </h1>
      <p className="text-desc text-xs max-w-3xl leading-relaxed">
        A single institutional view of house liquidity providers, player activity,
        agent flow, and competition results across the full Nunchi ecosystem.
      </p>
    </div>
  );
}
