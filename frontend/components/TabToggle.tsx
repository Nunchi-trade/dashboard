import React from "react";

interface TabToggleProps {
  active: "house" | "players";
  onChange: (tab: "house" | "players") => void;
}

export default function TabToggle({ active, onChange }: TabToggleProps) {
  return (
    <div className="space-y-3">
      <div className="inline-flex items-center rounded-full border border-border bg-white p-1">
        <button
          onClick={() => onChange("house")}
          className={`rounded-full px-7 py-1.5 text-xs font-medium transition-colors ${
            active === "house"
              ? "bg-dark text-white"
              : "bg-transparent text-[#6b6258]"
          }`}
        >
          House
        </button>
        <button
          onClick={() => onChange("players")}
          className={`rounded-full px-7 py-1.5 text-xs font-medium transition-colors ${
            active === "players"
              ? "bg-dark text-white"
              : "bg-transparent text-[#6b6258]"
          }`}
        >
          Players
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="inline-flex items-center rounded-full border border-border/60 bg-white px-3 py-1 text-xs text-desc">
          Current TvL = nLP + PT-wNLP + nHYPE
        </span>
        <span className="inline-flex items-center rounded-full border border-border/60 bg-white px-3 py-1 text-xs text-desc">
          Player feed = all competitions composited together
        </span>
      </div>
    </div>
  );
}
