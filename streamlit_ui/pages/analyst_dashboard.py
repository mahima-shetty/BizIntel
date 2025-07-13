# streamlit_ui/pages/analyst_dashboard.py

import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

from streamlit_ui.utils.analyst_prefs import load_analyst_prefs, save_analyst_prefs
from streamlit_ui.components.sidebar import render_sidebar

from app.agents.yfinance_agent import get_stock_data, get_kpi_summary, plot_stock_price_chart
from app.agents.llm_explainer import generate_trend_summary
from app.agents.aggregator_analyst import aggregate_analyst
from app.agents.summarization_agent import summarize_articles


# ─────────────────────────────────────────────
# 🔧 Constants
TRAILING_JUNK = ["TechCrunch", "Reuters", "CNBC", "NewsAPI", "Finnhub"]
TOPIC_OPTIONS = ["AI", "Finance", "Technology", "Startups"]
SOURCE_OPTIONS = ["TechCrunch", "NewsAPI", "Reuters", "CNBC", "Finnhub"]
SECTOR_TICKER_MAP = {
    "Technology": ["AAPL", "MSFT", "GOOGL"],
    "Finance": ["JPM", "BAC", "C"],
    "Healthcare": ["JNJ", "PFE", "MRK"],
    "Energy": ["XOM", "CVX", "BP"],
}


