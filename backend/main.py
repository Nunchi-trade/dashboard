"""
Nunchi Dashboard API — Thin FastAPI wrapper around data_fetcher.py
"""

import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import data_fetcher from parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_fetcher import (
    get_accurate_tvl,
    get_pendle_apy,
    get_alltime_totals_hyperscan,
    get_alltime_pendle_markets_hyperscan,
    get_hip3_volumes,
    get_testnet_analytics,
    fetch_hip3_volume,
)

app = FastAPI(title="Nunchi Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = ThreadPoolExecutor(max_workers=8)

HYPERLIQUID_TESTNET_API = "https://api.hyperliquid-testnet.xyz/info"
YEX_MARKET_NAMES = {
    "yex:BTCSWP": "Funding Rate Index Perps (BTCSWP)",
    "yex:VXX": "Volatility Index Perps (VXX)",
    "yex:US3M": "US TBill Yield Perps (US3M)",
}
YEX_PAIRS = ["yex:VXX", "yex:US3M", "yex:BTCSWP"]


def _fetch_yex_volumes():
    """Fetch YEX volumes from Hyperliquid testnet."""
    result = {}
    total = 0
    for pair in YEX_PAIRS:
        vol = fetch_hip3_volume(pair)
        result[pair] = vol
        total += vol["notional_volume"]
    result["total_notional"] = round(total, 2)
    return result


def _fetch_yex_market_data():
    """Fetch live YEX market data (24hr volume, open interest, funding) from Hyperliquid."""
    try:
        resp = requests.post(
            HYPERLIQUID_TESTNET_API,
            json={"type": "metaAndAssetCtxs", "dex": "yex"},
            timeout=15,
        )
        data = resp.json()
        if not isinstance(data, list) or len(data) < 2:
            return {}

        meta = data[0]
        ctxs = data[1]
        universe = meta.get("universe", [])

        markets = {}
        total_24h = 0
        total_oi = 0
        for i, ctx in enumerate(ctxs):
            if i >= len(universe):
                break
            coin = universe[i].get("name", f"yex:unknown_{i}")
            day_vol = float(ctx.get("dayNtlVlm", 0))
            oi = float(ctx.get("openInterest", 0))
            mark = float(ctx.get("markPx", 0))
            # OI is in base units, convert to notional
            oi_notional = oi * mark
            total_24h += day_vol
            total_oi += oi_notional
            # ADV = total notional volume / days trading
            vol_data = fetch_hip3_volume(coin)
            days = vol_data.get("days", 1) or 1
            adv = vol_data["notional_volume"] / days

            markets[coin] = {
                "name": YEX_MARKET_NAMES.get(coin, coin),
                "day_volume": round(day_vol, 2),
                "open_interest": round(oi_notional, 2),
                "adv": round(adv, 2),
                "funding": ctx.get("funding", "0"),
                "mark_price": mark,
            }

        return {
            "markets": markets,
            "total_24h_volume": round(total_24h, 2),
            "total_open_interest": round(total_oi, 2),
        }
    except Exception as e:
        print(f"Error fetching YEX market data: {e}")
        return {}


@app.get("/api/dashboard")
async def dashboard():
    """Single aggregate endpoint returning all dashboard data."""
    loop = asyncio.get_event_loop()

    tvl, apy, alltime, pendle, hip3, testnet, yex, yex_live = await asyncio.gather(
        loop.run_in_executor(executor, get_accurate_tvl),
        loop.run_in_executor(executor, get_pendle_apy),
        loop.run_in_executor(executor, get_alltime_totals_hyperscan),
        loop.run_in_executor(executor, get_alltime_pendle_markets_hyperscan),
        loop.run_in_executor(executor, get_hip3_volumes),
        loop.run_in_executor(executor, get_testnet_analytics),
        loop.run_in_executor(executor, _fetch_yex_volumes),
        loop.run_in_executor(executor, _fetch_yex_market_data),
    )

    return {
        "tvl": tvl,
        "apy": apy,
        "alltime_totals": alltime,
        "alltime_pendle": pendle,
        "hip3_volumes": hip3,
        "testnet": testnet,
        "yex_volumes": yex,
        "yex_markets": yex_live,
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}
