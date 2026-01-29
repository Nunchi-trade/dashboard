"""
Nunchi Analytics Dashboard
Real-time analytics for Nunchi (nunchi.trade) on HyperEVM
Styled with Nunchi brand design - Tabbed layout
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

from data_fetcher import (
    get_kpi_summary as _get_kpi_summary,
    get_daily_pendle_deposits as _get_daily_pendle_deposits,
    get_daily_volume as _get_daily_volume,
    get_nlp_tvl as _get_nlp_tvl,
    get_daily_nlp_volume as _get_daily_nlp_volume,
    get_top_holders as _get_top_holders,
    get_user_stats as _get_user_stats,
    get_market_stats as _get_market_stats,
    get_pendle_apy as _get_pendle_apy,
    get_apy_history as _get_apy_history,
    get_accurate_tvl as _get_accurate_tvl,
    get_alltime_totals_hyperscan as _get_alltime_totals_hyperscan,
    get_alltime_pendle_markets_hyperscan as _get_alltime_pendle_markets,
    get_pendle_peak_tvls as _get_pendle_peak_tvls,
    get_hip3_volumes as _get_hip3_volumes,
    get_testnet_analytics as _get_testnet_analytics,
    get_season_comparison as _get_season_comparison,
    get_pendle_swaps,
    get_pendle_lp_events,
    clear_cache,
    save_alltime_cache,
)
from config import CONTRACTS, PENDLE_MARKETS

# Streamlit cached wrappers for faster reloads
@st.cache_data(ttl=300, show_spinner=False)
def get_kpi_summary(days):
    return _get_kpi_summary(days)

@st.cache_data(ttl=300, show_spinner=False)
def get_daily_pendle_deposits(days):
    return _get_daily_pendle_deposits(days)

@st.cache_data(ttl=300, show_spinner=False)
def get_daily_volume(days):
    return _get_daily_volume(days)

@st.cache_data(ttl=300, show_spinner=False)
def get_nlp_tvl(days):
    return _get_nlp_tvl(days)

@st.cache_data(ttl=300, show_spinner=False)
def get_daily_nlp_volume(days):
    return _get_daily_nlp_volume(days)

@st.cache_data(ttl=300, show_spinner=False)
def get_top_holders(days):
    return _get_top_holders(days)

@st.cache_data(ttl=300, show_spinner=False)
def get_user_stats(days):
    return _get_user_stats(days)

@st.cache_data(ttl=300, show_spinner=False)
def get_market_stats(days):
    return _get_market_stats(days)

@st.cache_data(ttl=300, show_spinner=False)
def get_pendle_apy():
    return _get_pendle_apy()

@st.cache_data(ttl=300, show_spinner=False)
def get_apy_history(days):
    return _get_apy_history(days)

@st.cache_data(ttl=60, show_spinner=False)
def get_accurate_tvl():
    return _get_accurate_tvl()

@st.cache_data(ttl=3600, show_spinner=False)
def get_alltime_totals_hyperscan(force_refresh=False):
    return _get_alltime_totals_hyperscan(force_refresh)

@st.cache_data(ttl=3600, show_spinner=False)
def get_alltime_pendle_markets(force_refresh=False):
    return _get_alltime_pendle_markets(force_refresh)

@st.cache_data(ttl=3600, show_spinner=False)
def get_pendle_peak_tvls(force_refresh=False):
    return _get_pendle_peak_tvls(force_refresh)

@st.cache_data(ttl=300, show_spinner=False)
def get_hip3_volumes():
    return _get_hip3_volumes()

@st.cache_data(ttl=300, show_spinner=False)
def get_testnet_analytics():
    return _get_testnet_analytics()

@st.cache_data(ttl=300, show_spinner=False)
def get_season_comparison():
    return _get_season_comparison()

# Page config
st.set_page_config(
    page_title="Nunchi Stats",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Nunchi Brand CSS - Warm paper theme
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* CSS Variables - Nunchi Brand Tokens */
    :root {
        --bg: #F6F1EA;
        --panel: #FFFCF7;
        --ink: #121317;
        --muted: #6C6A63;
        --line: #E2D8C7;
        --line2: #EDE3D6;
        --accent: #8A7650;
        --accent2: #B9A98A;
        --green: #2BB673;
    }

    /* Main app background */
    .stApp {
        background: linear-gradient(180deg, #FBF8F2 0%, #F4EFE6 100%) !important;
    }

    .main .block-container {
        background: transparent !important;
        padding-top: 0;
        padding-bottom: 2rem;
        max-width: 1600px;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Typography */
    h1, h2, h3 {
        font-family: Georgia, "Times New Roman", serif !important;
        color: var(--ink) !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    h1 {
        font-size: 2.2rem !important;
        margin-bottom: 0.25rem !important;
    }

    h2, .stSubheader {
        font-size: 1.1rem !important;
        font-weight: 650 !important;
        letter-spacing: 0.6px;
    }

    p, span, div, label {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif !important;
        color: var(--ink);
    }

    /* Muted text */
    .muted-text {
        color: var(--muted) !important;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Top bar */
    .top-bar {
        background: var(--panel);
        border-bottom: 1px solid var(--line);
        padding: 18px 0;
        margin: -1rem -1rem 1.5rem -1rem;
    }

    .top-bar-inner {
        max-width: 1600px;
        margin: 0 auto;
        padding: 0 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .brand-name {
        font-family: Inter, sans-serif;
        font-size: 16px;
        font-weight: 800;
        letter-spacing: 3px;
        color: var(--ink);
    }

    .brand-sub {
        font-family: Inter, sans-serif;
        font-size: 14px;
        font-weight: 650;
        letter-spacing: 2px;
        color: var(--accent);
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 18px !important;
        padding: 20px 22px !important;
        box-shadow: 0 10px 14px rgba(0, 0, 0, 0.08) !important;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.1) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
        font-size: 12px !important;
        font-weight: 650 !important;
        letter-spacing: 0.7px !important;
        text-transform: uppercase !important;
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
        font-size: 1.5rem !important;
        font-weight: 750 !important;
        color: var(--ink) !important;
    }

    [data-testid="stMetricDelta"] {
        color: var(--accent) !important;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--panel) !important;
        border-right: 1px solid var(--line) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--ink) !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--panel) !important;
        color: var(--ink) !important;
        border: 1.5px solid var(--line) !important;
        border-radius: 18px !important;
        font-family: Inter, sans-serif !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }

    /* Dividers */
    hr {
        border: none !important;
        height: 1px !important;
        background: var(--line) !important;
        margin: 1.5rem 0 !important;
    }

    /* Tabs - match design mockup */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        gap: 24px;
        border-bottom: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        color: var(--muted) !important;
        font-family: Inter, sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 0 !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: transparent !important;
        color: var(--ink) !important;
        font-weight: 700 !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Card containers */
    .card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 10px 14px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }

    .card-header {
        font-family: Inter, sans-serif;
        font-size: 16px;
        font-weight: 650;
        color: var(--ink);
        margin-bottom: 4px;
    }

    .card-subtitle {
        font-family: Inter, sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: var(--muted);
        margin-bottom: 16px;
    }

    /* Data table styling */
    .data-row {
        background: #FFFEFB;
        border: 1px solid var(--line2);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .data-label {
        font-family: Inter, sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: var(--muted);
    }

    .data-value {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 14px;
        font-weight: 500;
        color: var(--muted);
    }

    /* APY pills */
    .apy-pill {
        display: inline-flex;
        align-items: center;
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 17px;
        padding: 8px 16px;
        margin-right: 12px;
        margin-bottom: 12px;
    }

    .apy-pill-label {
        font-family: Inter, sans-serif;
        font-size: 12px;
        font-weight: 650;
        letter-spacing: 0.7px;
        color: var(--muted);
        margin-right: 12px;
    }

    .apy-pill-value {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-size: 14px;
        font-weight: 500;
        color: var(--muted);
    }

    /* Pool status badges */
    .pool-active {
        color: #2BB673;
        font-weight: 600;
    }

    .pool-expired {
        color: #D9534F;
        font-weight: 600;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1.5rem 0;
        border-top: 1px solid var(--line);
        margin-top: 2rem;
    }

    .footer-text {
        font-family: Inter, sans-serif;
        font-size: 12px;
        color: var(--muted);
    }

    .footer-link {
        color: var(--accent) !important;
        text-decoration: underline;
        font-size: 12px;
        font-family: Inter, sans-serif;
        font-weight: 650;
    }

    /* DataFrames */
    .stDataFrame {
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
    }

    /* Info boxes */
    .stAlert {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        color: var(--muted) !important;
    }

    /* Caption text */
    .stCaption {
        color: var(--muted) !important;
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# Plotly theme for warm colors
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': '#F6F1EA',
        'plot_bgcolor': '#FFFFFF',
        'font': {'family': 'Inter, sans-serif', 'color': '#121317'},
        'xaxis': {'gridcolor': '#EFE7DB', 'linecolor': '#E2D8C7'},
        'yaxis': {'gridcolor': '#EFE7DB', 'linecolor': '#E2D8C7'},
        'colorway': ['#121317', '#8A7650', '#2BB673', '#B9A98A', '#6C6A63'],
    }
}

# Sidebar
with st.sidebar:
    st.markdown("### Settings")
    days = st.slider("Time Range (days)", 1, 30, 1)

    st.markdown("---")

    if st.button("Refresh Recent Data"):
        clear_cache()
        st.rerun()

    if st.button("Refresh All-Time Totals"):
        save_alltime_cache({})
        st.cache_data.clear()
        clear_cache()
        st.rerun()

    st.markdown("---")
    st.markdown("**Contracts**")
    st.code(f"wNLP: {CONTRACTS['wNLP'][:10]}...", language=None)
    st.code(f"nHYPE: {CONTRACTS['nHYPE'][:10]}...", language=None)

    st.markdown("---")
    st.markdown("**Links**")
    st.markdown("[Nunchi](https://nunchi.trade) | [Docs](https://docs.nunchi.trade)")

# Top bar header
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f"""
<div class="top-bar">
    <div class="top-bar-inner">
        <div class="brand">
            <span class="brand-name">NUNCHI</span>
            <span class="brand-sub">STATS</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load all data with error handling
