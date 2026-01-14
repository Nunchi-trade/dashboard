# Nunchi Analytics Dashboard

Real-time analytics dashboard for [Nunchi](https://nunchi.trade) on HyperEVM. No external APIs required - queries the blockchain directly.

![Dashboard Preview](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)
![HyperEVM](https://img.shields.io/badge/HyperEVM-Chain%20999-blue?style=for-the-badge)

## Features

- **Pendle Deposits & Withdrawals** - Track SY-wNLP mints/burns
- **Pendle Volume** - Daily swap volume and fees
- **nLP TVL** - Total value locked over time
- **nLP Volume** - Token transfer activity
- **Top Holders** - Current wNLP distribution
- **User Analytics** - Daily/cumulative unique users

## Quick Start

```bash
# 1. Navigate to the dashboard folder
cd nunchi_dashboard

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

This dashboard queries HyperEVM directly via the public RPC endpoint. No Dune, no API keys, completely free.

## Project Structure

```
nunchi_dashboard/
├── app.py              # Main Streamlit dashboard
├── data_fetcher.py     # HyperEVM data queries
├── config.py           # Contract addresses & settings
├── requirements.txt    # Python dependencies
├── run.sh              # Convenience runner script
└── README.md
```

## Contract Addresses (HyperEVM)

| Contract | Address |
|----------|---------|
| wNLP Token | `0x4Cc221cf1444333510a634CE0D8209D2D11B9bbA` |
| Pendle Market | `0x07a50aEc9B49cD605e66B0cA7e39d781E6Ae0b79` |
| SY-wNLP | `0x9b7430dB2C59247E861702B5C85131eEaf03aED3` |
| PT-wNLP | `0x17a885bb988353f430141890b41f787debc3e107` |
| YT-wNLP | `0x1f6EA7A91477523b9EAD6DB13f1373eAEB312952` |

## Dashboard Sections

### 1. KPI Summary
- Total TVL (nLP)
- 7-day Volume
- Total Fees Collected
- Total Users
- Pendle Deposits

### 2. Pendle Deposits/Withdrawals
- Daily deposits vs withdrawals bar chart
- Net flow area chart

### 3. Pendle Volume
- Daily trading volume
- Cumulative volume
- Daily fees collected

### 4. nLP TVL & Volume
- TVL over time (area chart)
- Daily net changes
- Transfer volume

### 5. Top Holders
- Top 20 wNLP holders table
- Supply distribution pie chart

### 6. User Analytics
- Daily active users
- Users by product (nLP vs Pendle)
- Cumulative unique users

## Configuration

Edit `config.py` to customize:

```python
# Cache settings
CACHE_TTL = 300  # 5 minutes

# Default time range
DEFAULT_DAYS = 30

# RPC endpoint (can use alternative providers)
RPC_URL = "https://rpc.hyperliquid.xyz/evm"
```

## Rate Limits

The public HyperEVM RPC has a rate limit of ~100 requests/minute. The dashboard includes:
- Built-in rate limiting (0.1s delay between requests)
- 5-minute caching to minimize RPC calls
- Batch processing for large queries

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

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
- The contracts may be new or have low activity
- Try increasing the time range slider

**"Connection error"**
- HyperEVM RPC may be temporarily unavailable
- Try refreshing in a few minutes

**Slow loading**
- First load fetches data from blockchain (can take 30-60s)
- Subsequent loads use cached data

## Resources

- [Nunchi Docs](https://docs.nunchi.trade)
- [HyperEVM Docs](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperevm)
- [Pendle Docs](https://docs.pendle.finance)
- [HyperEVMScan](https://hyperevmscan.io)

## License

MIT
