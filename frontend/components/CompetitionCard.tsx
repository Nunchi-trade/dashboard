import React from "react";
import { CompetitionInfo } from "@/lib/types";

interface CompetitionCardProps {
  comp: CompetitionInfo;
}

export default function CompetitionCard({ comp }: CompetitionCardProps) {
  const wallets = [
    { rank: 1, address: "[wallet #1]", pnl: "[value]" },
    { rank: 2, address: "[wallet #2]", pnl: "[value]" },
    { rank: 3, address: "[wallet #3]", pnl: "[value]" },
  ];

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

      <hr className="border-border" />

      {/* Top 3 wallets */}
      <div className="space-y-2">
        <p className="text-xs font-bold text-dark">Top 3 wallets</p>
        <div className="rounded-xl border border-border/60 p-3 space-y-2">
          {wallets.map((w) => (
            <div
              key={w.rank}
              className="flex items-center gap-2 text-xs text-desc"
            >
              {w.rank === 1 && (
                <span className="w-5 h-5 rounded-full bg-background border border-border flex items-center justify-center text-[10px] font-bold text-dark">
                  {w.rank}
                </span>
              )}
              <span className="flex-1 truncate">
                {w.rank > 1 && <span className="ml-7" />}
                {w.address}
              </span>
              <span className="text-muted">PNL {w.pnl}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