try:
    apy_data = get_pendle_apy()
except Exception as e:
    st.warning(f"Failed to load Pendle APY: {e}")
    apy_data = {}

try:
    accurate_tvl = get_accurate_tvl()
except Exception as e:
    st.warning(f"Failed to load TVL: {e}")
    accurate_tvl = {'wNLP_tvl': 0, 'SY_tvl': 0, 'nHYPE_tvl': 0}

with st.spinner("Loading data..."):
    try:
        alltime_totals = get_alltime_totals_hyperscan()
    except Exception as e:
        st.warning(f"Failed to load all-time totals: {e}")
        alltime_totals = {}

    try:
        alltime_pendle = get_alltime_pendle_markets()
    except Exception as e:
        st.warning(f"Failed to load Pendle markets: {e}")
        alltime_pendle = {}

    try:
        pendle_peak_tvls = get_pendle_peak_tvls()
    except Exception as e:
        pendle_peak_tvls = {}

    try:
        kpis = get_kpi_summary(days)
    except Exception as e:
        kpis = {}

    try:
        hip3_volumes = get_hip3_volumes()
    except Exception as e:
        hip3_volumes = {}

    try:
        testnet_data = get_testnet_analytics()
    except Exception as e:
        st.warning(f"Failed to load testnet data: {e}")
        testnet_data = {}

