export interface TvlData {
  wNLP_tvl: number;
  SY_tvl: number;
  nHYPE_tvl: number;
}

export interface PendleMarket {
  name: string;
  implied_apy: number;
  underlying_apy: number;
  tvl_usd: number;
  pt_price: number;
  yt_price: number;
  expiry: string;
  daily_yield: number;
  weekly_yield: number;
  monthly_yield: number;
  annual_yield: number;
}

export interface AlltimeTotals {
  wNLP: {
    deposits: number;
    withdrawals: number;
    volume: number;
    transfers: number;
    transfer_count: number;
    unique_users: number;
  };
  SY_wNLP: {
    deposits: number;
    withdrawals: number;
    volume: number;
    transfers: number;
    transfer_count: number;
    unique_users: number;
  };
  total_unique_users: number;
  timestamp: string;
}

export interface PendleMarketStats {
  market_address: string;
  expiry: string;
  swap_count: number;
  mint_count: number;
  burn_count: number;
  total_events: number;
  unique_users: number;
}

export interface Hip3PairVolume {
  base_volume: number;
  notional_volume: number;
  days: number;
}

export type Hip3Volumes = Record<string, Hip3PairVolume | number> & {
  total_notional: number;
};

export interface SimulatorAsset {
  asset: string;
  volume: number;
  trades_placed: number;
  net_user_profit: number;
  total_users: number;
}

export interface SeasonContract {
  contract: string;
  chain: number;
  chain_name: string;
  asset: string;
  users: number;
  volume: number;
  avg_per_user: number;
  net_profit: number;
  avg_time_to_close: number;
}

export interface SeasonData {
  by_contract?: SeasonContract[];
  by_asset?: Record<string, { volume: number; users: number; net_profit?: number }>;
  by_chain?: Record<string, { name: string; users: number; volume: number; avg_per_user: number }>;
  total?: {
    total_volume: number;
    total_users: number;
    avg_per_user: number;
    net_profit: number;
    avg_time_to_close_hours: number;
    avg_time_to_close_formatted: string;
  };
}

export interface TestnetData {
  simulator: {
    total_users: number;
    total_volume: number;
    avg_volume_per_user: number;
    by_asset?: SimulatorAsset[];
    total_trades_placed?: number;
    total_net_profit?: number;
  };
  season_one: SeasonData;
  season_two: SeasonData;
  totals: {
    total_volume: number;
    total_users: number;
  };
  timestamp: string;
}

export type YexVolumes = Record<string, Hip3PairVolume | number> & {
  total_notional: number;
};

export interface DashboardData {
  tvl: TvlData;
  apy: Record<string, PendleMarket>;
  alltime_totals: AlltimeTotals;
  alltime_pendle: Record<string, PendleMarketStats | string>;
  hip3_volumes: Hip3Volumes;
  testnet: TestnetData;
  yex_volumes: YexVolumes;
}

export interface CompetitionInfo {
  num: string;
  name: string;
  date: string;
  venue: string;
  leaderboard: string;
  duration: string;
  volume: number;
  netProfit: number;
  tradesPlaced: number;
  assets: string[];
}

export interface DerivedMetrics {
  nlpTvl: number;
  pendleTvl: number;
  nhypeTvl: number;
  totalTvl: number;
  nlpUsers: number;
  pendleUsers: number;
  totalLpWallets: number;
  totalVolume: number;
  totalWallets: number;
  totalMarkets: number;
  yexTotal: number;
  totalTradesPlaced: number;
  totalNetProfit: number;
  assetList: string[];
  competitions: CompetitionInfo[];
}
