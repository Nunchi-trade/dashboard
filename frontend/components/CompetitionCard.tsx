import React from "react";
import { CompetitionInfo } from "@/lib/types";

interface CompetitionCardProps {
  comp: CompetitionInfo;
}

function formatVolume(value: number): string {
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

export default function CompetitionCard({ comp }: CompetitionCardProps) {
  return (
    <div className="rounded-2xl border border-border bg-white p-6 space-y-4">
      {/* Header row: Title + Venue pill */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-xs uppercase tracking-wider font-bold text-dark">
            Competition {comp.num}
          </p>
          <p className="text-xs text-desc">{comp.date}</p>
        </div>
        <span className="rounded-full border border-border bg-background px-3 py-1 text-xs uppercase text-muted font-medium">
          {comp.venue}
        </span>
      </div>

      {/* Duration + Leaderboard row with YP logo on right */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-8">
          <div>
            <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
              Duration
            </p>
            <p className="text-sm font-semibold text-dark">{comp.duration}</p>
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
              Leaderboard
            </p>
            <p className="text-sm font-semibold text-dark">{comp.leaderboard}</p>
          </div>
        </div>

        {/* YP Logo */}
        <div
          className="w-[72px] h-[72px] rounded-full flex items-center justify-center shrink-0"
          style={{
            background:
              "linear-gradient(180deg, #fdecc1 0%, #a87037 100%)",
            padding: "2px",
          }}
        >
          <div className="w-full h-full rounded-full bg-white flex items-center justify-center">
            <span className="text-gold font-serif text-base tracking-[0.3em] leading-none">
              Y<br />P
            </span>
          </div>
        </div>
      </div>

      {/* Volume + PnL stats */}
      <div className="flex items-center gap-6">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
            Volume
          </p>
          <p className="text-lg font-semibold text-dark">
            {formatVolume(comp.volume)}
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
            Net Profit
          </p>
          <p className={`text-lg font-semibold ${comp.netProfit > 0 ? "text-green" : comp.netProfit < 0 ? "text-red-500" : "text-muted"}`}>
            {comp.netProfit > 0 ? "+" : ""}{formatVolume(Math.abs(comp.netProfit))}
            {comp.netProfit === 0 && <span className="text-xs font-normal ml-1">—</span>}
          </p>
        </div>
        {comp.assets.length > 0 && (
          <div>
            <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
              Markets
            </p>
            <p className="text-lg font-semibold text-dark">
              {comp.assets.length}
            </p>
          </div>
        )}
      </div>

      <hr className="border-border" />

      {/* Top 3 wallets — placeholder until leaderboard API is ready */}
      <div className="space-y-2">
        <p className="text-xs font-bold text-dark">Top 3 wallets</p>
        <div className="rounded-xl border border-border/60 p-3">
          <p className="text-xs text-desc italic">Leaderboard data coming soon</p>
        </div>
      </div>
    </div>
  );
}
