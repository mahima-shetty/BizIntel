# streamlit_ui/pages/Peer Comparison.py

import streamlit as st
import plotly.express as px
from app.agents.peer_comparison_agent import (
    get_peer_comparison,
    get_formatted_peer_df,
)

st.set_page_config(page_title="Peer Comparison", layout="wide")
st.title("📊 Peer Comparison Dashboard")

# Initialize session ticker
if "ticker" not in st.session_state:
    st.session_state["ticker"] = "AAPL"

# Ticker input box linked to session state
ticker = st.text_input("Enter Ticker", value=st.session_state["ticker"]).upper()
st.session_state["ticker"] = ticker  # update in session

available_metrics = [
    "Market Cap",
    "P/E Ratio",
    "EPS",
    "Revenue (TTM)",
    "Net Income (TTM)",
    "Return on Equity"
]

selected_metrics = st.multiselect(
    "Select Metrics to Compare",
    available_metrics,
    default=["Market Cap", "Return on Equity"]
)

sort_by = st.selectbox("Sort peers by", available_metrics)

if st.button("Compare Peers"):
    with st.spinner("🔍 Fetching peer data..."):
        raw_df = get_peer_comparison(ticker, sort_by)

        if raw_df.empty:
            st.warning("⚠️ No peer data found for this ticker.")
        else:
            st.subheader("📋 Comparison Table")
            formatted_df = get_formatted_peer_df(raw_df)
            st.dataframe(formatted_df, use_container_width=True)

            # Prepare for chart
            st.subheader("📊 Side-by-Side Metric Comparison")

            chart_df = raw_df[["Ticker"] + selected_metrics].copy()
            chart_df = chart_df.dropna(subset=selected_metrics)

            for metric in selected_metrics:
                if metric == "Return on Equity":
                    chart_df[metric] = chart_df[metric].apply(
                        lambda x: x * 100 if isinstance(x, (float, int)) else None
                    )
                elif "Cap" in metric or "Revenue" in metric or "Income" in metric:
                    chart_df[metric] = chart_df[metric].apply(
                        lambda x: x / 1e9 if isinstance(x, (float, int)) else None
                    )

            long_df = chart_df.melt(
                id_vars="Ticker", var_name="Metric", value_name="Value"
            )

            fig = px.bar(
                long_df,
                x="Ticker",
                y="Value",
                color="Metric",
                barmode="group",
                text=long_df["Value"].round(2),
                title="📊 Peer Comparison by Selected Metrics",
                template="plotly_white",
                height=500
            )
            fig.update_layout(
                yaxis_title="Value (B = Billion or %)",
                xaxis_title="Company Ticker",
                legend_title="Metric"
            )
            st.plotly_chart(fig, use_container_width=True)
