# analyst_dashboard.py

import streamlit as st
from streamlit_ui.utils.analyst_prefs import load_analyst_prefs, save_analyst_prefs
from app.agents.yfinance_agent import get_stock_data, get_kpi_summary, plot_stock_price_chart


# ───────────────────────────────────────────────────────────
# 📊 Section 1: KPI Tracking
def show_kpi_tracking_section(user_email):
    st.subheader("📊 KPI Tracking Dashboard")

    # Load from DB or fallback to defaults
    prefs = load_analyst_prefs(user_email)
    default_tickers = prefs.get("tickers", ["AAPL", "GOOGL", "MSFT"])
    tickers_input = st.text_input("Enter stock tickers (comma-separated):", ",".join(default_tickers))

    # Process user input
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    if not tickers:
        st.warning("⚠️ Please enter at least one valid stock ticker.")
        return

    # Save preferences back to DB
    prefs["tickers"] = tickers
    save_analyst_prefs(user_email, prefs)

    for ticker in tickers:
        st.markdown(f"### {ticker}")
        col1, col2 = st.columns([2, 1])

        # 📈 Stock Chart
        with col1:
            df = get_stock_data(ticker)
            plot_stock_price_chart(df, ticker)

        # 📌 KPIs
        with col2:
            kpi_data = get_kpi_summary(ticker)
            for k, v in kpi_data.items():
                st.markdown(f"**{k}:** {v}")

        st.markdown("---")

import pandas as pd

# ───────────────────────────────────────────────────────────
# 📈 Section 2: Trend Detection
def show_trend_detection_section(user_email):
    st.subheader("📈 Trend Detection with Thresholds")

    prefs = load_analyst_prefs(user_email)
    tickers = prefs.get("tickers", ["AAPL", "GOOGL", "MSFT"])
    threshold = st.slider("Set % change threshold", 1, 20, 5)

    for ticker in tickers:
        st.markdown(f"### {ticker} - Price Alerts")
        df = get_stock_data(ticker, period="30d", interval="1d")

        if df.empty or "Close" not in df.columns:
            st.warning(f"No price data for {ticker}")
            continue

        df["% Change"] = df["Close"].pct_change() * 100

        alerts = df[df["% Change"].abs() >= threshold]

        if alerts.empty:
            st.success("✅ No significant changes detected.")
        else:
            st.warning(f"⚠️ {len(alerts)} significant movements found.")
            st.dataframe(alerts[["Date", "Close", "% Change"]].dropna().round(2))



# ───────────────────────────────────────────────────────────
# 🚀 Main Entry Point
def show_analyst_dashboard():
    st.title("🧠 Analyst Dashboard")

    user_email = st.session_state.get("user_email")
    if not user_email:
        st.error("⚠️ User not logged in.")
        st.stop()

    # Section 1: KPI Tracking
    show_kpi_tracking_section(user_email)

    # Section 2: Trend Detection
    show_trend_detection_section(user_email)




# At bottom of founder_dashboard.py
if __name__ == "__main__" or __name__ == "__streamlit__":
    show_analyst_dashboard()