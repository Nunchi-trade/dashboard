import React from "react";
import type { PlayerMarket } from "@/lib/types";

interface PlayersPanelProps {
  totalPlayers: number;
  cumulativeVolume: number;
  dayVolume: number;
  markets: PlayerMarket[];
}

function formatV(value: number): string {
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

function formatNum(value: number): string {
  return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function PlayersPanel({ totalPlayers, cumulativeVolume, dayVolume, markets }: PlayersPanelProps) {
  return (
    <div className="bg-white border border-[#e7c6c2] rounded-[7px] p-[25px] flex flex-col gap-5">
      {/* Badge + description */}
      <div className="flex flex-col gap-1">
        <div className="inline-flex">
          <span className="text-xs font-bold text-[#1b1a17] bg-[#e7c6c2]/20 border border-[#e7c6c2] rounded-full px-3 py-0.5">
            PLAYERS
          </span>
        </div>
        <p className="text-sm text-dark leading-5">
          Players trade yield, rates, and volatility markets against House liquidity.
        </p>
      </div>

      {/* Stats row */}
      <div className="flex items-center gap-8">
        <div>
          <p className="text-[10px] uppercase tracking-[0.5px] font-medium text-muted leading-[15px]">
            Total Players
          </p>
          <p className="text-2xl font-semibold text-dark leading-8">
            {totalPlayers.toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-[0.5px] font-medium text-muted leading-[15px]">
            Cumulative Volume
          </p>
          <p className="text-2xl font-semibold text-dark leading-8">
            {formatV(cumulativeVolume)}
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-[0.5px] font-medium text-muted leading-[15px]">
            24HR Volume
          </p>
          <p className="text-2xl font-semibold text-dark leading-8">
            {formatV(dayVolume)}
          </p>
        </div>
      </div>

      <hr className="border-border" />

      {/* Market rows */}
      <div className="flex flex-col gap-4">
        {markets.map((m) => (
          <div key={m.name} className="flex items-center justify-between">
            <span className="text-xs font-bold text-dark w-[200px]">
              {m.name}
            </span>
            <div className="flex items-center justify-between w-[260px] text-[10.5px] font-medium text-[#434651]">
              <span>{formatNum(m.adv)} ADV</span>
              <span>{formatNum(m.oi)} OI</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
