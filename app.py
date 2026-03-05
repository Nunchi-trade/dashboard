"""
Nunchi House Stats Page
Institutional view of house liquidity, player activity, agent flow, and competition results.
Redesigned to match Figma spec (node-id=21:900).
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import os

from data_fetcher import (
    get_kpi_summary as _get_kpi_summary,
    get_pendle_apy as _get_pendle_apy,
    get_accurate_tvl as _get_accurate_tvl,
    get_alltime_totals_hyperscan as _get_alltime_totals_hyperscan,
    get_alltime_pendle_markets_hyperscan as _get_alltime_pendle_markets,
    get_hip3_volumes as _get_hip3_volumes,
    get_testnet_analytics as _get_testnet_analytics,
    get_season_comparison as _get_season_comparison,
    fetch_hip3_volume,
    clear_cache,
    save_alltime_cache,
)

# ---------------------------------------------------------------------------
# Streamlit cached wrappers
# ---------------------------------------------------------------------------

@st.cache_data(ttl=60, show_spinner=False)
def get_accurate_tvl():
    return _get_accurate_tvl()

@st.cache_data(ttl=300, show_spinner=False)
def get_pendle_apy():
    return _get_pendle_apy()

@st.cache_data(ttl=3600, show_spinner=False)
def get_alltime_totals_hyperscan(force_refresh=False):
    return _get_alltime_totals_hyperscan(force_refresh)

@st.cache_data(ttl=3600, show_spinner=False)
def get_alltime_pendle_markets(force_refresh=False):
    return _get_alltime_pendle_markets(force_refresh)

@st.cache_data(ttl=300, show_spinner=False)
def get_hip3_volumes():
    return _get_hip3_volumes()

@st.cache_data(ttl=300, show_spinner=False)
def get_yex_volumes():
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

@st.cache_data(ttl=300, show_spinner=False)
def get_testnet_analytics():
    return _get_testnet_analytics()

@st.cache_data(ttl=300, show_spinner=False)
def get_season_comparison():
    return _get_season_comparison()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Nunchi House Stats",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# CSS — Figma spec tokens (pixel-perfect match to node-id=21:900)
# ---------------------------------------------------------------------------

st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=DM+Serif+Display&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

st.markdown("""
<style>
/* ===== Design tokens from Figma (node 21:900) ===== */
:root {
    --bg: #F7F2EA;
    --dark: #1B1B1F;
    --muted: #4A4450;
    --border: #D8D2D8;
    --border-60: rgba(216, 210, 216, 0.6);
    --border-50: rgba(216, 210, 216, 0.5);
    --green: #00C950;
    --gold: #A87037;
    --white: #FFFFFF;
    --desc-text: #4d453d;
}

/* ===== Aggressive Streamlit reset ===== */
.stApp { background: var(--bg) !important; }
.main .block-container {
    background: transparent !important;
    padding: 0 48px 48px 48px !important;
    max-width: 1600px !important;
}
header[data-testid="stHeader"], #MainMenu, footer { display: none !important; }
[data-testid="stSidebar"] { background-color: var(--white) !important; border-right: 1px solid var(--border) !important; }

/* Kill ALL default Streamlit vertical gaps */
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
.stApp [data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 24px !important; }
[data-testid="element-container"] { margin: 0 !important; }
.element-container { margin: 0 !important; }
[data-testid="stMarkdown"] { margin: 0 !important; padding: 0 !important; }

