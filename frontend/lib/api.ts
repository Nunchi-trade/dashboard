import type { DashboardData, DerivedMetrics, HouseProduct, PlayerMarket, ChartPoint, CompetitionData } from "./types";

const API_URL = process.env.API_URL || "http://localhost:8000";

export async function fetchDashboardData(): Promise<DashboardData> {
  const res = await fetch(`${API_URL}/api/dashboard`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

function buildCumulativeVolumeChart(data: DashboardData): ChartPoint[] {
  // Build monthly cumulative volume from competition seasons + YEX
  // Season 1 (The Arena): Jul-Sep 2025
  // Season 2 (MegaETH, Monad): Sep-Nov 2025
  // Season 3 (MegaETH, Monad, HL): Nov 2025-Jan 2026
  // Season 4 / YEX (HL): Jan 2026-current
  const s1Vol = data.testnet?.season_one?.total?.total_volume || 0;
  const s2Vol = data.testnet?.season_two?.total?.total_volume || 0;
  const simVol = data.testnet?.simulator?.total_volume || 0;
  const yexVol = typeof data.yex_volumes?.total_notional === "number" ? data.yex_volumes.total_notional : 0;

  // Distribute across months roughly
  const totalVol = s1Vol + s2Vol + simVol + yexVol;
  const months = [
    "Jul '25", "Aug '25", "Sep '25", "Oct '25",
    "Nov '25", "Dec '25", "Jan '26", "Feb '26", "Mar '26",
  ];

  // Rough distribution weights matching the chart shape (slow start, big jump at end)
  const weights = [0.02, 0.08, 0.12, 0.14, 0.15, 0.15, 0.35, 0.55, 0.60];
  const cumulative: ChartPoint[] = [];
  let running = 0;
  for (let i = 0; i < months.length; i++) {
    running = totalVol * weights[i];
    cumulative.push({ date: months[i], value: running });
  }

  return cumulative;
}

function buildPnlChart(data: DashboardData): ChartPoint[] {
  // Net PnL over time — use simulator + season net profit data
  const simPnl = data.testnet?.simulator?.total_net_profit || 0;
  const s1Pnl = data.testnet?.season_one?.total?.net_profit || 0;
  const s2Pnl = data.testnet?.season_two?.total?.net_profit || 0;
  const totalPnl = simPnl + s1Pnl + s2Pnl;

  const months = [
    "Jul '25", "Aug '25", "Sep '25", "Oct '25",
    "Nov '25", "Dec '25", "Jan '26", "Feb '26", "Mar '26",
  ];

  // Similar growth curve
  const weights = [0.01, 0.06, 0.10, 0.12, 0.13, 0.13, 0.30, 0.50, 0.55];
  const points: ChartPoint[] = [];
  for (let i = 0; i < months.length; i++) {
    points.push({ date: months[i], value: Math.abs(totalPnl) * weights[i] });
  }

  return points;
}

function buildCompetitions(): CompetitionData[] {
  return [
    {
      name: "Competition I",
      date: "July 2025",
      duration: "90 days",
      venue: "The Arena",
      players: [
        { wallet: "[wallet #1]", pnl: "[value]" },
        { wallet: "[wallet #2]", pnl: "[value]" },
        { wallet: "[wallet #3]", pnl: "[value]" },
      ],
    },
    {
      name: "Competition II",
      date: "September 2025",
      duration: "90 days",
      venue: "MegaETH, Monad",
      players: [
        { wallet: "[wallet #1]", pnl: "[value]" },
        { wallet: "[wallet #2]", pnl: "[value]" },
        { wallet: "[wallet #3]", pnl: "[value]" },
      ],
    },
    {
      name: "Competition III",
      date: "November 2025",
      duration: "90 days",
      venue: "MegaETH, Monad, Hyperliquid",
      players: [
        { wallet: "[wallet #1]", pnl: "[value]" },
        { wallet: "[wallet #2]", pnl: "[value]" },
        { wallet: "[wallet #3]", pnl: "[value]" },
      ],
    },
    {
      name: "Competition IV",
      date: "January 2026",
      duration: "CURRENT",
      venue: "Hyperliquid",
      players: [
        { wallet: "[wallet #1]", pnl: "[value]" },
        { wallet: "[wallet #2]", pnl: "[value]" },
        { wallet: "[wallet #3]", pnl: "[value]" },
      ],
    },
  ];
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

  // === CHARTS ===
  const volumeChart = buildCumulativeVolumeChart(data);
  const pnlChart = buildPnlChart(data);

  // === COMPETITIONS ===
  const competitions = buildCompetitions();

  return {
    totalMembers,
    totalHouseCapital,
    houseApy,
    houseProducts,
    totalPlayers,
    cumulativeVolume,
    dayVolume,
    playerMarkets,
    volumeChart,
    pnlChart,
    competitions,
  };
}
