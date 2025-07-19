from streamlit_ui.utils.history import load_kpi_history, load_news_history
from app.agents.llm_explainer import summarize_kpi_and_news, format_insight_prompt  # Modular functions
import json

mock_kpi_history = {
    "AAPL": {
        "2025-07-10": {
            "Market Cap": 3000000000000,
            "PE Ratio": 28.5,
            "EPS": 6.10,
            "Dividend Yield": 0.52,
        },
        "2025-07-11": {
            "Market Cap": 3100000000000,
            "PE Ratio": 30.1,
            "EPS": 6.30,
            "Dividend Yield": 0.51,
        },
        "2025-07-12": {
            "Market Cap": 3050000000000,
            "PE Ratio": 29.8,
            "EPS": 6.25,
            "Dividend Yield": 0.50,
        },
        "2025-07-13": {
            "Market Cap": 3900000000000,  # 👈 Outlier
            "PE Ratio": 90.0,             # 👈 Outlier
            "EPS": 12.0,                  # 👈 Outlier
            "Dividend Yield": 1.2,        # 👈 Outlier
        },
        "2025-07-14": {
            "Market Cap": 3080000000000,
            "PE Ratio": 29.5,
            "EPS": 6.20,
            "Dividend Yield": 0.49,
        }
    }
}


def generate_insight_summary(question, prefs, user_email):
    tickers = prefs.get("tickers", ["AAPL", "MSFT"])
    topic = prefs.get("topic", "AI")
    sources = prefs.get("sources", ["NewsAPI"])

    kpi_history = load_kpi_history(user_email, tickers, days=7)

    news_history = load_news_history(user_email, days=7)

    if not kpi_history and not news_history:
        return "⚠️ No KPI or news history found. Please update your dashboard preferences and wait for data to be saved."

    # ✅ Split formatted parts
    kpi_lines = []
    for ticker, daily_data in kpi_history.items():
        kpi_lines.append(f"Ticker: {ticker}")
        for date, kpi in daily_data.items():
            kpi_lines.append(f"Date: {date}")
            for key, val in kpi.items():
                kpi_lines.append(f"- {key}: {val}")
            kpi_lines.append("")
    kpi_str = "\n".join(kpi_lines)

    news_lines = []
    for article in news_history:
        title = article.get("title", "")
        source = article.get("source", "")
        date = article.get("date", "")
        news_lines.append(f"- {title} ({source}, {date})")
    news_str = "\n".join(news_lines)

    return summarize_kpi_and_news({
        "question": question,
        "kpi_data": kpi_str,
        "news_data": news_str
    })
