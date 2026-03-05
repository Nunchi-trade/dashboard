import React from "react";

interface PlayersPanelProps {
  totalVolume: number;
  totalWallets: number;
  totalMarkets: number;
}

function formatB(value: number): string {
  return `$${(value / 1e9).toFixed(2)}B`;
}

export default function PlayersPanel({
  totalVolume,
  totalWallets,
  totalMarkets,
}: PlayersPanelProps) {
  return (
    <div className="rounded-2xl border border-border bg-white p-6 space-y-5">
      <div className="space-y-1">
        <p className="text-xs uppercase tracking-wider font-semibold text-dark">
          Players
        </p>
        <h2 className="text-sm font-normal text-dark">
          Total Players
        </h2>
        <p className="text-xs text-desc leading-relaxed">
          Aggregate wallets, volumes, markets, and agent flow across Competition I, II, III, and IV.
        </p>
      </div>

      <div className="flex items-center gap-8">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
            Total Volume
          </p>
          <p className="text-2xl font-semibold text-dark">
            {formatB(totalVolume)}
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
            Total Wallets
          </p>
          <p className="text-2xl font-semibold text-dark">
            {totalWallets.toLocaleString()}
          </p>
        </div>
      </div>

      <hr className="border-border" />

      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs font-semibold text-dark">Markets traded</p>
          <p className="text-sm text-muted">{totalMarkets.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-dark">Orders filled value</p>
          <p className="text-sm text-muted">$0</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-dark">Active agents</p>
          <p className="text-sm text-muted">0</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-dark">
            Composite feed window
          </p>
          <p className="text-sm text-muted">Jul 2025 &rarr; Now</p>
        </div>
      </div>
    </div>
  );
}