/* ===== Global typography (Inter is the sole font in Figma export) ===== */
*, p, span, div, label, a, td, th {
    font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ===== Navbar (node 21:1276) ===== */
.nav-bar {
    background: rgba(247, 242, 234, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border-50);
    border-radius: 7px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 -48px 0 -48px;
    position: sticky;
    top: 0;
    z-index: 999;
}
.nav-left {
    display: flex;
    align-items: center;
    gap: 37px;
}
.nav-logo {
    display: inline-grid;
    grid-template-columns: max-content;
    grid-template-rows: max-content;
    align-items: center;
    padding-left: 8px;
}
.nav-logo-nunchi {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2.5px;
    color: var(--dark);
    text-transform: uppercase;
}
.nav-logo-house {
    font-family: 'Canela Text', Georgia, 'DM Serif Display', serif !important;
    font-size: 18.27px;
    font-weight: 700;
    color: var(--dark);
    margin-left: 8px;
}
.nav-pills {
    display: inline-grid;
    grid-template-columns: max-content;
    grid-template-rows: max-content;
    align-items: center;
}
.nav-pill-perps {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(244, 178, 44, 0.08);
    border: 1px solid rgba(244, 178, 44, 0.32);
    border-radius: 12px;
    padding: 9px 11px 9px 9px;
    font-family: 'Avenir', 'Inter', sans-serif !important;
    font-size: 12px;
    font-weight: 500;
    line-height: 16.8px;
    color: var(--dark);
    text-decoration: none;
    white-space: nowrap;
}
.nav-pill-perps:hover { opacity: 0.85; text-decoration: none; color: var(--dark); }
.nav-pill-chips {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 9px;
    font-family: 'Avenir', 'Inter', sans-serif !important;
    font-size: 12px;
    font-weight: 500;
    line-height: 16.8px;
    color: var(--dark);
    text-decoration: none;
    white-space: nowrap;
    margin-left: 0;
}
.nav-pill-chips:hover { opacity: 0.85; text-decoration: none; color: var(--dark); }
.nav-right {
    display: flex;
    align-items: center;
    gap: 8px;
}
.wallet-pill {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--white);
    border: 1px solid var(--border-60);
    border-radius: 999px;
    padding: 9px 13px 9px 9px;
    font-size: 14px;
    font-weight: 600;
    color: var(--dark);
    overflow: hidden;
}
.wallet-left {
    display: flex;
    align-items: center;
    gap: 8px;
}
.usdyp-icon {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--bg);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 700;
    color: var(--gold);
    flex-shrink: 0;
    overflow: hidden;
}
.wallet-balance {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px;
    font-weight: 600;
    color: var(--dark);
    text-align: center;
    white-space: nowrap;
}
.wallet-sep {
    width: 1px;
    height: 20px;
    background: var(--border);
}
.wallet-right {
    display: flex;
    align-items: center;
    gap: 8px;
}
.wallet-user-icon {
    position: relative;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--border-60);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: var(--muted);
}
.wallet-user-icon::after {
    content: '';
    position: absolute;
    bottom: 0;
    right: 0;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green);
    border: 2px solid var(--white);
}
.wallet-addr {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px;
    font-weight: 500;
    color: var(--dark);
    white-space: nowrap;
}
.nav-gear {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 1px solid var(--border);
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: var(--muted);
    cursor: pointer;
}

/* ===== Page header (nodes 21:902-21:904) ===== */
.page-header {
    padding: 24px 0 0 0;
}
.breadcrumb {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
    white-space: nowrap;
}
.page-subtitle {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    margin-top: 8px;
    line-height: normal;
}
.page-desc {
    font-size: 12px;
    font-weight: 400;
    color: var(--desc-text);
    margin-top: 4px;
    line-height: normal;
    max-width: 700px;
}

/* ===== Tab toggle — st.radio pill override (node 21:1352) ===== */
.tab-radio {
    margin-top: 24px;
    margin-bottom: 0;
}
.tab-radio [data-testid="stRadioGroup"] > div {
    display: inline-flex !important;
    gap: 0 !important;
    border: 1px solid var(--border);
    border-radius: 999px;
    background: var(--white);
    padding: 4px;
    height: 42px;
    align-items: center;
    width: auto !important;
}
.tab-radio [data-testid="stRadioGroup"] label {
    border-radius: 999px !important;
    padding: 0 28px !important;
    height: 34px !important;
    display: flex !important;
    align-items: center !important;
    font-size: 12px !important;
    font-weight: 400 !important;
    cursor: pointer !important;
    margin: 0 !important;
    background: transparent !important;
    color: #6b6258 !important;
    white-space: nowrap !important;
    transition: background 0.15s, color 0.15s;
}
.tab-radio [data-testid="stRadioGroup"] label > div:first-child { display: none !important; }
.tab-radio [data-testid="stWidgetLabel"] { display: none !important; }
.tab-radio [data-testid="stRadioGroup"] label[data-checked="true"],
.tab-radio [data-testid="stRadioGroup"] label[aria-checked="true"],
.tab-radio [data-testid="stRadioGroup"] div[data-checked="true"] label,
.tab-radio [data-testid="stRadioGroup"] label:has(input:checked) {
    background: var(--dark) !important;
    color: var(--white) !important;
}
.tab-radio [data-testid="stRadioGroup"] label[data-baseweb="radio"] input:checked + div {
    background: var(--dark) !important;
    color: var(--white) !important;
}
.tab-radio [data-testid="stRadioGroup"] [role="radiogroup"] > label[data-testid="stMarkdownContainer"],
.tab-radio [data-testid="stRadioGroup"] [role="radiogroup"] > div[aria-checked="true"] > label {
    background: var(--dark) !important;
    color: var(--white) !important;
}

