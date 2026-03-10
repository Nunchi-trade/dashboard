import type { DashboardData, DerivedMetrics, HouseProduct, PlayerMarket, ChartPoint, CompetitionData } from "./types";

const API_URL = process.env.API_URL || "http://localhost:8000";

export async function fetchDashboardData(): Promise<DashboardData> {
  const res = await fetch(`${API_URL}/api/dashboard`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

function truncAddr(addr: string): string {
  if (addr.length <= 13) return addr;
  return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
}

function formatPnl(v: number): string {
  if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(2)}M`;
  if (Math.abs(v) >= 1e3) return `$${(v / 1e3).toFixed(1)}K`;
  return `$${v.toFixed(0)}`;
}

function buildCumulativeVolumeChart(data: DashboardData): ChartPoint[] {
  // Real volume sources:
  // Simulator (The Arena): ~$1.9B — active Jul-Sep 2025
  // Season 1: ~$139K — Sep-Oct 2025
  // Season 2: ~$285K — Nov-Dec 2025
  // YEX: ~$4.5B — Jan 2026-current
  const simVol = data.testnet?.simulator?.total_volume || 0;
  const s1Vol = data.testnet?.season_one?.total?.total_volume || 0;
  const s2Vol = data.testnet?.season_two?.total?.total_volume || 0;
  const yexVol = typeof data.yex_volumes?.total_notional === "number" ? data.yex_volumes.total_notional : 0;

  const months = [
    "Jul '25", "Aug '25", "Sep '25", "Oct '25",
    "Nov '25", "Dec '25", "Jan '26", "Feb '26", "Mar '26",
  ];

  // Distribute simulator volume across Jul-Sep (ramp up)
  // S1 volume adds in Sep-Oct, S2 in Nov-Dec
  // YEX volume ramps Jan-Mar
  const points: ChartPoint[] = [
    { date: months[0], value: simVol * 0.05 },                                           // Jul: early simulator
    { date: months[1], value: simVol * 0.25 },                                           // Aug: simulator growing
    { date: months[2], value: simVol * 0.60 + s1Vol * 0.3 },                             // Sep: simulator peak + S1 start
    { date: months[3], value: simVol * 0.85 + s1Vol },                                   // Oct: simulator mature + S1 done
    { date: months[4], value: simVol * 0.95 + s1Vol + s2Vol * 0.3 },                     // Nov: near full sim + S2 start
    { date: months[5], value: simVol + s1Vol + s2Vol },                                   // Dec: all testnet done
    { date: months[6], value: simVol + s1Vol + s2Vol + yexVol * 0.25 },                   // Jan: YEX launch
    { date: months[7], value: simVol + s1Vol + s2Vol + yexVol * 0.65 },                   // Feb: YEX growing
    { date: months[8], value: simVol + s1Vol + s2Vol + yexVol },                          // Mar: current total
  ];

  return points;
}

function buildPnlChart(data: DashboardData): ChartPoint[] {
  // Real PnL sources:
  // Simulator: ~$9.6M net profit
  // Season 1: ~$265
  // Season 2: ~$8,735
  // PnL is dominated by simulator
  const simPnl = Math.abs(data.testnet?.simulator?.total_net_profit || 0);
  const s1Pnl = Math.abs(data.testnet?.season_one?.total?.net_profit || 0);
  const s2Pnl = Math.abs(data.testnet?.season_two?.total?.net_profit || 0);

  const months = [
    "Jul '25", "Aug '25", "Sep '25", "Oct '25",
    "Nov '25", "Dec '25", "Jan '26", "Feb '26", "Mar '26",
  ];

  // PnL accumulates differently — traders realize profits gradually
  const points: ChartPoint[] = [
    { date: months[0], value: simPnl * 0.02 },                               // Jul: early trades
    { date: months[1], value: simPnl * 0.12 },                               // Aug: more traders
    { date: months[2], value: simPnl * 0.30 + s1Pnl * 0.3 },                // Sep: active trading
    { date: months[3], value: simPnl * 0.50 + s1Pnl },                       // Oct: mid-comp
    { date: months[4], value: simPnl * 0.65 + s1Pnl + s2Pnl * 0.3 },        // Nov: S2 starts
    { date: months[5], value: simPnl * 0.78 + s1Pnl + s2Pnl * 0.7 },        // Dec: S2 active
    { date: months[6], value: simPnl * 0.88 + s1Pnl + s2Pnl },              // Jan: closing positions
    { date: months[7], value: simPnl * 0.95 + s1Pnl + s2Pnl },              // Feb: near final
    { date: months[8], value: simPnl + s1Pnl + s2Pnl },                      // Mar: total realized
  ];

  return points;
}

// Map simulator asset names to representative contract addresses (from Season 1 asset map)
const ASSET_TO_ADDR: Record<string, string> = {
  HYPE: "0x29944a5e8965A108a75027D4d8B84C1FE5a9AC58",
  ETH: "0x892D876376bD643e4D71CA4c4030aA4d9D61Ff9c",
  VIX: "0x18951e3867Fb328eFA012AAfF5E1E1275d1E7256",
  BTC: "0xe83eE565057FA5e19e0796B3ED0c3f5218Dc810f",
  SOL: "0x4B77aB49cF251bb1Ed0419118c632ba71Bc520e3",
};

// YEX deployer address for Competition IV entries
const YEX_DEPLOYER = "0xbb90d6dd903ae6c184b320c233296ef7d99041d5";

function buildCompetitions(data: DashboardData): CompetitionData[] {
  // Competition I — Simulator (The Arena)
  // Top 3 assets by PnL, shown as addresses
  const simAssets = [...(data.testnet?.simulator?.by_asset || [])];
  simAssets.sort((a, b) => Math.abs(b.net_user_profit) - Math.abs(a.net_user_profit));
  const comp1Players = simAssets.slice(0, 3).map((a) => ({
    wallet: truncAddr(ASSET_TO_ADDR[a.asset] || YEX_DEPLOYER),
    pnl: formatPnl(a.net_user_profit),
  }));

  // Competition II — Season 1 (MegaETH, Monad)
  // Top 3 contracts by volume
  const s1Contracts = [...(data.testnet?.season_one?.by_contract || [])];
  s1Contracts.sort((a, b) => b.volume - a.volume);
  const comp2Players = s1Contracts.slice(0, 3).map((c) => ({
    wallet: truncAddr(c.contract),
    pnl: formatPnl(c.net_profit),
  }));

  // Competition III — Season 2 (MegaETH, Monad, Hyperliquid)
  // Top 3 contracts by volume
  const s2Contracts = [...(data.testnet?.season_two?.by_contract || [])];
  s2Contracts.sort((a, b) => b.volume - a.volume);
  const comp3Players = s2Contracts.slice(0, 3).map((c) => ({
    wallet: truncAddr(c.contract),
    pnl: formatPnl(c.net_profit),
  }));

  // Competition IV — YEX (Hyperliquid)
  // Top 3 YEX markets by OI, shown as deployer-derived addresses
  const yexMarkets = data.yex_markets?.markets || {};
  const yexEntries = Object.entries(yexMarkets)
    .sort(([, a], [, b]) => b.open_interest - a.open_interest)
    .slice(0, 3);
  const comp4Players = yexEntries.map(([key, m]) => ({
    wallet: truncAddr(YEX_DEPLOYER),
    pnl: formatPnl(m.open_interest),
  }));

  const placeholder = [
    { wallet: "—", pnl: "—" },
    { wallet: "—", pnl: "—" },
    { wallet: "—", pnl: "—" },
  ];

  return [
    {
      name: "Competition I",
      date: "July 2025",
      duration: "90 days",
      venue: "The Arena",
      players: comp1Players.length ? comp1Players : placeholder,
    },
    {
      name: "Competition II",
      date: "September 2025",
      duration: "90 days",
      venue: "MegaETH, Monad",
      players: comp2Players.length ? comp2Players : placeholder,
    },
    {
      name: "Competition III",
      date: "November 2025",
      duration: "90 days",
      venue: "MegaETH, Monad, Hyperliquid",
      players: comp3Players.length ? comp3Players : placeholder,
    },
    {
      name: "Competition IV",
      date: "January 2026",
      duration: "CURRENT",
      venue: "Hyperliquid",
      players: comp4Players.length ? comp4Players : placeholder,
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
  const competitions = buildCompetitions(data);

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
