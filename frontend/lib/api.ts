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

  // Simulator data
  const simulator = data.testnet?.simulator || {
    total_users: 0,
    total_volume: 0,
  };
  const simByAsset = data.testnet?.simulator?.by_asset || [];
  const simTradesPlaced = data.testnet?.simulator?.total_trades_placed || 0;
  const simNetProfit = data.testnet?.simulator?.total_net_profit || 0;
  const simAssets = simByAsset.map((a) => a.asset);

  // Season data
  const s1 = data.testnet?.season_one || {};
  const s2 = data.testnet?.season_two || {};
  const s1NetProfit = s1.total?.net_profit || 0;
  const s2NetProfit = s2.total?.net_profit || 0;
  const s1Assets = Object.keys(s1.by_asset || {});
  const s2Assets = Object.keys(s2.by_asset || {});

  // All unique assets across all competitions
  const allAssets = new Set([
    ...simAssets,
    ...s1Assets,
    ...s2Assets,
    "US3M",
    "VXX",
    "BTCSWP",
  ]);
  const assetList = Array.from(allAssets).sort();
  const totalMarkets = allAssets.size;

  // Total trades placed across all competitions
  // Seasons don't have trades_placed in the API, so we use contract counts as proxy
  const s1Contracts = s1.by_contract?.length || 0;
  const s2Contracts = s2.by_contract?.length || 0;
  const totalTradesPlaced = simTradesPlaced;

  // Total net profit across all competitions
  const totalNetProfit = simNetProfit + s1NetProfit + s2NetProfit;

  // Competition data
  const competitions: CompetitionInfo[] = [
    {
      num: "I",
      name: "COMPETITION I",
      date: "July 2025 - Simulator",
      venue: "THE ARENA",
      leaderboard: "The Arena",
      duration: `${simulator.total_users} users`,
      volume: simulator.total_volume,
      netProfit: simNetProfit,
      tradesPlaced: simTradesPlaced,
      assets: simAssets,
    },
    {
      num: "II",
      name: "COMPETITION II",
      date: "September 2025 - Season 1",
      venue: "MEGAETH + MONAD",
      leaderboard: "MegaETH, Monad",
      duration: `${s1.total?.total_users || 0} users`,
      volume: s1.total?.total_volume || 0,
      netProfit: s1NetProfit,
      tradesPlaced: s1Contracts,
      assets: s1Assets,
    },
    {
      num: "III",
      name: "COMPETITION III",
      date: "November 2025 - Season 2",
      venue: "MEGAETH + MONAD + HYPERLIQUID",
      leaderboard: "MegaETH, Monad, Hyperliquid",
      duration: `${s2.total?.total_users || 0} users`,
      volume: s2.total?.total_volume || 0,
      netProfit: s2NetProfit,
      tradesPlaced: s2Contracts,
      assets: s2Assets,
    },
    {
      num: "IV",
      name: "COMPETITION IV",
      date: "January 2026 - Hyperliquid Testnet",
      venue: "HYPERLIQUID",
      leaderboard: "Hyperliquid",
      duration: "YEX DEX",
      volume: yexTotal,
      netProfit: 0,
      tradesPlaced: 0,
      assets: ["US3M", "VXX", "BTCSWP"],
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
    totalTradesPlaced,
    totalNetProfit,
    assetList,
    competitions,
  };
}
