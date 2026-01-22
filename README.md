# Nunchi Analytics Dashboard

Real-time analytics dashboard for [Nunchi](https://nunchi.trade) on HyperEVM. Tracks nLP, nHYPE, and Pendle integrations with data from Hyperscan API.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)
![HyperEVM](https://img.shields.io/badge/HyperEVM-Chain%20999-blue?style=for-the-badge)

## Features

- **Current TVL** - Live nLP, nHYPE, Pendle SY, and Pendle market TVL
- **Volume Traded** - All-time HIP-3 volume on Hyperliquid testnet (VXX, US3M)
- **All-Time Totals** - Cumulative deposits, withdrawals, volume, and transfers
- **APY & Distributed Yield** - Live APY data and yield calculations from Pendle
- **Pendle Pools Breakdown** - Stats for both Dec 2025 (expired) and Jun 2026 (active) pools

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Nunchi-trade/dashboard.git
cd dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

Or use the convenience script:

```bash
./run.sh
```

Then open **http://localhost:8501** in your browser.

## No API Keys Required!

This dashboard queries data from:
- **Hyperscan API** - For all-time on-chain data (indexed, fast)
- **HyperEVM RPC** - For live TVL via totalSupply()
- **Pendle API** - For APY and yield data
- **Hyperliquid Testnet API** - For HIP-3 trading volume

## Project Structure

```
dashboard/
├── app.py              # Main Streamlit dashboard
├── data_fetcher.py     # Data fetching logic (Hyperscan, RPC, Pendle, Hyperliquid)
├── config.py           # Contract addresses & settings
├── alltime_cache.json  # Cached all-time data (speeds up loading)
├── requirements.txt    # Python dependencies
├── run.sh              # Convenience runner script
├── .streamlit/         # Streamlit configuration
└── README.md
```

## Contract Addresses (HyperEVM)

| Contract | Address |
|----------|---------|
| wNLP Token | `0x4Cc221cf1444333510a634CE0D8209D2D11B9bbA` |
| nHYPE Token | `0x88888884cdc539d00dfb9C9e2Af81baA65fDA356` |
| SY-wNLP | `0x9b7430dB2C59247E861702B5C85131eEaf03aED3` |
| Pendle Market (Dec 2025) | `0x07a50aEc9B49cD605e66B0cA7e39d781E6Ae0b79` |
| Pendle Market (Jun 2026) | `0xc1ef65d86f82d5a8160b577a150f65d52d6b266f` |

## Dashboard Sections

### 1. Current TVL
- nLP TVL (stablecoin vault)
- nHYPE TVL (HYPE vault)
- Pendle SY TVL
- Pendle TVL (USD)

### 2. Volume Traded
- VXX Volume (Hyperliquid HIP-3)
- US3M Volume (Hyperliquid HIP-3)
- Total Volume

### 3. All-Time Totals
- Total unique users, nLP users, Pendle users
- nLP deposits, withdrawals, volume, transfers
- Pendle deposits, withdrawals, volume, transfers

### 4. APY & Distributed Yield
- Underlying APY (TVL-weighted average)
- Implied APY (PT discount rate)
- Daily and annual yield calculations
- APY history chart

### 5. Pendle Pools Breakdown
- Dec 2025 pool (expired) - All-time peak TVL and stats
- Jun 2026 pool (active) - Current TVL and stats

## Configuration

Edit `config.py` to customize:

```python
# Cache settings
CACHE_TTL = 300  # 5 minutes

# Default time range
DEFAULT_DAYS = 1

# RPC endpoint
RPC_URL = "https://hyperliquid.drpc.org"
```

## Data Caching

The dashboard includes `alltime_cache.json` which contains pre-fetched all-time data. This allows the dashboard to load instantly. The cache is refreshed when you click "Refresh Data" in the sidebar.

If the cache is missing, the first load will fetch all data from Hyperscan (~2-3 minutes).

## Deployment Options

### Streamlit Cloud (Free)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo
4. Deploy!

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

### Railway/Render/Fly.io
Just push to GitHub and connect - all support Python apps.

## Troubleshooting

**"No data found"**
- Check if Hyperscan API is accessible
- Try refreshing the data from the sidebar

**Slow loading**
- First load without cache fetches all data (~2-3 min)
- Subsequent loads use cached data (instant)

**Volume shows $0**
- Hyperliquid testnet API may be temporarily unavailable
- HIP-3 pairs may have no recent activity

## Resources

- [Nunchi App](https://nunchi.trade)
- [Nunchi Docs](https://docs.nunchi.trade)
- [HyperEVM Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperevm)
- [Pendle Docs](https://docs.pendle.finance)
- [Hyperscan](https://hyperscan.com)

## License

MIT
