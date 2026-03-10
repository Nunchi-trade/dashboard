import React from "react";
import type { HouseProduct } from "@/lib/types";

interface HousePanelProps {
  totalMembers: number;
  totalCapital: number;
  apy: number;
  products: HouseProduct[];
}

function formatM(value: number): string {
  if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

export default function HousePanel({ totalMembers, totalCapital, apy, products }: HousePanelProps) {
  return (
    <div className="bg-white border border-[#bfd4ea] rounded-[7px] p-[25px] flex flex-col gap-5">
      {/* Badge + description */}
      <div className="flex flex-col gap-1">
        <div className="inline-flex">
          <span className="text-xs font-bold text-[#1b1a17] bg-[#bfd4ea]/20 border border-[#bfd4ea] rounded-full px-3 py-0.5">
            HOUSE
          </span>
        </div>
        <p className="text-sm text-dark leading-5">
          Capital powering Nunchi&apos;s managed liquidity layer.
        </p>
      </div>

      {/* Stats row */}
      <div className="flex items-center gap-8">
        <div>
          <p className="text-[10px] uppercase tracking-[0.5px] font-medium text-muted leading-[15px]">
            Total Members
          </p>
          <p className="text-2xl font-semibold text-dark leading-8">
            {totalMembers.toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-[0.5px] font-medium text-muted leading-[15px]">
            Total House Capital
          </p>
          <p className="text-2xl font-semibold text-dark leading-8">
            {formatM(totalCapital)}
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-[0.5px] font-medium text-muted leading-[15px]">
            APY
          </p>
          <p className="text-2xl font-semibold text-dark leading-8">
            {apy > 0 ? `${apy.toFixed(2)}%` : "—"}
          </p>
        </div>
      </div>

      <hr className="border-border" />

      {/* Product rows */}
      <div className="flex flex-col gap-4">
        {products.map((p) => (
          <div key={p.name} className="flex items-center justify-between">
            <span className="text-xs font-bold text-dark w-[200px]">
              {p.name}
            </span>
            <div className="flex items-start gap-8 w-[140px]">
              <span className="text-xs text-dark flex-1">
                {formatM(p.tvl)}
              </span>
              <span className="text-xs text-dark flex-1">
                {p.apy > 0 ? `${p.apy.toFixed(2)}% APY` : "—"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
