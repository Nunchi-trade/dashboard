import React from "react";

export default function PageHeader() {
  return (
    <div className="flex flex-col gap-2 items-start">
      <p className="text-[11px] uppercase tracking-[1.65px] font-medium text-muted">
        Stats &bull; House / Players
      </p>
      <h1 className="text-[38px] font-normal text-dark leading-[47.5px] font-serif">
        House &amp; Player Metrics
      </h1>
      <p className="text-xs text-desc leading-[19.5px] max-w-[768px]">
        Track House liquidity, player activity, and competition results across Nunchi in one place.
      </p>
    </div>
  );
}
