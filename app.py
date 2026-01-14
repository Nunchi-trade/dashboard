"""
Nunchi Analytics Dashboard
Real-time analytics for Nunchi (nunchi.trade) on HyperEVM
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

from data_fetcher import (
    get_kpi_summary,
    get_daily_pendle_deposits,
    get_daily_volume,
    get_nlp_tvl,
    get_daily_nlp_volume,
    get_top_holders,
    get_user_stats,
    get_pendle_swaps,
    get_pendle_lp_events,
    clear_cache,
)
from config import CONTRACTS

# Page config
st.set_page_config(
    page_title="Nunchi Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #0f3460;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #e94560;
    }
    .metric-label {
        color: #a0a0a0;
        font-size: 0.9rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #0f3460;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar
st.sidebar.title("⚙️ Settings")

days = st.sidebar.slider("Time Range (days)", 7, 90, 30)

if st.sidebar.button("🔄 Refresh Data"):
    clear_cache()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 Contracts")
st.sidebar.code(f"wNLP: {CONTRACTS['wNLP'][:10]}...")
st.sidebar.code(f"Pendle: {CONTRACTS['PENDLE_MARKET'][:10]}...")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Links")
st.sidebar.markdown("[Nunchi](https://nunchi.trade)")
st.sidebar.markdown("[Docs](https://docs.nunchi.trade)")
st.sidebar.markdown("[HyperEVMScan](https://hyperevmscan.io)")


# Main content
st.title("📊 Nunchi Analytics Dashboard")
st.markdown("*Real-time analytics for Nunchi on HyperEVM*")

# Load KPIs
with st.spinner("Loading data from HyperEVM..."):
    kpis = get_kpi_summary(days)

# KPI Cards
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total TVL (nLP)",
        value=f"${kpis['tvl']:,.2f}",
    )

with col2:
    st.metric(
        label="Volume (7d)",
        value=f"${kpis['volume_7d']:,.2f}",
    )

with col3:
    st.metric(
        label="Total Fees",
        value=f"${kpis['total_fees']:,.4f}",
    )

with col4:
    st.metric(
        label="Total Users",
        value=f"{kpis['total_users']:,}",
    )

with col5:
    st.metric(
        label="Pendle Deposits",
        value=f"${kpis['pendle_deposits']:,.2f}",
    )

st.markdown("---")

# Tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Pendle Deposits/Withdrawals",
    "📈 Pendle Volume",
    "💰 nLP TVL & Volume",
    "🏆 Top Holders",
    "👥 User Analytics"
])

# Tab 1: Pendle Deposits & Withdrawals
with tab1:
    st.subheader("Pendle Deposits & Withdrawals")

    deposits_df = get_daily_pendle_deposits(days)

    if not deposits_df.empty:
        # Create dual bar chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=deposits_df['date'],
            y=deposits_df['deposits'],
            name='Deposits',
            marker_color='#00d4aa',
        ))

        fig.add_trace(go.Bar(
            x=deposits_df['date'],
            y=deposits_df['withdrawals'],
            name='Withdrawals',
            marker_color='#ff6b6b',
        ))

        fig.update_layout(
            barmode='group',
            xaxis_title='Date',
            yaxis_title='Amount',
            template='plotly_dark',
            height=400,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Net flow chart
        st.subheader("Net Flow")
        fig_flow = px.area(
            deposits_df,
            x='date',
            y='net_flow',
            template='plotly_dark',
        )
        fig_flow.update_traces(
            fill='tonexty',
            line_color='#e94560',
        )
        st.plotly_chart(fig_flow, use_container_width=True)

        # Data table
        with st.expander("📋 View Raw Data"):
            st.dataframe(deposits_df, use_container_width=True)
    else:
        st.info("No deposit/withdrawal data found for the selected period.")

# Tab 2: Pendle Volume
with tab2:
    st.subheader("Pendle Trading Volume")

    volume_df = get_daily_volume(days)

    if not volume_df.empty:
        # Volume chart
        fig_vol = px.bar(
            volume_df,
            x='date',
            y='volume',
            template='plotly_dark',
            color_discrete_sequence=['#00d4aa'],
        )
        fig_vol.update_layout(
            xaxis_title='Date',
            yaxis_title='Volume',
            height=400,
        )
        st.plotly_chart(fig_vol, use_container_width=True)

        # Metrics row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Volume", f"${volume_df['volume'].sum():,.2f}")
        with col2:
            st.metric("Total Fees", f"${volume_df['fees'].sum():,.4f}")
        with col3:
            st.metric("Total Swaps", f"{volume_df['num_swaps'].sum():,}")

        # Cumulative volume
        st.subheader("Cumulative Volume")
        volume_df['cumulative'] = volume_df['volume'].cumsum()
        fig_cum = px.area(
            volume_df,
            x='date',
            y='cumulative',
            template='plotly_dark',
        )
        fig_cum.update_traces(fill='tonexty', line_color='#e94560')
        st.plotly_chart(fig_cum, use_container_width=True)

        # Fees chart
        st.subheader("Daily Fees Collected")
        fig_fees = px.bar(
            volume_df,
            x='date',
            y='fees',
            template='plotly_dark',
            color_discrete_sequence=['#ffd93d'],
        )
        st.plotly_chart(fig_fees, use_container_width=True)

        with st.expander("📋 View Raw Data"):
            st.dataframe(volume_df, use_container_width=True)
    else:
        st.info("No trading volume data found for the selected period.")

# Tab 3: nLP TVL & Volume
with tab3:
    st.subheader("nLP Total Value Locked")

    tvl_df = get_nlp_tvl(days)
    nlp_vol_df = get_daily_nlp_volume(days)

    if not tvl_df.empty:
        # TVL Chart
        fig_tvl = px.area(
            tvl_df,
            x='date',
            y='tvl',
            template='plotly_dark',
        )
        fig_tvl.update_traces(fill='tonexty', line_color='#00d4aa')
        fig_tvl.update_layout(
            xaxis_title='Date',
            yaxis_title='TVL',
            height=400,
        )
        st.plotly_chart(fig_tvl, use_container_width=True)

        # Daily changes
        st.subheader("Daily Net Changes")
        fig_changes = px.bar(
            tvl_df,
            x='date',
            y='daily_change',
            template='plotly_dark',
            color='daily_change',
            color_continuous_scale=['#ff6b6b', '#ffd93d', '#00d4aa'],
        )
        st.plotly_chart(fig_changes, use_container_width=True)

    if not nlp_vol_df.empty:
        st.subheader("nLP Transfer Volume")
        fig_nlp_vol = px.bar(
            nlp_vol_df,
            x='date',
            y='volume',
            template='plotly_dark',
            color_discrete_sequence=['#6c5ce7'],
        )
        st.plotly_chart(fig_nlp_vol, use_container_width=True)

    if tvl_df.empty and nlp_vol_df.empty:
        st.info("No nLP data found for the selected period.")

# Tab 4: Top Holders
with tab4:
    st.subheader("Top nLP Holders")

    holders_df = get_top_holders(90)  # Look back 90 days for holder data

    if not holders_df.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            # Holders table
            st.dataframe(
                holders_df.style.format({
                    'balance': '{:,.2f}',
                    'pct_supply': '{:.2f}%',
                }),
                use_container_width=True,
                height=500,
            )

        with col2:
            # Pie chart
            top_10 = holders_df.head(10).copy()
            other_pct = 100 - top_10['pct_supply'].sum()
            if other_pct > 0:
                top_10 = pd.concat([
                    top_10,
                    pd.DataFrame([{'holder': 'Others', 'balance': 0, 'pct_supply': other_pct}])
                ])

            fig_pie = px.pie(
                top_10,
                values='pct_supply',
                names='holder',
                template='plotly_dark',
                hole=0.4,
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent')
            fig_pie.update_layout(showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No holder data found.")

# Tab 5: User Analytics
with tab5:
    st.subheader("User Analytics")

    users_df = get_user_stats(days)

    if not users_df.empty:
        # Daily active users
        fig_users = px.line(
            users_df,
            x='date',
            y='daily_users',
            template='plotly_dark',
            markers=True,
        )
        fig_users.update_traces(line_color='#e94560')
        fig_users.update_layout(
            xaxis_title='Date',
            yaxis_title='Daily Active Users',
            height=400,
        )
        st.plotly_chart(fig_users, use_container_width=True)

        # Product breakdown
        st.subheader("Users by Product")

        fig_product = go.Figure()
        fig_product.add_trace(go.Bar(
            x=users_df['date'],
            y=users_df['nlp_users'],
            name='nLP Users',
            marker_color='#00d4aa',
        ))
        fig_product.add_trace(go.Bar(
            x=users_df['date'],
            y=users_df['pendle_users'],
            name='Pendle Users',
            marker_color='#6c5ce7',
        ))
        fig_product.update_layout(
            barmode='stack',
            template='plotly_dark',
            xaxis_title='Date',
            yaxis_title='Users',
        )
        st.plotly_chart(fig_product, use_container_width=True)

        # Cumulative users
        st.subheader("Cumulative Unique Users")
        users_df['cumulative_users'] = users_df['daily_users'].cumsum()
        fig_cum_users = px.area(
            users_df,
            x='date',
            y='cumulative_users',
            template='plotly_dark',
        )
        fig_cum_users.update_traces(fill='tonexty', line_color='#ffd93d')
        st.plotly_chart(fig_cum_users, use_container_width=True)
    else:
        st.info("No user data found for the selected period.")


# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Data sourced directly from HyperEVM RPC | Built with Streamlit</p>
        <p><a href='https://nunchi.trade' target='_blank'>nunchi.trade</a></p>
    </div>
    """,
    unsafe_allow_html=True,
)
