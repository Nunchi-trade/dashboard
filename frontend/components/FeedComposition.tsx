import React from "react";

interface FeedCompositionProps {
  totalMarkets: number;
  assetList: string[];
}

const venues = ["The Arena", "MegaETH", "Monad", "Hyperliquid"];
const comps = ["Comp I", "Comp II", "Comp III", "Comp IV"];

export default function FeedComposition({ totalMarkets, assetList }: FeedCompositionProps) {
  return (
    <div className="rounded-2xl border border-border bg-white p-6 space-y-5">
      <div className="space-y-1">
        <p className="text-xs uppercase tracking-wider font-semibold text-dark">
          Feed Composition
        </p>
        <h2 className="text-sm font-normal text-dark">
          Markets, venues, and seasons
        </h2>
        <p className="text-xs text-desc leading-relaxed">
          Competition coverage contributing to the composite player feed.
        </p>
      </div>

      <div className="space-y-1">
        <p className="text-[10px] uppercase tracking-wider text-muted font-medium">
          Number of Markets Traded
        </p>
        <p className="text-2xl font-semibold text-dark">
          {totalMarkets.toLocaleString()}
        </p>
      </div>

      <div className="space-y-2">
        <p className="text-xs font-semibold text-dark">Assets</p>
        <div className="flex flex-wrap gap-1.5">
          {assetList.map((a) => (
            <span
              key={a}
              className="rounded-full border border-border bg-background px-2.5 py-0.5 text-[10px] text-muted font-medium"
            >
              {a}
            </span>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-xs font-semibold text-dark">Venue coverage</p>
        <ul className="space-y-1">
          {venues.map((v) => (
            <li key={v} className="flex items-center gap-2 text-xs text-desc">
              <span className="w-1 h-1 rounded-full bg-muted" />
              {v}
            </li>
          ))}
        </ul>
      </div>

      <div className="flex flex-wrap gap-2">
        {comps.map((c) => (
          <span
            key={c}
            className="rounded-full border border-border px-3 py-1 text-xs text-muted font-medium"
          >
            {c}
          </span>
        ))}
      </div>
    </div>
  );
}
