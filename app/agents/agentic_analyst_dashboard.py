# app/agents/agentic_analyst_dashboard.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any

from app.agents.yfinance_agent import get_stock_data, get_kpi_summary
from app.agents.llm_explainer import generate_trend_summary
from app.agents.aggregator_analyst import aggregate_analyst
from app.agents.summarization_agent import summarize_articles
from app.agents.insight_explorer import generate_insight_summary
from streamlit_ui.utils.anomaly import detect_anomalies_for_ticker
from streamlit_ui.utils.analyst_prefs import load_analyst_prefs

# ─────────────────────────────
class AnalystDashboardState(TypedDict):
    user_email: str
    prefs: Dict[str, Any]
    tickers: List[str]
    stock_data: Dict[str, Any]
    kpi_summary: Dict[str, Dict[str, Any]]
    trend_alerts: Dict[str, Any]
    custom_articles: List[Dict[str, Any]]
    summarized_articles: List[Dict[str, Any]]
    anomalies: Dict[str, Any]
    insight_responses: Dict[str, str]
    final_report: Dict[str, Any]

# ─────────────────────────────
def load_preferences(state: AnalystDashboardState):
    prefs = load_analyst_prefs(state["user_email"])
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
    tickers = prefs.get("tickers", [])
    return {**state, "prefs": prefs, "tickers": tickers}

# ─────────────────────────────
def fetch_stock_data_and_kpis(state: AnalystDashboardState):
    tickers = state["tickers"]
    kpi_summary = {}
    stock_data = {}
    for ticker in tickers:
        df = get_stock_data(ticker)
        kpi = get_kpi_summary(ticker)
        stock_data[ticker] = df
        kpi_summary[ticker] = kpi
    return {**state, "stock_data": stock_data, "kpi_summary": kpi_summary}

# ─────────────────────────────
def detect_trends(state: AnalystDashboardState):
    tickers = state["tickers"]
    threshold = 3.0  # Fixed threshold or could be from prefs if passed
    alerts = {}
    for ticker in tickers:
        df = state["stock_data"].get(ticker)
        if df is None or df.empty or "Close" not in df.columns:
            alerts[ticker] = {"error": "No price data"}
            continue
        df["% Change"] = df["Close"].pct_change() * 100
        sig_moves = df[df["% Change"].abs() >= threshold]
        alerts[ticker] = sig_moves.round(2).to_dict(orient="records") if not sig_moves.empty else []
    return {**state, "trend_alerts": alerts}

# ─────────────────────────────
def aggregate_news_articles(state: AnalystDashboardState):
    topic = state["prefs"].get("topic", "Startups")
    count = int(state["prefs"].get("count", 5))
    sources = state["prefs"].get("sources", ["TechCrunch", "NewsAPI"])
    articles = aggregate_analyst(topic=topic, count=count, sources=sources)
    return {**state, "custom_articles": articles}

# ─────────────────────────────
def summarize_articles_node(state: AnalystDashboardState):
    articles = state.get("custom_articles", [])
    for article in articles:
        article["summary"] = summarize_articles([article])  # Summarize individually
    return {**state, "summarized_articles": articles}

# ─────────────────────────────
def detect_anomalies_node(state: AnalystDashboardState):
    kpi_history = {}  # We don’t have actual KPI history here; ideally load from DB if needed
    # For now, anomaly detection on current KPI summary only is limited,
    # so just passing empty or placeholder anomalies
    anomalies = detect_anomalies_for_ticker(kpi_history)
    return {**state, "anomalies": anomalies}

# ─────────────────────────────
def generate_insights_node(state: AnalystDashboardState):
    # Sample predefined questions - you may want to customize or take from prefs/user input
    questions = [
        "What happened to my tracked stocks this week?",
        "Were there any major KPI changes in the last 7 days?",
        "What are the most discussed topics in the news I read?",
        "Summarize insights from my KPIs and news together"
    ]
    insight_responses = {}
    for q in questions:
        response = generate_insight_summary(q, state["prefs"], state["user_email"])
        insight_responses[q] = response
    return {**state, "insight_responses": insight_responses}

# ─────────────────────────────
def compile_final_report(state: AnalystDashboardState):
    report = {
        "prefs": state["prefs"],
        "tickers": state["tickers"],
        "kpi_summary": state["kpi_summary"],
        "trend_alerts": state["trend_alerts"],
        "market_news": state["summarized_articles"],
        "anomalies": state["anomalies"],
        "insights": state["insight_responses"]
    }
    return {**state, "final_report": report}

# ─────────────────────────────
graph = StateGraph(AnalystDashboardState)
graph.add_node("load_preferences", load_preferences)
graph.add_node("fetch_stock_data_and_kpis", fetch_stock_data_and_kpis)
graph.add_node("detect_trends", detect_trends)
graph.add_node("aggregate_news_articles", aggregate_news_articles)
graph.add_node("summarize_articles_node", summarize_articles_node)
graph.add_node("detect_anomalies_node", detect_anomalies_node)
graph.add_node("generate_insights_node", generate_insights_node)
graph.add_node("compile_final_report", compile_final_report)

graph.set_entry_point("load_preferences")
graph.add_edge("load_preferences", "fetch_stock_data_and_kpis")
graph.add_edge("fetch_stock_data_and_kpis", "detect_trends")
graph.add_edge("detect_trends", "aggregate_news_articles")
graph.add_edge("aggregate_news_articles", "summarize_articles_node")
graph.add_edge("summarize_articles_node", "detect_anomalies_node")
graph.add_edge("detect_anomalies_node", "generate_insights_node")
graph.add_edge("generate_insights_node", "compile_final_report")
graph.add_edge("compile_final_report", END)

app = graph.compile()
# ─────────────────────────────