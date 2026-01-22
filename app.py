"""
Nunchi Analytics Dashboard
Real-time analytics for Nunchi (nunchi.trade) on HyperEVM
Styled with Nunchi brand design
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

# Page config
st.set_page_config(
    page_title="Nunchi Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Nunchi Brand CSS - Warm paper theme
st.markdown("""
<style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* CSS Variables - Nunchi Brand Tokens */
    :root {
        --bg: #F6F1EA;
        --panel: #FBF8F3;
        --ink: #111111;
        --muted: #6F6A62;
        --line: #D9CDBB;
        --line2: #E7DED1;
        --accent: #8A7B5B;
        --accent2: #B9A98A;
        --green: #2BB673;
    }

    /* Main app background */
    .stApp {
        background-color: var(--bg) !important;
    }

    .main .block-container {
        background-color: var(--bg) !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1800px;
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
        font-size: 3.2rem !important;
        margin-bottom: 0.5rem !important;
    }

    h2, .stSubheader {
        font-size: 1.6rem !important;
        letter-spacing: -0.2px;
    }

    p, span, div, label {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, sans-serif !important;
        color: var(--ink);
    }

    /* Muted text */
    .muted-text {
        color: var(--muted) !important;
        font-size: 1rem;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: var(--panel) !important;
        border: 1.5px solid var(--line) !important;
        border-radius: 18px !important;
        padding: 20px 22px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06) !important;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08) !important;
        border-color: var(--accent2) !important;
    }

    [data-testid="stMetricLabel"] {
        font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        letter-spacing: 0.3px !important;
        text-transform: uppercase !important;
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        font-family: Inter, ui-sans-serif, system-ui, sans-serif !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
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
        height: 2px !important;
        background: linear-gradient(90deg,
            rgba(217, 205, 187, 0) 0%,
            rgba(217, 205, 187, 1) 15%,
            rgba(217, 205, 187, 1) 85%,
            rgba(217, 205, 187, 0) 100%) !important;
        margin: 2rem 0 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent !important;
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: var(--panel) !important;
        border: 1.5px solid var(--line) !important;
        border-radius: 18px !important;
        color: var(--muted) !important;
        font-family: Inter, sans-serif !important;
        font-weight: 500 !important;
        padding: 8px 20px !important;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: var(--panel) !important;
        border-color: var(--accent) !important;
        color: var(--ink) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: var(--panel) !important;
        border: 1px solid var(--line) !important;
        border-radius: 12px !important;
        color: var(--ink) !important;
        font-family: Inter, sans-serif !important;
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

    /* Spinner */
    .stSpinner > div {
        border-color: var(--accent) transparent transparent transparent !important;
    }

    /* Slider */
    .stSlider [data-baseweb="slider"] {
        background-color: var(--line) !important;
    }

    .stSlider [data-testid="stThumbValue"] {
        color: var(--ink) !important;
    }

    /* Caption text */
    .stCaption {
        color: var(--muted) !important;
        font-size: 12px !important;
    }

    /* Custom header styles */
    .nunchi-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .nunchi-brand {
        font-family: Inter, sans-serif;
        font-size: 18px;
        letter-spacing: 4px;
        color: var(--ink);
        font-weight: 600;
    }

    .nunchi-brand-sub {
        font-family: Inter, sans-serif;
        font-size: 14px;
        letter-spacing: 2px;
        color: var(--muted);
        margin-left: 8px;
    }

    .live-pill {
        display: inline-flex;
        align-items: center;
        background: var(--panel);
        border: 1.2px solid var(--line);
        border-radius: 18px;
        padding: 8px 16px;
        font-family: Inter, sans-serif;
        font-size: 13px;
        color: var(--ink);
    }

    .live-dot {
        width: 10px;
        height: 10px;
        background: #2BB673;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1rem;
    }

    .section-icon {
        width: 18px;
        height: 18px;
        border: 1.5px solid var(--line);
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 16px;
        margin-left: 8px;
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

    /* Footer links */
    .footer-link {
        color: var(--accent) !important;
        text-decoration: none;
        font-size: 13px;
        font-family: Inter, sans-serif;
    }

    .footer-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# Plotly theme for warm colors
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': '#F6F1EA',
        'plot_bgcolor': '#FBF8F3',
        'font': {'family': 'Inter, sans-serif', 'color': '#111111'},
        'xaxis': {'gridcolor': '#E7DED1', 'linecolor': '#D9CDBB'},
        'yaxis': {'gridcolor': '#E7DED1', 'linecolor': '#D9CDBB'},
        'colorway': ['#8A7B5B', '#B9A98A', '#2BB673', '#D9CDBB', '#6F6A62'],
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
    st.code(f"SY: {CONTRACTS['SY_wNLP'][:10]}...", language=None)

    st.markdown("---")
    st.markdown("**Links**")
    st.markdown("[Nunchi](https://nunchi.trade) | [Docs](https://docs.nunchi.trade)")

# Custom header
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f"""
<div class="nunchi-header">
    <div>
        <span class="nunchi-brand">NUNCHI</span>
        <span class="nunchi-brand-sub">ANALYTICS</span>
    </div>
    <div style="display: flex; gap: 12px; align-items: center;">
        <div class="live-pill">
            <div class="live-dot"></div>
            Live
        </div>
        <div class="live-pill">
            <span style="color: var(--muted); margin-right: 8px;">Last updated</span>
            {current_time}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main title
st.title("Nunchi Analytics Dashboard")
st.markdown('<p class="muted-text">Real-time protocol stats for nLP, Pendle integrations, and on-chain activity.</p>', unsafe_allow_html=True)

# Load data
apy_data = get_pendle_apy()
accurate_tvl = get_accurate_tvl()

with st.spinner("Loading all-time totals..."):
    alltime_totals = get_alltime_totals_hyperscan()
    alltime_pendle = get_alltime_pendle_markets()
    pendle_peak_tvls = get_pendle_peak_tvls()

with st.spinner(f"Loading {days} day(s) of recent data..."):
    kpis = get_kpi_summary(days)

# Section: Current TVL
st.markdown("---")
st.markdown("""
<div class="section-header">
    <svg class="section-icon" width="18" height="18" viewBox="0 0 18 18"><rect x="0" y="0" width="18" height="18" rx="4" fill="none" stroke="#D9CDBB" stroke-width="1.5"/><path d="M4 12 L8 9 L11 11 L14 6" fill="none" stroke="#8A7B5B" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="14" cy="6" r="1.6" fill="#8A7B5B"/></svg>
    <h2 style="margin: 0;">Current TVL</h2>
    <span class="section-subtitle">(Live from blockchain)</span>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="NLP TVL",
        value=f"${accurate_tvl['wNLP_tvl']:,.2f}",
        help="Stablecoin vault TVL"
    )

with col2:
    st.metric(
        label="nHYPE TVL",
        value=f"{accurate_tvl['nHYPE_tvl']:,.2f} HYPE",
        help="nHYPE vault TVL"
    )

with col3:
    st.metric(
        label="PENDLE SY TVL",
        value=f"{accurate_tvl['SY_tvl']:,.2f}",
        help="SY wrappers from nLP flows"
    )

with col4:
    pendle_tvl_usd = sum(info['tvl_usd'] for info in apy_data.values()) if apy_data else 0
    st.metric(
        label="PENDLE TVL (USD)",
        value=f"${pendle_tvl_usd:,.2f}",
        help="TVL in Pendle markets"
    )

# Section: Volume Traded
st.markdown("---")
st.markdown("""
<div class="section-header">
    <svg class="section-icon" width="18" height="18" viewBox="0 0 18 18"><rect x="0" y="0" width="18" height="18" rx="4" fill="none" stroke="#D9CDBB" stroke-width="1.5"/><path d="M4 12 L8 9 L11 11 L14 6" fill="none" stroke="#8A7B5B" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="14" cy="6" r="1.6" fill="#8A7B5B"/></svg>
    <h2 style="margin: 0;">Volume Traded</h2>
    <span class="section-subtitle">(Hyperliquid testnet with mockUSDC)</span>
</div>
""", unsafe_allow_html=True)

hip3_volumes = get_hip3_volumes()

vol_col1, vol_col2, vol_col3 = st.columns(3)

with vol_col1:
    vxx_vol = hip3_volumes.get('nunchi:VXX', {}).get('notional_volume', 0)
    st.metric(
        label="VXX VOLUME",
        value=f"${vxx_vol:,.2f}",
        help="All-time notional volume for nunchi:VXX"
    )

with vol_col2:
    us3m_vol = hip3_volumes.get('nunchi:US3M', {}).get('notional_volume', 0)
    st.metric(
        label="US3M VOLUME",
        value=f"${us3m_vol:,.2f}",
        help="All-time notional volume for nunchi:US3M"
    )

with vol_col3:
    total_vol = hip3_volumes.get('total_notional', 0)
    st.metric(
        label="TOTAL VOLUME",
        value=f"${total_vol:,.2f}",
        help="Combined all-time volume across both pairs"
    )

# Section: All-Time Totals
st.markdown("---")
st.markdown("""
<div class="section-header">
    <svg class="section-icon" width="18" height="18" viewBox="0 0 18 18"><rect x="0" y="0" width="18" height="18" rx="4" fill="none" stroke="#D9CDBB" stroke-width="1.5"/><path d="M4 12 L8 9 L11 11 L14 6" fill="none" stroke="#8A7B5B" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="14" cy="6" r="1.6" fill="#8A7B5B"/></svg>
    <h2 style="margin: 0;">All-Time Totals</h2>
    <span class="section-subtitle">(Since contract deployment)</span>
</div>
""", unsafe_allow_html=True)

if alltime_totals and 'wNLP' in alltime_totals:
    wNLP = alltime_totals['wNLP']
    SY = alltime_totals['SY_wNLP']

    # Row 1: Users
    col_u1, col_u2, col_u3, col_u4 = st.columns(4)
    with col_u1:
        st.metric(
            label="TOTAL UNIQUE USERS",
            value=f"{alltime_totals.get('total_unique_users', 0):,}",
            help="Distinct wallets interacted"
        )
    with col_u2:
        st.metric(
            label="NLP USERS",
            value=f"{wNLP.get('unique_users', 0):,}",
            help="Vault depositors / holders"
        )
    with col_u3:
        st.metric(
            label="PENDLE USERS",
            value=f"{SY.get('unique_users', 0):,}",
            help="Users via Pendle routes"
        )
    with col_u4:
        st.metric(
            label="TOTAL TRANSACTIONS",
            value=f"{wNLP['transfer_count'] + SY['transfer_count']:,}",
            help="All contracts aggregated"
        )

    # Row 2: nLP metrics
    col_n1, col_n2, col_n3, col_n4 = st.columns(4)
    with col_n1:
        st.metric(
            label="NLP DEPOSITS",
            value=f"${wNLP['deposits']:,.2f}",
            help="Cumulative deposits"
        )
    with col_n2:
        st.metric(
            label="NLP WITHDRAWALS",
            value=f"${wNLP['withdrawals']:,.2f}",
            help="Cumulative withdrawals"
        )
    with col_n3:
        st.metric(
            label="NLP VOLUME",
            value=f"${wNLP['volume']:,.2f}",
            help="Transfers + internal flows"
        )
    with col_n4:
        st.metric(
            label="NLP TRANSFERS",
            value=f"{wNLP['transfer_count']:,}",
            help="Token movements"
        )

    # Row 3: Pendle metrics
    col_p1, col_p2, col_p3, col_p4 = st.columns(4)
    with col_p1:
        st.metric(
            label="PENDLE DEPOSITS",
            value=f"${SY['deposits']:,.2f}",
            help="Deposits into Pendle markets"
        )
    with col_p2:
        st.metric(
            label="PENDLE WITHDRAWALS",
            value=f"${SY['withdrawals']:,.2f}",
            help="Withdrawals from Pendle"
        )
    with col_p3:
        st.metric(
            label="PENDLE VOLUME",
            value=f"${SY['volume']:,.2f}",
            help="SY/PT/YT related volume"
        )
    with col_p4:
        st.metric(
            label="PENDLE TRANSFERS",
            value=f"{SY['transfer_count']:,}",
            help="Pendle token movements"
        )

    if 'timestamp' in alltime_totals:
        st.caption(f"Last updated: {alltime_totals['timestamp']}")
else:
    st.info("All-time data loading... Click 'Refresh All-Time Totals' in sidebar.")

# Section: APY & Yield
st.markdown("---")
st.markdown("""
<div class="section-header">
    <svg class="section-icon" width="18" height="18" viewBox="0 0 18 18"><rect x="0" y="0" width="18" height="18" rx="4" fill="none" stroke="#D9CDBB" stroke-width="1.5"/><path d="M4 12 L8 9 L11 11 L14 6" fill="none" stroke="#8A7B5B" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="14" cy="6" r="1.6" fill="#8A7B5B"/></svg>
    <h2 style="margin: 0;">APY & Distributed Yield</h2>
</div>
""", unsafe_allow_html=True)

if apy_data:
    total_tvl = sum(info['tvl_usd'] for info in apy_data.values())
    total_daily_yield = sum(info['daily_yield'] for info in apy_data.values())
    total_annual_yield = sum(info['annual_yield'] for info in apy_data.values())

    if total_tvl > 0:
        avg_underlying_apy = sum(info['underlying_apy'] * info['tvl_usd'] for info in apy_data.values()) / total_tvl
        avg_implied_apy = sum(info['implied_apy'] * info['tvl_usd'] for info in apy_data.values()) / total_tvl
    else:
        avg_underlying_apy = 0
        avg_implied_apy = 0

    col_y1, col_y2, col_y3, col_y4 = st.columns(4)
    with col_y1:
        st.metric("UNDERLYING APY", f"{avg_underlying_apy:.1f}%", help="TVL-weighted average yield")
    with col_y2:
        st.metric("IMPLIED APY", f"{avg_implied_apy:.1f}%", help="PT discount rate")
    with col_y3:
        st.metric("DAILY YIELD", f"${total_daily_yield:,.2f}")
    with col_y4:
        st.metric("ANNUAL YIELD", f"${total_annual_yield:,.2f}")

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
                name=f'{market} - Underlying',
                line=dict(width=2, color='#8A7B5B'),
            ))
            fig_apy.add_trace(go.Scatter(
                x=market_data['timestamp'],
                y=market_data['implied_apy'],
                mode='lines',
                name=f'{market} - Implied',
                line=dict(width=2, dash='dash', color='#B9A98A'),
            ))

        fig_apy.update_layout(
            paper_bgcolor='#F6F1EA',
            plot_bgcolor='#FBF8F3',
            font=dict(family='Inter, sans-serif', color='#111111'),
            xaxis=dict(gridcolor='#E7DED1', linecolor='#D9CDBB', title='Date'),
            yaxis=dict(gridcolor='#E7DED1', linecolor='#D9CDBB', title='APY (%)'),
            height=350,
            margin=dict(l=40, r=40, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_apy, use_container_width=True)
else:
    st.info("APY data unavailable")

# Section: Pendle Pools
st.markdown("---")
st.markdown("""
<div class="section-header">
    <svg class="section-icon" width="18" height="18" viewBox="0 0 18 18"><rect x="0" y="0" width="18" height="18" rx="4" fill="none" stroke="#D9CDBB" stroke-width="1.5"/><path d="M4 12 L8 9 L11 11 L14 6" fill="none" stroke="#8A7B5B" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="14" cy="6" r="1.6" fill="#8A7B5B"/></svg>
    <h2 style="margin: 0;">Pendle Pools Breakdown</h2>
    <span class="section-subtitle">(All-time stats)</span>
</div>
""", unsafe_allow_html=True)

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

            # For expired pool: show all-time peak TVL (×2 for LP value)
            # For active pool: show current TVL from Pendle API
            if is_expired:
                peak_tvl_data = pendle_peak_tvls.get(market_name, {}) if pendle_peak_tvls else {}
                peak_tvl = peak_tvl_data.get('peak_tvl', 0) * 2  # Multiply by 2 for LP value
                st.metric("ALL TIME TVL", f"${peak_tvl:,.2f}")
            else:
                market_addr = stats.get('market_address', '').lower()
                current_tvl = apy_data.get(market_addr, {}).get('tvl_usd', 0) if apy_data else 0
                st.metric("TVL", f"${current_tvl:,.2f}")

            st.metric("SWAP COUNT", f"{stats['swap_count']:,}")
            st.metric("LP MINTS", f"{stats['mint_count']:,}")
            st.metric("LP BURNS", f"{stats['burn_count']:,}")
            st.metric("TOTAL EVENTS", f"{stats['total_events']:,}")
            st.metric("UNIQUE USERS", f"{stats['unique_users']:,}")
else:
    st.info("Loading pool data...")

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 1rem 0;">
    <p style="color: var(--muted); font-size: 12px; margin-bottom: 12px;">
        Metrics sourced from on-chain events and vault accounting.
    </p>
    <div style="display: flex; justify-content: center; gap: 16px;">
        <a href="https://nunchi.trade" target="_blank" class="footer-link">Open app</a>
        <span style="color: var(--muted);">•</span>
        <a href="https://docs.nunchi.trade" target="_blank" class="footer-link">Documentation</a>
        <span style="color: var(--muted);">•</span>
        <a href="https://hyperscan.com" target="_blank" class="footer-link">HyperScan</a>
    </div>
</div>
""", unsafe_allow_html=True)
