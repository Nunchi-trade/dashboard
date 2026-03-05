import React from "react";

interface HousePanelProps {
  totalTvl: number;
  lpWallets: number;
  nlpTvl: number;
  pendleTvl: number;
  nhypeTvl: number;
}

function formatM(value: number): string {
  return `$${(value / 1e6).toFixed(1)}M`;
}

export default function HousePanel({
  totalTvl,
  lpWallets,
  nlpTvl,
  pendleTvl,
  nhypeTvl,
}: HousePanelProps) {
  const maxBar = Math.max(nlpTvl, pendleTvl, nhypeTvl, 1);

  const bars = [
    {
      label: "nLP",
      value: nlpTvl,
      bg: "bg-gradient-to-r from-[#b8d4a8] to-[#dce8d4]",
    },
    {
      label: "Pendle LP / PT-wNLP",
      value: pendleTvl,
      bg: "bg-gradient-to-r from-[#d4c8a8] to-[#e8e0d0]",
    },
    {
      label: "nHYPE",
      value: nhypeTvl,
      bg: "bg-gradient-to-r from-[#b8b4c0] to-[#d4d0d8]",
    },
  ];

  return (
    <div className="rounded-2xl border border-border bg-white p-6 space-y-5">
      <div className="space-y-1">
        <p className="text-xs uppercase tracking-wider font-semibold text-dark">
          House
        </p>
        <h2 className="text-sm font-normal text-dark">
          House Liquidity Providers
        </h2>
        <p className="text-xs text-desc leading-relaxed">
          Unique wallets across nLP, Pendle LP/PT-wNLP, and staked HYPE in nHYPE.
        </p>
      </div>

      <div className="flex items-center gap-8">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
            Total TVL
          </p>
          <p className="text-2xl font-semibold text-dark">{formatM(totalTvl)}</p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
            LP Wallets
          </p>
          <p className="text-2xl font-semibold text-dark">
            {lpWallets.toLocaleString()}
          </p>
        </div>
      </div>

      <hr className="border-border" />

      <div className="space-y-4">
        {bars.map((bar) => (
          <div key={bar.label} className="space-y-1.5">
            <div className="flex items-center gap-4 text-xs">
              <span className="text-dark font-bold w-[140px]">{bar.label}</span>
              <span className="text-dark">{formatM(bar.value)}</span>
            </div>
            <div className="bg-background h-2 rounded-full overflow-hidden">
              <div
                className={`h-2 rounded-full ${bar.bg}`}
                style={{ width: `${Math.max((bar.value / maxBar) * 100, 2)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