# Main tabs - matching design mockup
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Yield Tokenization", "HIP-3 Liquidity", "HIP-3 Staking", "Testnet (Proxy)"])

# ============== TAB 1: OVERVIEW ==============
with tab1:
    st.markdown("## Overview")
    st.markdown('<p class="muted-text">Protocol-wide metrics across all Nunchi products.</p>', unsafe_allow_html=True)

    # Current TVL row
    st.markdown("### Current TVL")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("NLP TVL", f"${accurate_tvl['wNLP_tvl']:,.0f}", help="Stablecoin vault TVL")

    with col2:
        st.metric("nHYPE TVL", f"{accurate_tvl['nHYPE_tvl']:,.0f} HYPE", help="nHYPE vault TVL")

    with col3:
        st.metric("PENDLE SY TVL", f"{accurate_tvl['SY_tvl']:,.0f}", help="SY wrappers from nLP flows")

    with col4:
        pendle_tvl_usd = sum(info['tvl_usd'] for info in apy_data.values()) if apy_data else 0
        st.metric("PENDLE TVL (USD)", f"${pendle_tvl_usd:,.0f}", help="TVL in Pendle markets")

    st.markdown("---")

    # All-time totals
    st.markdown("### All-Time Totals")
    st.markdown('<p class="muted-text">Since contract deployment on HyperEVM.</p>', unsafe_allow_html=True)

    if alltime_totals and 'wNLP' in alltime_totals:
        wNLP = alltime_totals['wNLP']
        SY = alltime_totals['SY_wNLP']

        # Calculate user counts
        nlp_depositors = wNLP.get('unique_users', 0)

        # Get Pendle users across both pools
        pendle_users_total = 0
        if alltime_pendle:
            for market_name, stats in alltime_pendle.items():
                if market_name != 'timestamp':
                    pendle_users_total += stats.get('unique_users', 0)

        # Get testnet + simulator users
        testnet_users = 0
        if testnet_data:
            testnet_users = testnet_data.get('totals', {}).get('total_users', 0)

        # Total unique users = NLP + Pendle + Testnet/Simulator
        total_unique = nlp_depositors + pendle_users_total + testnet_users

        # Row 1: Users
        col_u1, col_u2, col_u3, col_u4 = st.columns(4)
        with col_u1:
            st.metric("TOTAL UNIQUE USERS", f"{total_unique:,}", help="NLP + Pendle + Testnet users")
        with col_u2:
            st.metric("NLP DEPOSITORS", f"{nlp_depositors:,}", help="Vault depositors")
        with col_u3:
            st.metric("PENDLE USERS", f"{pendle_users_total:,}", help="Users across both pools")
        with col_u4:
            st.metric("TESTNET USERS", f"{testnet_users:,}", help="Simulator + S1 + S2 users")

        # Row 2: nLP metrics
        st.markdown("#### nLP Metrics")
        col_n1, col_n2, col_n3, col_n4 = st.columns(4)
        with col_n1:
            st.metric("NLP DEPOSITS", f"${wNLP['deposits']:,.0f}")
        with col_n2:
            st.metric("NLP WITHDRAWALS", f"${wNLP['withdrawals']:,.0f}")
        with col_n3:
            st.metric("NLP VOLUME", f"${wNLP['volume']:,.0f}")
        with col_n4:
            st.metric("NLP TRANSFERS", f"{wNLP['transfer_count']:,}")

        # Row 3: Pendle metrics
        st.markdown("#### Pendle Metrics")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            st.metric("PENDLE DEPOSITS", f"${SY['deposits']:,.0f}")
        with col_p2:
            st.metric("PENDLE WITHDRAWALS", f"${SY['withdrawals']:,.0f}")
        with col_p3:
            st.metric("PENDLE VOLUME", f"${SY['volume']:,.0f}")
        with col_p4:
            st.metric("PENDLE TRANSFERS", f"{SY['transfer_count']:,}")