# ─────────────────────────────────────────────
# 🧠 Utility
def extract_main_text_and_link(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    link_tag = soup.find("a")
    link = link_tag["href"] if link_tag and link_tag.has_attr("href") else None
    text = soup.get_text(strip=True)
    return text, link


# ─────────────────────────────────────────────
# 📩 Load Defaults if Not Found
def load_user_preferences(email):
    prefs = load_analyst_prefs(email)
    if not prefs:
        prefs = {
            "sector": "Technology",
            "topic": "Startups",
            "region": "Global",
            "count": 5,
            "sources": ["TechCrunch", "NewsAPI"],
            "notification_frequency": "Daily",
            "tickers": ["AAPL", "GOOGL", "MSFT"]
        }
        st.warning("⚠️ No preferences found. Using defaults.")
    return prefs


# ─────────────────────────────────────────────
# 📊 KPI Tracking
def show_kpi_tracking_section(prefs, user_email):
    st.subheader("📊 KPI Tracking Dashboard")
    sector_pref = prefs.get("sector", "Technology")
    st.caption(f"🏭 Sector: **{sector_pref}**")

    default_tickers = prefs.get("tickers") or SECTOR_TICKER_MAP.get(sector_pref, ["AAPL"])
    tickers_input = st.text_input("Enter stock tickers (comma-separated):", ",".join(default_tickers))
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

    if not tickers:
        st.warning("⚠️ Please enter at least one valid stock ticker.")
        return

    prefs["tickers"] = tickers
    save_analyst_prefs(user_email, prefs)

    for ticker in tickers:
        st.markdown(f"### {ticker}")
        col1, col2 = st.columns([2, 1])

        with col1:
            df = get_stock_data(ticker)
            plot_stock_price_chart(df, ticker)

        with col2:
            kpi_data = get_kpi_summary(ticker)
            for k, v in kpi_data.items():
                st.markdown(f"**{k}:** {v}")

        st.markdown("---")


# ─────────────────────────────────────────────
# 📈 Trend Detection
def show_trend_detection_section(prefs):
    st.subheader("📈 Trend Detection with Thresholds")
    tickers = prefs.get("tickers", ["AAPL", "GOOGL", "MSFT"])
    threshold = st.slider("Set '%' change threshold", 0.5, 10.0, 3.0)

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

            if st.button(f"🧠 Explain {ticker} trends", key=f"llm_{ticker}"):
                with st.spinner("Analyzing trends..."):
                    explanation = generate_trend_summary(ticker, alerts)
                    st.success(explanation)


# ─────────────────────────────────────────────
# 🛠 Custom Data Builder
def show_custom_data_builder_section(prefs):
    st.subheader("🛠 Custom Data Source Builder")

    topic = prefs.get("topic", "AI")
    sources = prefs.get("sources", ["NewsAPI", "Reuters", "CNBC"])
    count = prefs.get("count", 5)

    if st.button("🔎 Fetch News"):
        st.session_state["custom_articles"] = aggregate_analyst(
            topic=topic,
            count=int(count),
            sources=sources
        )

    articles = st.session_state.get("custom_articles", [])
    if not articles:
        st.info("No articles fetched yet.")
        return

    st.markdown("### 🧾 Results")
    for i, article in enumerate(articles):
        st.markdown(f"### {i+1}. {article.get('title', 'No title')}")
        st.write(f"📡 Source: {article.get('source', 'Unknown')}")

        raw_content = article.get("content") or article.get("description") or ""
        content, extracted_link = extract_main_text_and_link(raw_content)

        title = article.get("title", "").strip()
        content = content.strip()

        if title and content.lower().startswith(title.lower()):
            content = content[len(title):].strip()
        for junk in TRAILING_JUNK:
            if content.lower().endswith(junk.lower()):
                content = content[:-len(junk)].strip()

        if not content or len(content) < 20:
            st.info("📖 Read more through the link below.")
        else:
            st.write(content)

        final_link = extracted_link or article.get("url")
        if final_link:
            st.markdown(f"[🔗 Read Full Article]({final_link})", unsafe_allow_html=True)

        if content and len(content) >= 20:
            if st.button(f"🧠 Summarize", key=f"summarize_{i}"):
                with st.spinner("Summarizing..."):
                    summary = summarize_articles([article])
                    st.success(summary)

        st.markdown("---")


# ─────────────────────────────────────────────
# ⚙️ Preferences Form
def show_analyst_preferences_form(prefs):
    st.markdown("## ⚙️ Update Your Analyst Preferences")

    topic = prefs.get("topic", "AI")
    count = int(prefs.get("count", 5))
    sources = prefs.get("sources", ["NewsAPI", "Reuters", "CNBC"])
    sector = prefs.get("sector", "Technology")

    topic = topic if topic in TOPIC_OPTIONS else "AI"
    sector_options = list(SECTOR_TICKER_MAP.keys())
    sector = sector if sector in sector_options else "Technology"

    with st.form("update_analyst_prefs"):
        topic = st.selectbox("🧠 Topic", TOPIC_OPTIONS, index=TOPIC_OPTIONS.index(topic))
        sector = st.selectbox("🏭 Sector", sector_options, index=sector_options.index(sector))
        count = st.slider("📊 Articles to Fetch", 1, 20, count)
        sources = st.multiselect("📡 News Sources", SOURCE_OPTIONS, default=sources)
        submitted = st.form_submit_button("💾 Save Preferences")
        if submitted:
            return {
                "topic": topic,
                "count": count,
                "sector": sector,
                "sources": sources
            }
    return None



# ─────────────────────────────────────────────
# 🚀 Entry Point
def show_analyst_dashboard():
    st.title("🧠 Analyst Dashboard")

    user_email = st.session_state.get("user_email")
    if not user_email:
        st.error("⚠️ User not logged in.")
        st.stop()

    prefs = load_user_preferences(user_email)
    render_sidebar("analyst", prefs)

    show_kpi_tracking_section(prefs, user_email)
    
    show_trend_detection_section(prefs)
    st.markdown("---")
    show_custom_data_builder_section(prefs)

    updated_prefs = show_analyst_preferences_form(prefs)
    if updated_prefs:
        save_analyst_prefs(user_email, updated_prefs)
        st.success("✅ Preferences saved. Refreshing...")
        st.rerun()


if __name__ == "__main__" or __name__ == "__streamlit__":
    show_analyst_dashboard()
