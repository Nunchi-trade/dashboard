import React from "react";

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 backdrop-blur-sm bg-[#F7F2EA]/40 border-b border-[#D8D2D8]/50 h-14 flex items-center px-6">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1 text-lg select-none">
          <span className="text-gold font-semibold tracking-tight">NUNCHI</span>
          <span className="text-dark font-bold tracking-tight">HOUSE</span>
        </div>
        <a
          href="https://yex.nunchi.trade"
          className="flex items-center gap-1.5 bg-[rgba(244,178,44,0.08)] border border-[rgba(244,178,44,0.32)] rounded-xl px-3 py-2 text-xs text-dark hover:opacity-80 transition-opacity"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Back to Perps Trading
        </a>
        <a href="#" className="flex items-center gap-1 text-xs text-desc hover:underline">
          How to earn cHIPs
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-60">
            <path d="M7 17L17 7M17 7H7M17 7v10" />
          </svg>
        </a>
      </div>
    </nav>
  );
}
