import type { DashboardData, DerivedMetrics, HouseProduct, PlayerMarket } from "./types";

const API_URL = process.env.API_URL || "http://localhost:8000";

export async function fetchDashboardData(): Promise<DashboardData> {
  const res = await fetch(`${API_URL}/api/dashboard`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export function deriveMetrics(data: DashboardData): DerivedMetrics {
  // === HOUSE ===
  const nlpTvl = data.tvl?.wNLP_tvl || 0;
  const syTvl = data.tvl?.SY_tvl || 0;
  const nhypeTvl = data.tvl?.nHYPE_tvl || 0;

  // Pendle TVL from APY data
  let pendleTvl = 0;
  if (data.apy) {
    for (const v of Object.values(data.apy)) {
      if (v && typeof v === "object" && "tvl_usd" in v) {
        pendleTvl += v.tvl_usd || 0;
      }
    }
  }

  const totalHouseCapital = nlpTvl + pendleTvl + nhypeTvl;

  // LP wallets (House members)
  const nlpUsers = data.alltime_totals?.wNLP?.unique_users || 0;
  let pendleUsers = 0;
  if (data.alltime_pendle) {
    for (const [k, v] of Object.entries(data.alltime_pendle)) {
      if (k !== "timestamp" && typeof v === "object" && "unique_users" in v) {
        pendleUsers += v.unique_users;
      }
    }
  }
  const totalMembers = nlpUsers + pendleUsers;

  // APY — use Pendle implied APY as representative, fallback to 0
  let houseApy = 0;
  if (data.apy) {
    const apyValues = Object.values(data.apy);
    if (apyValues.length > 0) {
      const first = apyValues[0];
      if (first && typeof first === "object" && "implied_apy" in first) {
        houseApy = first.implied_apy * 100;
      }
    }
  }

  const houseProducts: HouseProduct[] = [
    { name: "NunchiLiquidity Provider (nLP)", tvl: nlpTvl, apy: houseApy },
    { name: "Pendle Yield Tokenization (LP / YT-wNLP)", tvl: pendleTvl || syTvl, apy: houseApy },
    { name: "Native Staking (nHYPE)", tvl: nhypeTvl, apy: 0 },
  ];

  // === PLAYERS ===
  const testnetTotals = data.testnet?.totals || { total_volume: 0, total_users: 0 };
  const yexTotal =
    typeof data.yex_volumes?.total_notional === "number"
      ? data.yex_volumes.total_notional
      : 0;
  const cumulativeVolume = testnetTotals.total_volume + yexTotal;
  const totalPlayers = testnetTotals.total_users;

  // 24hr volume from live YEX market data
  const dayVolume = data.yex_markets?.total_24h_volume || 0;

  // Market rows from live YEX data
  const marketOrder = ["yex:BTCSWP", "yex:VXX", "yex:US3M"];
  const playerMarkets: PlayerMarket[] = marketOrder.map((coin) => {
    const m = data.yex_markets?.markets?.[coin];
    return {
      name: m?.name || coin,
      adv: m?.adv || 0,
      oi: m?.open_interest || 0,
    };
  });

  return {
    totalMembers,
    totalHouseCapital,
    houseApy,
    houseProducts,
    totalPlayers,
    cumulativeVolume,
    dayVolume,
    playerMarkets,
  };
}