/* Info chips row (nodes 21:909, 21:912) */
.info-chips-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.info-chip {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
    white-space: nowrap;
}

/* ===== Panel cards (nodes 21:915, 21:956) ===== */
.panel {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    min-height: 315px;
    box-sizing: border-box;
    overflow: hidden;
}
.panel-label {
    font-size: 12px;
    font-weight: 400;
    letter-spacing: 0;
    color: var(--dark);
    line-height: normal;
    margin-bottom: 8px;
}
.panel-title {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
}
.panel-desc {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
    margin-bottom: 20px;
}

/* ===== Metric row (TOTAL TVL | LP WALLETS, nodes 21:923-21:928) ===== */
.metric-row {
    display: flex;
    gap: 48px;
    margin-bottom: 20px;
}
.metric-label {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    text-transform: uppercase;
    line-height: normal;
}
.metric-value {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    margin-top: 4px;
    line-height: normal;
}

/* ===== TVL bar rows (nodes 21:929-21:955) ===== */
.tvl-bars {
    display: flex;
    flex-direction: column;
    gap: 0;
}
.tvl-row {
    display: flex;
    align-items: center;
    height: 30px;
}
.tvl-name {
    font-size: 12px;
    font-weight: 700;
    color: var(--dark);
    min-width: 130px;
    line-height: normal;
}
.tvl-val {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    min-width: 80px;
    text-align: right;
    padding-right: 12px;
    line-height: normal;
}
.tvl-bar-track {
    flex: 1;
    height: 18px;
    background: var(--border-60);
    border-radius: 4px;
    overflow: hidden;
}
.tvl-bar-fill {
    height: 100%;
    border-radius: 4px;
}
.tvl-bar-fill.nlp { background: var(--gold); }
.tvl-bar-fill.pendle { background: #6B5B95; }
.tvl-bar-fill.nhype { background: var(--green); }

/* ===== Players stat grid (nodes 21:970-21:990) ===== */
.players-divider {
    width: 100%;
    height: 1px;
    background: var(--border);
    margin: 16px 0 16px 0;
}
.stat-table {
    display: grid;
    grid-template-columns: 1fr 1fr;
    row-gap: 14px;
    column-gap: 24px;
}
.stat-table-item {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}
.stat-table-label {
    font-size: 12px;
    font-weight: 700;
    color: var(--dark);
    line-height: normal;
}
.stat-table-value {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
}

/* ===== Section header (PLAYER FEED, AGENT FLOW, etc.) ===== */
.section-hdr {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}
.section-label {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
}
.section-pill {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    letter-spacing: 0;
}
.section-title {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
    margin-bottom: 2px;
}
.section-desc {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
    margin-bottom: 12px;
}

/* ===== Chart row — style Streamlit column internals as cards ===== */
.chart-row [data-testid="stColumn"] > div > div {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    overflow: hidden;
}
.chart-row [data-testid="stColumn"] > div > [data-testid="stVerticalBlockBorderWrapper"] > div {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    overflow: hidden;
}

/* ===== Agent flow card (node 21:1034) ===== */
.side-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    min-height: 356px;
    box-sizing: border-box;
}
.agent-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 12px;
}
.agent-box {
    background: var(--bg);
    border: 1px solid var(--border-60);
    border-radius: 12px;
    padding: 14px 16px;
    min-height: 80px;
}
.agent-box-label {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    text-transform: uppercase;
    line-height: normal;
    margin-bottom: 6px;
}
.agent-box-value {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
}
.agent-box-desc {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    margin-top: 4px;
    line-height: normal;
}

