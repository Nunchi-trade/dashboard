import React from "react";
import { CompetitionInfo } from "@/lib/types";
import CompetitionCard from "./CompetitionCard";

interface CompetitionSectionProps {
  competitions: CompetitionInfo[];
}

export default function CompetitionSection({
  competitions,
}: CompetitionSectionProps) {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <p className="text-xs uppercase tracking-wider font-semibold text-dark">
          Competitions
        </p>
        <h2 className="text-[38px] font-normal text-dark font-serif leading-tight">
          Competition history
        </h2>
        <p className="text-xs text-desc leading-relaxed max-w-3xl">
          Each competition card shows period, format, number of days, venues, and top 3 wallet results. Replace placeholders with live values.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {competitions.map((comp) => (
          <CompetitionCard key={comp.num} comp={comp} />
        ))}
      </div>
    </div>
  );
}
