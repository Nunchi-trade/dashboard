import type { DashboardData, DerivedMetrics, CompetitionInfo } from "./types";

const API_URL = process.env.API_URL || "http://localhost:8000";

export async function fetchDashboardData(): Promise<DashboardData> {
  const res = await fetch(`${API_URL}/api/dashboard`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export function deriveMetrics(data: DashboardData): DerivedMetrics {
  const nlpTvl = data.tvl.wNLP_tvl;
  const pendleTvl = Object.values(data.apy).reduce(
    (sum, m) => sum + (m.tvl_usd || 0),
    0
  );
  const nhypeTvl = data.tvl.nHYPE_tvl;
  const totalTvl = nlpTvl + pendleTvl;

  // LP wallets
  const nlpUsers = data.alltime_totals?.wNLP?.unique_users || 0;
  let pendleUsers = 0;
  if (data.alltime_pendle) {
    for (const [k, v] of Object.entries(data.alltime_pendle)) {
      if (k !== "timestamp" && typeof v === "object" && "unique_users" in v) {
        pendleUsers += v.unique_users;
      }
    }
  }
  const totalLpWallets = nlpUsers + pendleUsers;

  // Player totals
  const totals = data.testnet?.totals || { total_volume: 0, total_users: 0 };
  const yexTotal =
    typeof data.yex_volumes?.total_notional === "number"
      ? data.yex_volumes.total_notional
      : 0;
  const totalVolume = totals.total_volume + yexTotal;
  const totalWallets = totals.total_users;

  // Markets traded
  let totalMarkets = 0;
  if (data.testnet) {
    const s1Assets = data.testnet.season_one?.by_asset || {};
    const s2Assets = data.testnet.season_two?.by_asset || {};
    const allAssets = new Set([
      ...Object.keys(s1Assets),
      ...Object.keys(s2Assets),
      "US3M",
      "VXX",
      "BTCSWP",
    ]);
    totalMarkets = allAssets.size;
  }

  // Competition data
  const simulator = data.testnet?.simulator || {
    total_users: 0,
    total_volume: 0,
  };
  const s1 = data.testnet?.season_one || {};
  const s2 = data.testnet?.season_two || {};

  const competitions: CompetitionInfo[] = [
    {
      num: "I",
      name: "COMPETITION I",
      date: "July 2025 - Simulator",
      venue: "THE ARENA",
      leaderboard: "The Arena",
      duration: `${simulator.total_users} users`,
      volume: simulator.total_volume,
    },
    {
      num: "II",
      name: "COMPETITION II",
      date: "September 2025 - Season 1",
      venue: "MEGAETH + MONAD",
      leaderboard: "MegaETH, Monad",
      duration: `${s1.total?.total_users || 0} users`,
      volume: s1.total?.total_volume || 0,
    },
    {
      num: "III",
      name: "COMPETITION III",
      date: "November 2025 - Season 2",
      venue: "MEGAETH + MONAD + HYPERLIQUID",
      leaderboard: "MegaETH, Monad, Hyperliquid",
      duration: `${s2.total?.total_users || 0} users`,
      volume: s2.total?.total_volume || 0,
    },
    {
      num: "IV",
      name: "COMPETITION IV",
      date: "January 2026 - Hyperliquid Testnet",
      venue: "HYPERLIQUID",
      leaderboard: "Hyperliquid",
      duration: "YEX DEX",
      volume: yexTotal,
    },
  ];

  return {
    nlpTvl,
    pendleTvl,
    nhypeTvl,
    totalTvl,
    nlpUsers,
    pendleUsers,
    totalLpWallets,
    totalVolume,
    totalWallets,
    totalMarkets,
    yexTotal,
    competitions,
  };
}
