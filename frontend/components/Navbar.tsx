import React from "react";

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 backdrop-blur-sm bg-[#F7F2EA]/40 border-b border-[#D8D2D8]/50 h-14 flex items-center justify-between px-6">
      {/* Left: Logo + back link */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1 text-lg select-none">
          <span className="text-gold font-semibold tracking-tight">NUNCHI</span>
          <span className="text-dark font-bold tracking-tight">HOUSE</span>
        </div>
        <a
          href="#"
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

      {/* Right: Wallet info */}
      <div className="flex items-center gap-3">
        <div className="flex items-center bg-white rounded-full border border-border px-4 py-1.5 text-xs gap-3">
          <span className="font-medium text-dark">$3.53K</span>
          <span className="w-px h-4 bg-border" />
          <span className="text-muted">0x065D...C827</span>
          <span className="w-2 h-2 rounded-full bg-green" />
        </div>
        <button className="w-8 h-8 flex items-center justify-center rounded-full border border-border bg-white hover:bg-background transition-colors">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" />
          </svg>
        </button>
      </div>
    </nav>
  );
}
