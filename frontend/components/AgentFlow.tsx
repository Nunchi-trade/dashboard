import React from "react";

const metrics = [
  {
    label: "Active Agents",
    value: "0",
    desc: "currently in the composite feed",
  },
  {
    label: "Agent Volume",
    value: "$0",
    desc: "all competitions combined",
  },
  {
    label: "Agent Markets",
    value: "0",
    desc: "unique markets touched",
  },
  {
    label: "Filled Value (USDYP)",
    value: "$0",
    desc: "orders filled across agents",
  },
];

export default function AgentFlow() {
  return (
    <div className="rounded-2xl border border-border bg-white p-6 space-y-4">
      <div className="space-y-1">
        <p className="text-xs uppercase tracking-wider font-semibold text-dark">
          Agent Flow
        </p>
        <h2 className="text-sm font-normal text-dark">
          Agent Trades
        </h2>
        <p className="text-xs text-desc leading-relaxed">
          Number of agents active, volumes, markets, and orders filled value (USDYP).
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        {metrics.map((m) => (
          <div
            key={m.label}
            className="rounded-xl border border-[#D8D2D8]/60 p-4 space-y-1"
          >
            <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
              {m.label}
            </p>
            <p className="text-xl font-semibold text-dark">{m.value}</p>
            <p className="text-[10px] text-desc">{m.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
