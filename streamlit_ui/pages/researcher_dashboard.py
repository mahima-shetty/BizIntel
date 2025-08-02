# streamlit_ui/pages/researcher_dashboard.py

import streamlit as st
import plotly.express as px
import yfinance as yf
import pandas as pd

from streamlit_ui.utils.researcher_prefs import load_researcher_prefs, save_researcher_prefs
from streamlit_ui.components.sidebar import render_sidebar

from app.agents.deep_dive_agent import company_deep_dive
from app.agents.peer_comparison_agent import get_peer_comparison, get_formatted_peer_df
from app.agents.industry_benchmarks_agent import compute_industry_benchmarks
from app.agents.peer_comparison_agent import generate_peer_comparison_insight

# ─────────────────────────────────────────────
@st.cache_data(show_spinner="📊 Computing industry benchmarks...")
def compute_industry_benchmarks_cached(ticker: str):
    return compute_industry_benchmarks(ticker)


@st.cache_data(show_spinner="📊 Fetching peer comparison data...")
def get_cached_peer_data(ticker: str, sort_by: str):
    raw_df = get_peer_comparison(ticker, sort_by)
    formatted_df = get_formatted_peer_df(raw_df)
    return raw_df, formatted_df


# ─────────────────────────────────────────────
def load_user_preferences(email):
    prefs = load_researcher_prefs(email)
    if not prefs:
        prefs = {"ticker": "AAPL", "depth": "standard"}
        st.warning("⚠️ No researcher preferences found. Using defaults.")
    st.session_state["depth"] = prefs.get("depth", "standard")  # ← add this
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

    if st.session_state.get("deep_dive_result") and st.session_state.get("deep_dive_ticker") == ticker:
        result = st.session_state["deep_dive_result"]
        business_model = result.get("business_model", "")
        strategy = result.get("strategy","")
        summary = result.get("summary", "")
        # swot = result.get("swot", "")
        source = result.get("source", "")

        st.markdown(
            f"""
            <div style='padding:1em; border-radius:8px; background-color:#000000; border:1px solid #ddd;'>
                <h4 style='color:white;'>📈 Business Model ({source})</h4>
                <p style='color:white;'>{business_model}</p>
                <hr style='border: 1px solid #555;'/>
                <h4 style='color:white;'>🎯 Strategy ({source})</h4>
                <p style='color:white;'>{strategy}</p>
                <hr style='border: 1px solid #555;'/>
                <h4 style='color:white;'>🧠 Summary ({source})</h4>
                <p style='color:white;'>{summary}</p>
                <hr style='border: 1px solid #555;'/></div>
                
            
            """,
            unsafe_allow_html=True
        )


        # ✅ Show peer comparison always
        show_peer_comparison_section(ticker)

        # 🔍 Only show industry benchmarks for deep analysis
        if st.session_state.get("depth") == "deep":
            st.markdown("---")
            show_industry_benchmark_section(ticker)


        

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
    st.session_state["selected_metrics"] = selected_metrics  # ✅ Used later in chart

    sort_by = st.selectbox("Sort peers by", available_metrics)

    # Load peer data
    if st.button("🔁 Refresh Peer Data") or st.session_state.get("last_peer_ticker") != ticker:
        print(f"[DEBUG] Refreshing peer data for {ticker} sorted by {sort_by}")
        raw_df, formatted_df = get_cached_peer_data(ticker, sort_by)
        st.session_state["peer_df_raw"] = raw_df
        st.session_state["peer_df_formatted"] = formatted_df
        st.session_state["last_peer_ticker"] = ticker
        st.session_state["peer_insight"] = None  # reset LLM summary

    # Display peer comparison table and charts
    if "peer_df_raw" in st.session_state and isinstance(st.session_state["peer_df_raw"], pd.DataFrame):
        raw_df = st.session_state["peer_df_raw"]

        if not raw_df.empty:
            st.markdown("### 📋 Peer Comparison Table")
            st.dataframe(st.session_state["peer_df_formatted"], use_container_width=True)

            # 📊 Chart
            if selected_metrics:
                print(f"[DEBUG] Generating chart for metrics: {selected_metrics}")
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
                st.info("ℹ️ Select at least one metric to show chart.")

            # 🧠 LLM Insight (manual trigger)
            st.markdown("### 🤖 Analyst Summary")
            if st.button("🧠 Generate Analyst Summary"):
                print("[DEBUG] Generating analyst summary manually...")
                print("[DEBUG] peer_df_raw type:", type(raw_df))
                print("[DEBUG] peer_df_raw preview:\n", raw_df.to_string())

                with st.spinner("Generating peer insights..."):
                    try:
                        insight = generate_peer_comparison_insight(ticker, raw_df)
                        st.session_state["peer_insight"] = insight.strip().replace("\n\n", "\n")
                        print("[DEBUG] Insight generated successfully.")
                    except Exception as e:
                        st.session_state["peer_insight"] = f"⚠️ Error: {e}"
                        print(f"[ERROR] LLM insight generation failed: {e}")

            # Show previously generated insight (if any)
            insight_text = st.session_state.get("peer_insight")
            if insight_text:
                st.markdown(
                    f"""
                    <div style='padding:1em; border-radius:8px; background-color:#000000; border:1px solid #ddd;'>{insight_text}</div>
                    
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info("Click the button above to generate insights.")

        else:
            print("[WARN] peer_df_raw is empty.")
            st.warning("⚠️ No peer data available.")



# ─────────────────────────────────────────────
def show_industry_benchmark_section(ticker: str):
    st.subheader("🧭 Industry Benchmarks")

    try:
        info = yf.Ticker(ticker).info
        sector = info.get("sector", "N/A")
        industry = info.get("industry", "N/A")
        st.caption(f"Sector: **{sector}** | Industry: **{industry}**")
    except Exception:
        st.caption("⚠️ Unable to retrieve sector/industry.")

    if st.button("📊 Show Industry Comparison"):
        with st.spinner("Computing industry benchmarks..."):
            df = compute_industry_benchmarks_cached(ticker)
            if df.empty:
                st.warning("Not enough peer data to compute industry benchmarks.")
                return

            formatted_df = df.copy()
            for col in ["Company", "Peer Median"]:
                formatted_df[col] = formatted_df[col].apply(
                    lambda x: f"{x:.2f}" if isinstance(x, (float, int)) else "—"
                )

            st.markdown("### 📋 Company vs. Peer Median")
            st.dataframe(formatted_df, use_container_width=True)

            melted = df.melt(id_vars="Metric", var_name="Type", value_name="Value")
            fig = px.bar(
                melted, x="Metric", y="Value", color="Type",
                barmode="group", text=melted["Value"].round(2),
                title="Company vs. Peer Median", template="plotly_white", height=500
            )
            st.plotly_chart(fig, use_container_width=True)


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