/* ===== Feed composition (node 21:1228) ===== */
.fc-box {
    background: var(--bg);
    border: 1px solid var(--border-60);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.fc-box-label {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    text-transform: uppercase;
    line-height: normal;
}
.fc-box-value {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
    margin-top: 2px;
}
.fc-venue-title {
    font-size: 12px;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 4px;
    line-height: normal;
}
.fc-venue-list {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
    padding-left: 16px;
    margin: 0;
}
.fc-venue-list li { margin-bottom: 2px; }
.fc-pills {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 10px;
}
.fc-pill {
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 6px 12px;
    font-size: 12px;
    font-weight: 700;
    color: var(--dark);
    text-align: center;
    background: var(--white);
    line-height: normal;
}

/* ===== Competition section (node 21:1060) ===== */
.comp-section-label {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    text-transform: uppercase;
    margin-bottom: 8px;
    line-height: normal;
}
.comp-section-heading {
    font-family: 'Inter', sans-serif !important;
    font-size: 38px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
    margin-bottom: 8px;
}
.comp-section-desc {
    font-size: 12px;
    font-weight: 400;
    color: var(--desc-text);
    line-height: normal;
    margin-bottom: 24px;
    max-width: 754px;
}

/* Competition card (nodes 21:1067, 21:1115, 21:1135, 21:1162) */
.comp-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 24px;
    min-height: 288px;
    box-sizing: border-box;
    position: relative;
    overflow: hidden;
}
.comp-card-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}
.comp-card-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
/* YP logo — gradient per Figma: from-[#fdecc1] 85.7% to-[#a87037] 161.6% */
.yp-logo {
    width: 92px;
    height: 92px;
    border-radius: 50%;
    background: linear-gradient(180deg, #fdecc1 85.7%, #a87037 161.6%);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    overflow: hidden;
}
.yp-logo-inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Canela Text', 'DM Serif Display', Georgia, serif !important;
    font-size: 45.48px;
    font-weight: 700;
    color: transparent;
    background: linear-gradient(180deg, #fdecc1 85.7%, #a87037 161.6%);
    -webkit-background-clip: text;
    background-clip: text;
    letter-spacing: 29.56px;
    line-height: 16.99px;
    text-align: center;
    white-space: pre-wrap;
}
.yp-logo-text {
    font-family: 'Canela Text', 'DM Serif Display', Georgia, serif !important;
    font-size: 28px;
    font-weight: 700;
    color: var(--white);
    letter-spacing: 4px;
}
.comp-card-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.comp-card-name {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
}
.comp-card-date {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    line-height: normal;
}
.comp-venue-pill {
    background: var(--bg);
    border: 1px solid var(--border-60);
    border-radius: 999px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    white-space: nowrap;
    align-self: flex-start;
}
.comp-meta {
    display: flex;
    gap: 32px;
    margin-bottom: 16px;
}
.comp-meta-label {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    text-transform: uppercase;
    line-height: normal;
}
.comp-meta-value {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    margin-top: 4px;
    line-height: normal;
}
.comp-divider {
    width: 100%;
    height: 1px;
    background: var(--border);
    margin: 12px 0;
}
.comp-wallets-label {
    font-size: 12px;
    font-weight: 700;
    color: var(--dark);
    margin-bottom: 8px;
    line-height: normal;
}
.wallet-rows-container {
    border: 1px solid var(--border-60);
    border-radius: 12px;
    overflow: hidden;
}
.wallet-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-60);
    font-size: 12px;
}
.wallet-row:last-child { border-bottom: none; }
.wallet-rank {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--border-60);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 700;
    color: var(--dark);
    flex-shrink: 0;
}
.wallet-addr-cell {
    font-family: 'Inter', sans-serif !important;
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    flex: 1;
}
.wallet-pnl {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    margin-left: auto;
}

/* ===== Footer (node 21:1182) ===== */
.page-footer {
    font-size: 12px;
    font-weight: 400;
    color: var(--dark);
    padding: 24px 0;
    margin-top: 40px;
    border-top: 1px solid var(--border);
    line-height: normal;
}

/* Remove default Streamlit horizontal rule styling */
hr { border-color: var(--border) !important; }

