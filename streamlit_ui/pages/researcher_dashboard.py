# streamlit_ui/pages/researcher_dashboard.py

import streamlit as st
from streamlit_ui.utils.researcher_prefs import load_researcher_prefs, save_researcher_prefs
from streamlit_ui.components.sidebar import render_sidebar
from app.agents.deep_dive_agent import company_deep_dive
from app.agents.peer_comparison_agent import get_peer_comparison, get_formatted_peer_df
import plotly.express as px

# ─────────────────────────────────────────────
def load_user_preferences(email):
    prefs = load_researcher_prefs(email)
    if not prefs:
        prefs = {"ticker": "AAPL", "depth": "standard"}
        st.warning("⚠️ No researcher preferences found. Using defaults.")
    return prefs

# ─────────────────────────────────────────────
def show_company_deep_dive_section(prefs):
    st.subheader("🏢 Company Deep Dive")

    ticker = st.text_input("Enter Ticker Symbol", prefs.get("ticker", "AAPL")).upper()
    prefs["ticker"] = ticker

    if st.button("🔍 Run Deep Dive"):
        with st.spinner(f"Generating deep dive for {ticker}..."):
            result = company_deep_dive(ticker)
            st.session_state["deep_dive_result"] = result
            st.session_state["deep_dive_ticker"] = ticker
            st.success("✅ Done! Business model and strategy ready.")

    if "deep_dive_result" in st.session_state:
        st.markdown(st.session_state["deep_dive_result"])

        if st.session_state.get("deep_dive_ticker") == ticker:
            st.markdown("---")
            show_peer_comparison_section(ticker)

# ─────────────────────────────────────────────
def show_peer_comparison_section(ticker: str):
    st.subheader("📊 Peer Comparison")

    available_metrics = [
        "Market Cap", "P/E Ratio", "EPS",
        "Revenue (TTM)", "Net Income (TTM)", "Return on Equity"
    ]

    selected_metrics = st.multiselect(
        "Select Metrics to Compare", available_metrics,
        default=["Market Cap", "Return on Equity"]
    )

    sort_by = st.selectbox("Sort peers by", available_metrics)

    if st.button("🔁 Refresh Peer Data") or st.session_state.get("last_peer_ticker") != ticker:
        with st.spinner(f"Fetching peer data for {ticker}..."):
            raw_df = get_peer_comparison(ticker, sort_by)
            st.session_state["peer_df_raw"] = raw_df
            st.session_state["peer_df_formatted"] = get_formatted_peer_df(raw_df)
            st.session_state["last_peer_ticker"] = ticker

    if "peer_df_formatted" in st.session_state:
        st.markdown("### 📋 Peer Comparison Table")
        st.dataframe(st.session_state["peer_df_formatted"], use_container_width=True)

        if selected_metrics:
            st.markdown("### 📊 Multi-Metric Bar Chart")
            raw_df = st.session_state["peer_df_raw"]
            chart_df = raw_df[["Ticker"] + selected_metrics].dropna()

            for metric in selected_metrics:
                if metric == "Return on Equity":
                    chart_df[metric] = chart_df[metric] * 100
                elif "Cap" in metric or "Revenue" in metric or "Income" in metric:
                    chart_df[metric] = chart_df[metric] / 1e9

            long_df = chart_df.melt(id_vars="Ticker", var_name="Metric", value_name="Value")

            fig = px.bar(
                long_df, x="Ticker", y="Value", color="Metric",
                barmode="group", text=long_df["Value"].round(2),
                title="Peer Metric Comparison", template="plotly_white", height=500
            )
            fig.update_layout(yaxis_title="Value (normalized)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ Select at least one metric to render the chart.")

# ─────────────────────────────────────────────
def show_researcher_preferences_form(prefs):
    st.markdown("## ⚙️ Research Preferences")

    with st.form("update_researcher_prefs"):
        ticker = st.text_input("Default Ticker", prefs.get("ticker", "AAPL"))
        depth = st.selectbox("Depth of Analysis", ["standard", "deep"], index=0)
        submitted = st.form_submit_button("💾 Save Preferences")
        if submitted:
            return {"ticker": ticker, "depth": depth}
    return None

# ─────────────────────────────────────────────
def show_researcher_dashboard():
    st.title("🔬 Researcher Dashboard")

    user_email = st.session_state.get("user_email")
    if not user_email:
        st.error("⚠️ User not logged in.")
        st.stop()

    prefs = load_user_preferences(user_email)
    render_sidebar("researcher", prefs)

    show_company_deep_dive_section(prefs)
    st.markdown("---")

    updated_prefs = show_researcher_preferences_form(prefs)
    if updated_prefs:
        save_researcher_prefs(user_email, updated_prefs)
        st.success("✅ Preferences saved. Refreshing...")
        st.rerun()

# ⌛ Trigger
if __name__ == "__main__" or __name__ == "__streamlit__":
    show_researcher_dashboard()
