import React from "react";

interface TabToggleProps {
  active: "house" | "players";
  onChange: (tab: "house" | "players") => void;
}

export default function TabToggle({ active, onChange }: TabToggleProps) {
  return (
    <div className="inline-flex items-center rounded-full border border-border bg-white p-[5px]">
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
  );
}