# ============== TAB 2: YIELD TOKENIZATION ==============
with tab2:
    st.markdown("## Yield Tokenization")
    st.markdown('<p class="muted-text">Pendle integration: yield tokenization (YT/PT/LP) for nLP.</p>', unsafe_allow_html=True)

    # APY metrics
    if apy_data:
        total_tvl = sum(info['tvl_usd'] for info in apy_data.values())
        total_daily_yield = sum(info['daily_yield'] for info in apy_data.values())

        if total_tvl > 0:
            avg_underlying_apy = sum(info['underlying_apy'] * info['tvl_usd'] for info in apy_data.values()) / total_tvl
            avg_implied_apy = sum(info['implied_apy'] * info['tvl_usd'] for info in apy_data.values()) / total_tvl
        else:
            avg_underlying_apy = 0
            avg_implied_apy = 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("PENDLE TVL", f"${total_tvl:,.0f}")
        with col2:
            st.metric("UNDERLYING APY", f"{avg_underlying_apy:.1f}%")
        with col3:
            st.metric("IMPLIED APY", f"{avg_implied_apy:.1f}%")
        with col4:
            st.metric("DAILY YIELD", f"${total_daily_yield:,.2f}")

    st.markdown("---")

    # Pendle Pools breakdown
    st.markdown("### Pendle Pools")

    if alltime_pendle and len(alltime_pendle) > 1:
        pool_names = [k for k in alltime_pendle.keys() if k != 'timestamp']
        pool_cols = st.columns(len(pool_names))

        for idx, market_name in enumerate(pool_names):
            stats = alltime_pendle[market_name]
            with pool_cols[idx]:
                is_expired = "Dec 2025" in market_name
                status_class = "pool-expired" if is_expired else "pool-active"
                status_text = "Expired" if is_expired else "Active"

                st.markdown(f"""
                <div style="margin-bottom: 8px;">
                    <strong style="font-size: 1.1rem;">{market_name}</strong>
                    <span class="{status_class}" style="margin-left: 8px;">{status_text}</span>
                </div>
                <div style="color: var(--muted); font-size: 13px; margin-bottom: 12px;">Expiry: {stats['expiry']}</div>
                """, unsafe_allow_html=True)

                if is_expired:
                    peak_tvl_data = pendle_peak_tvls.get(market_name, {}) if pendle_peak_tvls else {}
                    peak_tvl = peak_tvl_data.get('peak_tvl', 0) * 2
                    st.metric("ALL TIME TVL", f"${peak_tvl:,.0f}")
                else:
                    market_addr = stats.get('market_address', '').lower()
                    current_tvl = apy_data.get(market_addr, {}).get('tvl_usd', 0) if apy_data else 0
                    st.metric("TVL", f"${current_tvl:,.0f}")

                st.metric("SWAP COUNT", f"{stats['swap_count']:,}")
                st.metric("LP MINTS", f"{stats['mint_count']:,}")
                st.metric("LP BURNS", f"{stats['burn_count']:,}")
                st.metric("TOTAL EVENTS", f"{stats['total_events']:,}")
                st.metric("UNIQUE USERS", f"{stats['unique_users']:,}")

