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
from app.agents.insight_explorer import generate_insight_summary
from streamlit_ui.utils.history import save_kpi_snapshot, save_news_article
from streamlit_ui.utils.history import load_kpi_history, load_news_history
from app.agents.agentic_analyst_dashboard import app

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
        # Save KPI snapshot
        try:
            save_kpi_snapshot(user_email, ticker, kpi_data)
        except Exception as e:
            st.warning(f"⚠️ Could not save KPI snapshot for {ticker}: {e}")

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
                    print("will call generate_trend_summary in ANalyzing trends...")
                    explanation = generate_trend_summary(ticker, alerts)
                    st.success(explanation)


# ─────────────────────────────────────────────
# 🛠 Custom Data Builder
def show_custom_data_builder_section(prefs,user_email):
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
    
    
    # Save each article to history
    try:
        for article in articles:
            save_news_article(user_email, article)
    except Exception as e:
        st.warning(f"⚠️ Could not save news articles: {e}")
    
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
# 🔍 Section 5: Insight Explorer (LLM + Queryable)
def show_insight_explorer_section(prefs, user_email):
    st.subheader("🔍 Insight Explorer")

    # Predefined questions
    st.markdown("#### 🧠 Try one of these:")
    questions = [
        "📈 What happened to my tracked stocks this week?",
        "📉 Were there any major KPI changes in the last 7 days?",
        "📰 What are the most discussed topics in the news I read?",
        "🤖 Summarize insights from my KPIs and news together"
    ]

    for i, q in enumerate(questions):
        if st.button(q, key=f"qbtn_{i}"):
            with st.spinner("Generating insights..."):
                response = generate_insight_summary(q, prefs, user_email)
                st.success(response)

    st.markdown("---")

    # Freeform query
    st.markdown("#### 💬 Ask your own question:")
    user_query = st.text_area("Type your question about KPIs or news...", height=100)

    if st.button("🔍 Analyze My Data"):
        if user_query.strip():
            with st.spinner("Thinking..."):
                response = generate_insight_summary(user_query, prefs, user_email)
                st.success(response)
        else:
            st.warning("Please enter a valid question.")


from utils.anomaly import detect_anomalies_for_ticker
import streamlit as st



mock_kpi_history = {
    "AAPL": {
        "2025-07-10": {"Market Cap": 3_000_000_000_000, "PE Ratio": 28.5, "EPS": 6.10, "Dividend Yield": 0.52},
        "2025-07-11": {"Market Cap": 3_100_000_000_000, "PE Ratio": 30.1, "EPS": 6.30, "Dividend Yield": 0.51},
        "2025-07-12": {"Market Cap": 3_050_000_000_000, "PE Ratio": 29.8, "EPS": 6.25, "Dividend Yield": 0.50},
        "2025-07-13": {"Market Cap": 3_900_000_000_000, "PE Ratio": 90.0,  "EPS": 12.00, "Dividend Yield": 1.20},
        "2025-07-14": {"Market Cap": 3_080_000_000_000, "PE Ratio": 29.5, "EPS": 6.20, "Dividend Yield": 0.49},
    }
}


import json

def show_anomaly_section(kpi_history):
    st.markdown("🔍 **Anomaly Detection**")
    
    
    USE_MOCK_DATA = False
    if USE_MOCK_DATA:
        kpi_history = mock_kpi_history
        
    anomalies = detect_anomalies_for_ticker(kpi_history)
    
    # st.write("📊 Raw Anomalies Dict:")
    # st.json(anomalies)

    
    
    # st.code(json.dumps(anomalies, indent=2), language="json")


    if not anomalies:
        st.success("✅ No anomalies detected in KPI metrics.")
    else:
        for ticker, anomaly_data in anomalies.items():
            st.subheader(f"📈 {ticker} Anomalies")
            for metric, records in anomaly_data.items():
                st.markdown(f"**{metric}**")
                for r in records:
                    st.markdown(f"- {r['Date']}: {metric} = `{r[metric]}`")



##  ─────────────────────────────────────────────
## 🚀 Entry Point
# def show_analyst_dashboard():
#     st.title("🧠 Analyst Dashboard")

#     user_email = st.session_state.get("user_email")
#     if not user_email:
#         st.error("⚠️ User not logged in.")
#         st.stop()

#     prefs = load_user_preferences(user_email)
#     render_sidebar("analyst", prefs)

#     show_kpi_tracking_section(prefs, user_email)
    
#     show_trend_detection_section(prefs)
#     st.markdown("---")
#     show_custom_data_builder_section(prefs, user_email)
    
#     st.markdown("---")
#     show_insight_explorer_section(prefs,user_email)
#     st.markdown("---")
#     # ✅ FIX: Load KPI history here
#     tickers = prefs.get("tickers", ["AAPL", "MSFT"])
#     kpi_history = load_kpi_history(user_email, tickers, days=7)
#     show_anomaly_section(kpi_history)
    

#     updated_prefs = show_analyst_preferences_form(prefs)
#     if updated_prefs:
#         save_analyst_prefs(user_email, updated_prefs)
#         st.success("✅ Preferences saved. Refreshing...")
#         st.rerun()




##  ─────────────────────────────────────────────
## 🚀 Entry Point

        
def show_analyst_dashboard():
    st.title("🧠 Analyst Dashboard")

    user_email = st.session_state.get("user_email")
    if not user_email:
        st.error("⚠️ User not logged in.")
        st.stop()

    # Load prefs
    prefs = load_user_preferences(user_email)
    render_sidebar("analyst", prefs)

    # --- Run LangGraph flow ONCE ---
    if "analyst_report" not in st.session_state:
        with st.spinner("🤖 Running AI pipeline..."):
            result = app.invoke({"user_email": user_email})
            st.session_state.analyst_report = result.get("final_report", {})

    # You can pass st.session_state.analyst_report into any section
    
    print("Analyst Report:", st.session_state.analyst_report)
    report = st.session_state.analyst_report

    # Independent section calls
    show_kpi_tracking_section(prefs, user_email)
    show_trend_detection_section(prefs)
    show_custom_data_builder_section(prefs, user_email)
    show_insight_explorer_section(prefs, user_email)

    # KPI history for anomalies
    kpi_history = load_kpi_history(user_email, prefs.get("tickers", ["AAPL", "MSFT"]), days=7)
    show_anomaly_section(kpi_history)

    # Download the readable report
    st.markdown("### 📥 Download Full Report")
          
            
    if st.button("📄 Download Report"):
        report_json = json.dumps(report, indent=2, default=str)  
        st.download_button(
            label="Download Report",
            data=report_json,
            file_name="analyst_report.json",
            mime="application/json"
        )
            
    # Preferences update
    updated_prefs = show_analyst_preferences_form(prefs)
    if updated_prefs:
        save_analyst_prefs(user_email, updated_prefs)
        st.success("✅ Preferences saved. Refreshing...")
        st.rerun()


if __name__ == "__main__" or __name__ == "__streamlit__":
    show_analyst_dashboard()
