import React from "react";

export interface CompetitionInfo {
  name: string;
  date: string;
  duration: string;
  venue: string;
  players: { wallet: string; pnl: string }[];
}

interface CompetitionCardProps {
  competition: CompetitionInfo;
}

export default function CompetitionCard({ competition }: CompetitionCardProps) {
  return (
    <div className="bg-white border border-border rounded-[7px] p-[25px] flex flex-col gap-4">
      {/* Header: name/date + duration + venue */}
      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-1">
          <p className="text-xs font-bold text-dark uppercase tracking-[0.6px] leading-4">
            {competition.name}
          </p>
          <p className="text-xs text-desc leading-4">{competition.date}</p>
        </div>
        <div className="flex items-center gap-8">
          <div>
            <p className="text-[10px] uppercase tracking-[0.5px] font-medium text-muted leading-[15px]">
              Duration
            </p>
            <p className="text-sm font-semibold text-dark leading-5">
              {competition.duration}
            </p>
          </div>
          <div className="text-right">
            <p className="text-[10px] uppercase tracking-[0.5px] font-medium text-muted leading-[15px]">
              VENUE
            </p>
            <p className="text-sm font-semibold text-dark leading-5">
              {competition.venue}
            </p>
          </div>
        </div>
      </div>

      <hr className="border-border" />

      {/* Top 3 Players */}
      <div className="flex flex-col gap-2">
        <p className="text-xs font-bold text-dark leading-4">Top 3 Players</p>
        <div className="border border-border-60 rounded-xl p-[13px] flex flex-col gap-2">
          {competition.players.map((p, i) => (
            <div key={i} className="flex items-center gap-2">
              <span className="w-5 h-5 flex items-center justify-center rounded-full bg-background border border-border text-[10px] font-bold text-dark shrink-0">
                {i + 1}
              </span>
              <span className="flex-1 text-xs text-desc leading-4 truncate">
                {p.wallet}
              </span>
              <span className="text-xs text-muted leading-4 shrink-0">
                PNL {p.pnl}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