# ============== TAB 3: HIP-3 LIQUIDITY ==============
with tab3:
    st.markdown("## HIP-3 Liquidity")
    st.markdown('<p class="muted-text">nLP vault: stablecoin capital that underwrites market quality and feeds the system loop.</p>', unsafe_allow_html=True)

    # Hero cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("TVL (LIVE)", f"${accurate_tvl['wNLP_tvl']:,.0f}", help="USDC + USDT deposits")

    with col2:
        # Current APY from Pendle
        if apy_data:
            total_tvl = sum(info['tvl_usd'] for info in apy_data.values())
            if total_tvl > 0:
                avg_apy = sum(info['underlying_apy'] * info['tvl_usd'] for info in apy_data.values()) / total_tvl
            else:
                avg_apy = 0
            st.metric("CURRENT APY (EST.)", f"{avg_apy:.1f}%", help="Base + rewards")
        else:
            st.metric("CURRENT APY (EST.)", "N/A")

    with col3:
        if apy_data:
            daily_yield = sum(info['daily_yield'] for info in apy_data.values())
            st.metric("DAILY DISTRIBUTED", f"${daily_yield:,.2f}", help="7D average")
        else:
            st.metric("DAILY DISTRIBUTED", "$0")

    with col4:
        if apy_data:
            annual_yield = sum(info['annual_yield'] for info in apy_data.values())
            st.metric("TOTAL DISTRIBUTED", f"${annual_yield:,.0f}", help="All-time estimated")
        else:
            st.metric("TOTAL DISTRIBUTED", "$0")

    st.markdown("---")

    # Two column layout: Yield Profile + Vault Accounting
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### Yield Profile")
        st.markdown('<p class="muted-text">APY breakdown and trend.</p>', unsafe_allow_html=True)

        # APY pills
        if apy_data:
            total_tvl = sum(info['tvl_usd'] for info in apy_data.values())
            if total_tvl > 0:
                base_apy = sum(info['underlying_apy'] * info['tvl_usd'] for info in apy_data.values()) / total_tvl
                implied_apy = sum(info['implied_apy'] * info['tvl_usd'] for info in apy_data.values()) / total_tvl
            else:
                base_apy = 0
                implied_apy = 0

            st.markdown(f"""
            <div style="margin-bottom: 16px;">
                <span class="apy-pill"><span class="apy-pill-label">BASE</span><span class="apy-pill-value">{base_apy:.1f}%</span></span>
                <span class="apy-pill"><span class="apy-pill-label">IMPLIED</span><span class="apy-pill-value">{implied_apy:.1f}%</span></span>
                <span class="apy-pill" style="background: rgba(18,19,23,0.06);"><span class="apy-pill-label">TOTAL (EST.)</span><span class="apy-pill-value">{base_apy:.1f}%</span></span>
            </div>
            """, unsafe_allow_html=True)

        # APY Chart
        apy_history = get_apy_history(days)
        if not apy_history.empty:
            fig_apy = go.Figure()

            for market in apy_history['market'].unique():
                market_data = apy_history[apy_history['market'] == market]
                fig_apy.add_trace(go.Scatter(
                    x=market_data['timestamp'],
                    y=market_data['underlying_apy'],
                    mode='lines',
                    name=f'Underlying',
                    line=dict(width=3, color='#121317'),
                ))
                fig_apy.add_trace(go.Scatter(
                    x=market_data['timestamp'],
                    y=market_data['implied_apy'],
                    mode='lines',
                    name=f'Implied',
                    line=dict(width=2, color='#8A7650'),
                ))

            fig_apy.update_layout(
                paper_bgcolor='#FFFFFF',
                plot_bgcolor='#FFFFFF',
                font=dict(family='Inter, sans-serif', color='#121317'),
                xaxis=dict(gridcolor='#EFE7DB', linecolor='#E2D8C7', title=''),
                yaxis=dict(gridcolor='#EFE7DB', linecolor='#E2D8C7', title='APY (%)'),
                height=280,
                margin=dict(l=40, r=20, t=20, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                showlegend=True,
            )
            st.plotly_chart(fig_apy, use_container_width=True)

    with col_right:
        st.markdown("### Vault Accounting")
        st.markdown('<p class="muted-text">All-time event accounting.</p>', unsafe_allow_html=True)

        if alltime_totals and 'wNLP' in alltime_totals:
            wNLP = alltime_totals['wNLP']

            st.markdown(f"""
            <div class="data-row"><span class="data-label">Deposits</span><span class="data-value">${wNLP['deposits']:,.0f}</span></div>
            <div class="data-row"><span class="data-label">Withdrawals</span><span class="data-value">${wNLP['withdrawals']:,.0f}</span></div>
            <div class="data-row"><span class="data-label">Net deposits</span><span class="data-value">${wNLP['deposits'] - wNLP['withdrawals']:,.0f}</span></div>
            <div class="data-row"><span class="data-label">Transfers</span><span class="data-value">{wNLP['transfer_count']:,}</span></div>
            <div class="data-row"><span class="data-label">Unique users</span><span class="data-value">{wNLP['unique_users']:,}</span></div>
            """, unsafe_allow_html=True)

# ============== TAB 4: HIP-3 STAKING ==============
with tab4:
    st.markdown("## HIP-3 Staking")
    st.markdown('<p class="muted-text">nHYPE: liquid staking token for HYPE supporting the HIP-3 bond.</p>', unsafe_allow_html=True)

    # Hero cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("nHYPE TVL", f"{accurate_tvl['nHYPE_tvl']:,.0f} HYPE", help="Total HYPE staked")

    with col2:
        st.metric("nHYPE CONTRACT", CONTRACTS['nHYPE'][:18] + "...", help="nHYPE token address")

    with col3:
        # Placeholder for staking vault when available
        st.metric("STATUS", "Active", help="Staking is live")

    st.markdown("---")

    # Volume traded section
    st.markdown("### HIP-3 Volume Traded")
    st.markdown('<p class="muted-text">Hyperliquid testnet with mockUSDC.</p>', unsafe_allow_html=True)

    vol_col1, vol_col2, vol_col3 = st.columns(3)

    with vol_col1:
        vxx_vol = hip3_volumes.get('nunchi:VXX', {}).get('notional_volume', 0)
        st.metric("VXX VOLUME", f"${vxx_vol:,.0f}")

    with vol_col2:
        us3m_vol = hip3_volumes.get('nunchi:US3M', {}).get('notional_volume', 0)
        st.metric("US3M VOLUME", f"${us3m_vol:,.0f}")

    with vol_col3:
        total_vol = hip3_volumes.get('total_notional', 0)
        st.metric("TOTAL VOLUME", f"${total_vol:,.0f}")

# ============== TAB 5: TESTNET (PROXY) ==============
with tab5:
    st.markdown("## Testnet Analytics")
    st.markdown('<p class="muted-text">MegaETH & Monad testnet activity.</p>', unsafe_allow_html=True)

    if testnet_data:
        totals = testnet_data.get('totals', {})
        simulator = testnet_data.get('simulator', {})
        s1 = testnet_data.get('season_one', {})
        s2 = testnet_data.get('season_two', {})

        # Hero metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("TOTAL USERS", f"{totals.get('total_users', 0):,}")
        with col2:
            st.metric("TOTAL VOLUME", f"${totals.get('total_volume', 0):,.0f}")
        with col3:
            avg_vol = totals.get('total_volume', 0) / totals.get('total_users', 1) if totals.get('total_users', 0) > 0 else 0
            st.metric("AVG / USER", f"${avg_vol:,.0f}")

        st.markdown("---")

        # Simulator
        st.markdown("### Simulator")
        col_sim1, col_sim2, col_sim3 = st.columns(3)
        with col_sim1:
            st.metric("USERS", f"{simulator.get('total_users', 0):,}")
        with col_sim2:
            st.metric("VOLUME", f"${simulator.get('total_volume', 0):,.0f}")
        with col_sim3:
            st.metric("AVG / USER", f"${simulator.get('avg_volume_per_user', 0):,.0f}")

        st.markdown("---")

        # Season One & Two side by side
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.markdown("### Season One")
            s1_total = s1.get('total', {})
            st.metric("USERS", f"{s1_total.get('total_users', 0):,}")
            st.metric("VOLUME", f"${s1_total.get('total_volume', 0):,.0f}")
            st.metric("NET PROFIT", f"${s1_total.get('net_profit', 0):,.0f}")
            st.metric("AVG TIME TO CLOSE", s1_total.get('avg_time_to_close_formatted', 'N/A'))

            st.markdown("**By Chain:**")
            s1_chains = s1.get('by_chain', {})
            for chain_id, chain_data in s1_chains.items():
                st.markdown(f"- **{chain_data['name']}**: {chain_data['users']:,} users, ${chain_data['volume']:,.0f}")

            st.markdown("**Top Assets:**")
            s1_assets = s1.get('by_asset', {})
            sorted_assets = sorted(s1_assets.items(), key=lambda x: x[1]['volume'], reverse=True)[:5]
            for asset, data in sorted_assets:
                st.markdown(f"- **{asset}**: {data['users']:,} users, ${data['volume']:,.0f}")

        with col_s2:
            st.markdown("### Season Two")
            s2_total = s2.get('total', {})
            st.metric("USERS", f"{s2_total.get('total_users', 0):,}")
            st.metric("VOLUME", f"${s2_total.get('total_volume', 0):,.0f}")
            st.metric("NET PROFIT", f"${s2_total.get('net_profit', 0):,.0f}")
            st.metric("AVG TIME TO CLOSE", s2_total.get('avg_time_to_close_formatted', 'N/A'))

            st.markdown("**By Chain:**")
            s2_chains = s2.get('by_chain', {})
            for chain_id, chain_data in s2_chains.items():
                st.markdown(f"- **{chain_data['name']}**: {chain_data['users']:,} users, ${chain_data['volume']:,.0f}")

            st.markdown("**Top Assets:**")
            s2_assets = s2.get('by_asset', {})
            sorted_assets = sorted(s2_assets.items(), key=lambda x: x[1]['volume'], reverse=True)[:5]
            for asset, data in sorted_assets:
                st.markdown(f"- **{asset}**: {data['users']:,} users, ${data['volume']:,.0f}")

        st.markdown("---")

        # Season Comparison Table
        st.markdown("### Season Comparison")
        comparison_data = get_season_comparison()

        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            comparison_df = comparison_df[comparison_df['s1_volume'] + comparison_df['s2_volume'] > 0]
            comparison_df = comparison_df.sort_values('s2_volume', ascending=False)

            display_df = comparison_df[['asset', 's1_users', 's1_volume', 's2_users', 's2_volume', 'user_growth', 'volume_growth']].copy()
            display_df.columns = ['Asset', 'S1 Users', 'S1 Volume', 'S2 Users', 'S2 Volume', 'User Growth %', 'Vol Growth %']
            display_df['S1 Volume'] = display_df['S1 Volume'].apply(lambda x: f"${x:,.0f}")
            display_df['S2 Volume'] = display_df['S2 Volume'].apply(lambda x: f"${x:,.0f}")
            display_df['User Growth %'] = display_df['User Growth %'].apply(lambda x: f"{x:+.1f}%" if x != 0 else "New")
            display_df['Vol Growth %'] = display_df['Vol Growth %'].apply(lambda x: f"{x:+.1f}%" if x != 0 else "New")

            st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Chain Comparison
        st.markdown("### Chain Comparison")
        chain_col1, chain_col2 = st.columns(2)

        with chain_col1:
            st.markdown("**MegaETH (Chain 6342)**")
            mega_s1 = s1.get('by_chain', {}).get(6342, {'users': 0, 'volume': 0})
            mega_s2 = s2.get('by_chain', {}).get(6342, {'users': 0, 'volume': 0})
            st.metric("S1 Users", f"{mega_s1.get('users', 0):,}")
            st.metric("S1 Volume", f"${mega_s1.get('volume', 0):,.0f}")
            st.metric("S2 Users", f"{mega_s2.get('users', 0):,}")
            st.metric("S2 Volume", f"${mega_s2.get('volume', 0):,.0f}")

        with chain_col2:
            st.markdown("**Monad (Chain 10143)**")
            monad_s1 = s1.get('by_chain', {}).get(10143, {'users': 0, 'volume': 0})
            monad_s2 = s2.get('by_chain', {}).get(10143, {'users': 0, 'volume': 0})
            st.metric("S1 Users", f"{monad_s1.get('users', 0):,}")
            st.metric("S1 Volume", f"${monad_s1.get('volume', 0):,.0f}")
            st.metric("S2 Users", f"{monad_s2.get('users', 0):,}")
            st.metric("S2 Volume", f"${monad_s2.get('volume', 0):,.0f}")

    else:
        st.info("Testnet analytics data unavailable")

# Footer
st.markdown(f"""
<div class="footer">
    <p class="footer-text">
        Last updated: <span style="font-family: monospace;">{current_time}</span> ·
        Metrics sourced from on-chain events and vault accounting.
    </p>
    <div style="margin-top: 12px;">
        <a href="https://nunchi.trade" target="_blank" class="footer-link">Open app</a>
        <span style="color: var(--muted); margin: 0 8px;">·</span>
        <a href="https://docs.nunchi.trade" target="_blank" class="footer-link">Documentation</a>
    </div>
</div>
""", unsafe_allow_html=True)