/* Force plotly charts to not add extra padding */
[data-testid="stPlotlyChart"] > div { margin-top: -8px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar (minimal)
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### Settings")
    if st.button("Refresh Data"):
        clear_cache()
        st.rerun()
    if st.button("Refresh All-Time"):
        save_alltime_cache({})
        st.cache_data.clear()
        clear_cache()
        st.rerun()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

try:
    accurate_tvl = get_accurate_tvl()
except Exception:
    accurate_tvl = {"wNLP_tvl": 0, "SY_tvl": 0, "nHYPE_tvl": 0}

try:
    apy_data = get_pendle_apy()
except Exception:
    apy_data = {}

with st.spinner("Loading data..."):
    try:
        alltime_totals = get_alltime_totals_hyperscan()
    except Exception:
        alltime_totals = {}

    try:
        alltime_pendle = get_alltime_pendle_markets()
    except Exception:
        alltime_pendle = {}

    try:
        hip3_volumes = get_hip3_volumes()
    except Exception:
        hip3_volumes = {}

    try:
        yex_volumes = get_yex_volumes()
    except Exception:
        yex_volumes = {}

    try:
        testnet_data = get_testnet_analytics()
    except Exception:
        testnet_data = {}

# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------

nlp_tvl = accurate_tvl.get("wNLP_tvl", 0)
pendle_tvl = sum(info["tvl_usd"] for info in apy_data.values()) if apy_data else 0
nhype_tvl = accurate_tvl.get("nHYPE_tvl", 0)
total_tvl = nlp_tvl + pendle_tvl  # nHYPE is in HYPE, not USD

# LP wallets
nlp_users = alltime_totals.get("wNLP", {}).get("unique_users", 0) if alltime_totals else 0
pendle_users = 0
if alltime_pendle:
    for k, v in alltime_pendle.items():
        if k != "timestamp":
            pendle_users += v.get("unique_users", 0)
total_lp_wallets = nlp_users + pendle_users

# Player totals
totals = testnet_data.get("totals", {}) if testnet_data else {}
total_volume = totals.get("total_volume", 0)
total_wallets = totals.get("total_users", 0)

# Add YEX volume to total
yex_total = yex_volumes.get("total_notional", 0)
total_volume += yex_total

# Markets traded
total_markets = 0
if testnet_data:
    s1_assets = testnet_data.get("season_one", {}).get("by_asset", {})
    s2_assets = testnet_data.get("season_two", {}).get("by_asset", {})
    all_assets = set(list(s1_assets.keys()) + list(s2_assets.keys()))
    all_assets.update(["US3M", "VXX", "BTCSWP"])
    total_markets = len(all_assets)

# Competition data
simulator = testnet_data.get("simulator", {}) if testnet_data else {}
s1 = testnet_data.get("season_one", {}) if testnet_data else {}
s2 = testnet_data.get("season_two", {}) if testnet_data else {}

COMP_INFO = [
    {
        "num": "I", "name": "COMPETITION I", "date": "July 2025 - Simulator",
        "venue": "THE ARENA", "leaderboard": "The Arena",
        "duration": f"{simulator.get('total_users', 0)} users",
        "volume": simulator.get("total_volume", 0),
    },
    {
        "num": "II", "name": "COMPETITION II", "date": "September 2025 - Season 1",
        "venue": "MEGAETH + MONAD", "leaderboard": "MegaETH, Monad",
        "duration": f"{s1.get('total', {}).get('total_users', 0)} users",
        "volume": s1.get("total", {}).get("total_volume", 0),
    },
    {
        "num": "III", "name": "COMPETITION III", "date": "November 2025 - Season 2",
        "venue": "MEGAETH + MONAD + HYPERLIQUID", "leaderboard": "MegaETH, Monad, Hyperliquid",
        "duration": f"{s2.get('total', {}).get('total_users', 0)} users",
        "volume": s2.get("total", {}).get("total_volume", 0),
    },
    {
        "num": "IV", "name": "COMPETITION IV", "date": "January 2026 - Hyperliquid Testnet",
        "venue": "HYPERLIQUID", "leaderboard": "Hyperliquid",
        "duration": "YEX DEX",
        "volume": yex_total,
    },
]

# ===========================================================================
# RENDER — pixel-perfect match to Figma node-id=21:900
# ===========================================================================

# ---------------------------------------------------------------------------
# 1. NAVBAR (node 21:1276 — sticky header with blur)
# ---------------------------------------------------------------------------

st.markdown("""
<div class="nav-bar">
    <div class="nav-left">
        <div class="nav-logo">
            <span class="nav-logo-nunchi">NUNCHI</span>
            <span class="nav-logo-house">HOUSE</span>
        </div>
        <div class="nav-pills">
            <a href="https://nunchi.trade" target="_blank" class="nav-pill-perps">Back to Perps Trading</a>
            <a href="https://docs.nunchi.trade" target="_blank" class="nav-pill-chips">How to earn cHIPs &#8599;</a>
        </div>
    </div>
    <div class="nav-right">
        <div class="wallet-pill">
            <div class="wallet-left">
                <div class="usdyp-icon">YP</div>
                <span class="wallet-balance">$3.53K</span>
            </div>
            <div class="wallet-sep"></div>
            <div class="wallet-right">
                <div class="wallet-user-icon">&#9679;</div>
                <span class="wallet-addr">0x065D&hellip;C827</span>
            </div>
        </div>
        <div class="nav-gear">&#9881;</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 2. PAGE HEADER (nodes 21:902-21:904)
# ---------------------------------------------------------------------------

st.markdown("""
<div class="page-header">
    <div class="breadcrumb">STATS &bull; HOUSE &mdash; PLAYERS</div>
    <div class="page-subtitle">Liquidity, competition, and agent activity</div>
    <div class="page-desc">
        A single institutional view of house liquidity providers, player activity, agent flow,
        and competition results across the full Nunchi ecosystem.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 3. TAB TOGGLE (node 21:1352) + INFO CHIPS (nodes 21:909, 21:912)
# ---------------------------------------------------------------------------

st.markdown('<div class="tab-radio">', unsafe_allow_html=True)
active_tab = st.radio(
    "",
    ["House", "Players"],
    horizontal=True,
    label_visibility="collapsed",
    key="active_tab",
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-chips-row">
    <div class="info-chip">Current TVL = nLP + PT-wNLP + nHYPE</div>
    <div class="info-chip">Player feed = all competitions composited together</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 4. HOUSE + PLAYERS panels — 50/50 (nodes 21:915, 21:956)
# ---------------------------------------------------------------------------

max_tvl = max(nlp_tvl, pendle_tvl, nhype_tvl, 1)

col_house, col_players = st.columns(2)

with col_house:
    nlp_pct = min(nlp_tvl / max_tvl * 100, 100)
    pendle_pct = min(pendle_tvl / max_tvl * 100, 100)
    nhype_pct = min(nhype_tvl / max_tvl * 100, 100)

    st.markdown(f"""
    <div class="panel">
        <div class="panel-label">HOUSE</div>
        <div class="panel-title">House Liquidity Providers</div>
        <div class="panel-desc">Unique wallets across nLP, Pendle LP/PT-wNLP, and staked HYPE in nHYPE.</div>
        <div class="metric-row">
            <div>
                <div class="metric-label">TOTAL TVL</div>
                <div class="metric-value">${total_tvl:,.0f}</div>
            </div>
            <div>
                <div class="metric-label">LP WALLETS</div>
                <div class="metric-value">{total_lp_wallets:,}</div>
            </div>
        </div>
        <div class="players-divider"></div>
        <div class="tvl-bars">
            <div class="tvl-row">
                <span class="tvl-name">nLP</span>
                <span class="tvl-val">${nlp_tvl:,.0f}</span>
                <div class="tvl-bar-track"><div class="tvl-bar-fill nlp" style="width:{nlp_pct:.1f}%"></div></div>
            </div>
            <div class="tvl-row">
                <span class="tvl-name">Pendle LP / PT-wNLP</span>
                <span class="tvl-val">${pendle_tvl:,.0f}</span>
                <div class="tvl-bar-track"><div class="tvl-bar-fill pendle" style="width:{pendle_pct:.1f}%"></div></div>
            </div>
            <div class="tvl-row">
                <span class="tvl-name">nHYPE</span>
                <span class="tvl-val">{nhype_tvl:,.0f} HYPE</span>
                <div class="tvl-bar-track"><div class="tvl-bar-fill nhype" style="width:{nhype_pct:.1f}%"></div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_players:
    st.markdown(f"""
    <div class="panel">
        <div class="panel-label">PLAYERS</div>
        <div class="panel-title">Total Players</div>
        <div class="panel-desc">Aggregate wallets, volumes, markets, and agent flow across Competition I, II, III, and IV.</div>
        <div class="metric-row">
            <div>
                <div class="metric-label">TOTAL VOLUME</div>
                <div class="metric-value">${total_volume:,.0f}</div>
            </div>
            <div>
                <div class="metric-label">TOTAL WALLETS</div>
                <div class="metric-value">{total_wallets:,}</div>
            </div>
        </div>
        <div class="players-divider"></div>
        <div class="stat-table">
            <div class="stat-table-item">
                <span class="stat-table-label">Markets traded</span>
                <span class="stat-table-value">{total_markets}</span>
            </div>
            <div class="stat-table-item">
                <span class="stat-table-label">Orders filled value</span>
                <span class="stat-table-value">${total_volume:,.0f}</span>
            </div>
            <div class="stat-table-item">
                <span class="stat-table-label">Active agents</span>
                <span class="stat-table-value">&mdash;</span>
            </div>
            <div class="stat-table-item">
                <span class="stat-table-label">Composite feed window</span>
                <span class="stat-table-value">Jul 2025 &rarr; Now</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 5. PLAYER FEED chart + AGENT FLOW — 68/32 split (nodes 21:991, 21:1034)
# ---------------------------------------------------------------------------

comp_volumes = [
    ("Comp I", simulator.get("total_volume", 0)),
    ("Comp II", s1.get("total", {}).get("total_volume", 0)),
    ("Comp III", s2.get("total", {}).get("total_volume", 0)),
    ("Comp IV", yex_total),
]
dates = [
    datetime(2025, 7, 1), datetime(2025, 9, 1),
    datetime(2025, 11, 1), datetime(2026, 1, 1),
    datetime.now(),
]
cumulative = [0]
running = 0
for _, vol in comp_volumes:
    running += vol
    cumulative.append(running)

st.markdown('<div class="chart-row">', unsafe_allow_html=True)
col_feed, col_agent = st.columns([68, 32])

with col_feed:
    st.markdown("""
        <div class="section-hdr">
            <div class="section-label">PLAYER FEED</div>
            <div class="section-pill">COMPOSITED FEED</div>
        </div>
        <div class="section-title">Total Cumulative Volumes</div>
        <div class="section-desc">All competition data composited into one feed, from July 2025 to now.</div>
    """, unsafe_allow_html=True)

    fig_feed = go.Figure()
    fig_feed.add_trace(go.Scatter(
        x=dates, y=cumulative,
        mode="lines", name="Cumulative Volume",
        line=dict(width=2.5, color="#00C950"),
        fill="tozeroy", fillcolor="rgba(0, 201, 80, 0.06)",
    ))
    for i, (label, _) in enumerate(comp_volumes):
        fig_feed.add_vline(x=dates[i + 1], line_width=1, line_dash="dash", line_color="#D8D2D8")
        fig_feed.add_annotation(
            x=dates[i + 1], y=cumulative[i + 1],
            text=label, showarrow=False, yshift=15,
            font=dict(size=10, color="#1B1B1F", family="Inter"),
        )
    fig_feed.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1B1B1F", size=12),
        xaxis=dict(gridcolor="#F7F2EA", linecolor="#D8D2D8", title="", zeroline=False),
        yaxis=dict(gridcolor="#F7F2EA", linecolor="#D8D2D8", title="", tickprefix="$", tickformat=",.0f", zeroline=False),
        height=240, margin=dict(l=60, r=16, t=8, b=36),
        showlegend=False, hovermode="x unified",
    )
    st.plotly_chart(fig_feed, use_container_width=True, config={"displayModeBar": False})

with col_agent:
    st.markdown(f"""
    <div class="side-card">
        <div class="section-hdr">
            <div class="section-label">AGENT FLOW</div>
        </div>
        <div class="section-title">Agent Trades</div>
        <div class="section-desc">Number of agents active, volumes, markets, and orders filled value (USDYP).</div>
        <div class="agent-grid">
            <div class="agent-box">
                <div class="agent-box-label">ACTIVE AGENTS</div>
                <div class="agent-box-value">&mdash;</div>
                <div class="agent-box-desc">currently in the composite feed</div>
            </div>
            <div class="agent-box">
                <div class="agent-box-label">AGENT VOLUME</div>
                <div class="agent-box-value">&mdash;</div>
                <div class="agent-box-desc">all competitions combined</div>
            </div>
            <div class="agent-box">
                <div class="agent-box-label">AGENT MARKETS</div>
                <div class="agent-box-value">&mdash;</div>
                <div class="agent-box-desc">unique markets touched</div>
            </div>
            <div class="agent-box">
                <div class="agent-box-label">FILLED VALUE (USDYP)</div>
                <div class="agent-box-value">&mdash;</div>
                <div class="agent-box-desc">orders filled across agents</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 6. NET PNL chart + FEED COMPOSITION — 68/32 split (nodes 21:1183, 21:1228)
# ---------------------------------------------------------------------------

s1_profit = s1.get("total", {}).get("net_profit", 0)
s2_profit = s2.get("total", {}).get("net_profit", 0)
pnl_dates = [
    datetime(2025, 7, 1), datetime(2025, 9, 1),
    datetime(2025, 11, 1), datetime(2026, 1, 1),
    datetime.now(),
]
pnl_values = [0, 0, s1_profit, s1_profit + s2_profit, s1_profit + s2_profit]

st.markdown('<div class="chart-row">', unsafe_allow_html=True)
col_pnl, col_comp = st.columns([68, 32])

with col_pnl:
    st.markdown("""
        <div class="section-hdr">
            <div class="section-label">PLAYER FEED</div>
            <div class="section-pill">ALL COMPETITIONS COMBINED</div>
        </div>
        <div class="section-title">Net PNL Over Time</div>
        <div class="section-desc">Net PNL across all competitions composited into one continuous feed.</div>
    """, unsafe_allow_html=True)

    fig_pnl = go.Figure()
    fig_pnl.add_trace(go.Scatter(
        x=pnl_dates, y=pnl_values,
        mode="lines", name="Net PNL",
        line=dict(width=2.5, color="#00C950"),
        fill="tozeroy", fillcolor="rgba(0, 201, 80, 0.06)",
    ))
    for i, label in enumerate(["Comp I", "Comp II", "Comp III", "Comp IV"]):
        fig_pnl.add_vline(x=pnl_dates[i + 1], line_width=1, line_dash="dash", line_color="#D8D2D8")
        fig_pnl.add_annotation(
            x=pnl_dates[i + 1], y=pnl_values[i + 1],
            text=label, showarrow=False, yshift=15,
            font=dict(size=10, color="#1B1B1F", family="Inter"),
        )
    fig_pnl.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#1B1B1F", size=12),
        xaxis=dict(gridcolor="#F7F2EA", linecolor="#D8D2D8", title="", zeroline=False),
        yaxis=dict(gridcolor="#F7F2EA", linecolor="#D8D2D8", title="", tickprefix="$", tickformat=",.0f", zeroline=False),
        height=240, margin=dict(l=60, r=16, t=8, b=36),
        showlegend=False, hovermode="x unified",
    )
    st.plotly_chart(fig_pnl, use_container_width=True, config={"displayModeBar": False})

with col_comp:
    st.markdown(f"""
    <div class="side-card">
        <div class="section-hdr">
            <div class="section-label">FEED COMPOSITION</div>
        </div>
        <div class="section-title">Markets, venues, and seasons</div>
        <div class="section-desc" style="margin-bottom:8px;">Competition coverage contributing to the composite player feed.</div>
        <div class="fc-box">
            <div class="fc-box-label">NUMBER OF MARKETS TRADED</div>
            <div class="fc-box-value">{total_markets}</div>
        </div>
        <div class="fc-box">
            <div class="fc-venue-title">Venue coverage</div>
            <ul class="fc-venue-list">
                <li>&bull; The Arena</li>
                <li>&bull; MegaETH</li>
                <li>&bull; Monad</li>
                <li>&bull; Hyperliquid</li>
            </ul>
        </div>
        <div class="fc-pills">
            <div class="fc-pill">Comp I</div>
            <div class="fc-pill">Comp II</div>
            <div class="fc-pill">Comp III</div>
            <div class="fc-pill">Comp IV</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 7. COMPETITIONS section (node 21:1060)
# ---------------------------------------------------------------------------

st.markdown("""
<div style="margin-top: 40px; padding-top: 24px;">
    <div class="comp-section-label">COMPETITIONS</div>
    <div class="comp-section-heading">Competition history</div>
    <div class="comp-section-desc">
        Each competition card shows period, format, number of days, venues, and top 3 wallet results. Replace placeholders with live values.
    </div>
</div>
""", unsafe_allow_html=True)

# Row 1: Comp I + Comp II
comp_r1c1, comp_r1c2 = st.columns(2)
# Row 2: Comp III + Comp IV
comp_r2c1, comp_r2c2 = st.columns(2)

comp_cols = [comp_r1c1, comp_r1c2, comp_r2c1, comp_r2c2]

for idx, comp in enumerate(COMP_INFO):
    with comp_cols[idx]:
        wallet_html = ""
        for rank in range(1, 4):
            wallet_html += f"""
            <div class="wallet-row">
                <div class="wallet-rank">{rank}</div>
                <div class="wallet-addr-cell">[wallet #{rank}]</div>
                <div class="wallet-pnl">PNL [value]</div>
            </div>
            """

        st.markdown(f"""
        <div class="comp-card">
            <div class="comp-card-top">
                <div class="comp-card-left">
                    <div class="yp-logo"><span class="yp-logo-text">Y P</span></div>
                    <div class="comp-card-info">
                        <div class="comp-card-name">{comp['name']}</div>
                        <div class="comp-card-date">{comp['date']}</div>
                    </div>
                </div>
                <div class="comp-venue-pill">{comp['venue']}</div>
            </div>
            <div class="comp-meta">
                <div>
                    <div class="comp-meta-label">DURATION</div>
                    <div class="comp-meta-value">{comp['duration']}</div>
                </div>
                <div>
                    <div class="comp-meta-label">LEADERBOARD</div>
                    <div class="comp-meta-value">{comp['leaderboard']}</div>
                </div>
            </div>
            <div class="comp-divider"></div>
            <div class="comp-wallets-label">Top 3 wallets</div>
            <div class="wallet-rows-container">
                {wallet_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 8. FOOTER (node 21:1182)
# ---------------------------------------------------------------------------

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f"""
<div class="page-footer">
    Notes: swap bracketed placeholders with live metrics, wallet IDs, PNL, and day counts.
    Charts are intentionally illustrative and keep the Nunchi institutional aesthetic.
    <br>Last updated: {current_time}
</div>
""", unsafe_allow_html=True)
