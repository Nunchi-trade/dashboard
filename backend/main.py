"""
Nunchi Dashboard API — Thin FastAPI wrapper around data_fetcher.py
"""

import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

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


def _fetch_yex_volumes():
    """Fetch YEX volumes from Hyperliquid testnet."""
    yex_pairs = ["yex:US3M", "yex:VXX", "yex:BTCSWP"]
    result = {}
    total = 0
    for pair in yex_pairs:
        vol = fetch_hip3_volume(pair)
        result[pair] = vol
        total += vol["notional_volume"]
    result["total_notional"] = round(total, 2)
    return result


@app.get("/api/dashboard")
async def dashboard():
    """Single aggregate endpoint returning all dashboard data."""
    loop = asyncio.get_event_loop()

    tvl, apy, alltime, pendle, hip3, testnet, yex = await asyncio.gather(
        loop.run_in_executor(executor, get_accurate_tvl),
        loop.run_in_executor(executor, get_pendle_apy),
        loop.run_in_executor(executor, get_alltime_totals_hyperscan),
        loop.run_in_executor(executor, get_alltime_pendle_markets_hyperscan),
        loop.run_in_executor(executor, get_hip3_volumes),
        loop.run_in_executor(executor, get_testnet_analytics),
        loop.run_in_executor(executor, _fetch_yex_volumes),
    )

    return {
        "tvl": tvl,
        "apy": apy,
        "alltime_totals": alltime,
        "alltime_pendle": pendle,
        "hip3_volumes": hip3,
        "testnet": testnet,
        "yex_volumes": yex,
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}
