# app/agents/agentic_analyst_dashboard.py

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional

# utils
from streamlit_ui.utils.history import load_kpi_history, load_news_history
from streamlit_ui.utils.history import save_kpi_snapshot, save_news_article
from streamlit_ui.utils.anomaly import detect_anomalies_for_ticker
from streamlit_ui.utils.analyst_prefs import load_analyst_prefs

# agents
from app.agents.yfinance_agent import get_stock_data, get_kpi_summary
from app.agents.llm_explainer import generate_trend_summary
from app.agents.aggregator_analyst import aggregate_analyst
from app.agents.summarization_agent import summarize_articles
from app.agents.insight_explorer import generate_insight_summary


# -----------------------------------------------------------------
# Helper
# -----------------------------------------------------------------
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


# -----------------------------------------------------------------
# State
# -----------------------------------------------------------------
class AnalystState(BaseModel):
    user_email: Optional[str] = None  # passed once, never overwritten
    tickers: List[str] = Field(default_factory=list)
    sector: Optional[str] = "Technology"
    topic: Optional[str] = "AI"
    count: int = 5
    sources: List[str] = Field(default_factory=list)
    threshold: float = 3.0
    stock_trends: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    trend_summaries: Dict[str, str] = Field(default_factory=dict)
    kpis: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    anomalies: Dict[str, Any] = Field(default_factory=dict)
    news_articles: List[Dict[str, Any]] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    final_report: Dict[str, Any] = Field(default_factory=dict)


# -----------------------------------------------------------------
# Nodes (only update the fields you change)
# -----------------------------------------------------------------
def load_user_prefs_node(state: AnalystState) -> dict:
    prefs = load_user_preferences(state.user_email)
    return {
        "tickers": prefs.get("tickers", []),
        "topic": prefs.get("topic", state.topic),
        "sector": prefs.get("sector", state.sector),
        "count": prefs.get("count", state.count),
        "sources": prefs.get("sources", [])
    }

def load_history_node(state: AnalystState) -> dict:
    updates = {}
    kpi_hist = load_kpi_history(state.user_email, state.tickers, days=7)
    news_hist = load_news_history(state.user_email, days=7)
    if kpi_hist:
        updates["kpis"] = kpi_hist
    if news_hist:
        updates["news_articles"] = news_hist
    return updates

def fetch_stock_data_node(state: AnalystState) -> dict:
    trends = {}
    for ticker in state.tickers:
        df = get_stock_data(ticker, period="30d", interval="1d")
        if not df.empty and "Close" in df.columns:
            trends[ticker] = df[["Date", "Close"]].to_dict(orient="records")
    return {"stock_trends": trends}

def detect_significant_changes_node(state: AnalystState) -> dict:
    trends = {}
    for ticker, rows in state.stock_trends.items():
        df = pd.DataFrame(rows)
        df["% Change"] = df["Close"].pct_change() * 100
        alerts = df[df["% Change"].abs() >= state.threshold]
        trends[ticker] = alerts.to_dict(orient="records")
    return {"stock_trends": trends}

def generate_trend_summaries_node(state: AnalystState) -> dict:
    summaries = {}
    for ticker, alerts in state.stock_trends.items():
        if alerts:
            df_alerts = pd.DataFrame(alerts)
            summaries[ticker] = generate_trend_summary(ticker, df_alerts)
    return {"trend_summaries": summaries}

def fetch_kpi_data_node(state: AnalystState) -> dict:
    kpis = {}
    for ticker in state.tickers:
        summary = get_kpi_summary(ticker)
        if summary:
            kpis[ticker] = summary
            save_kpi_snapshot(state.user_email, ticker, summary)
    return {"kpis": kpis}

def anomaly_detection_node(state: AnalystState) -> dict:
    anomalies = detect_anomalies_for_ticker({t: [state.kpis[t]] for t in state.kpis})
    return {"anomalies": anomalies}

def fetch_news_node(state: AnalystState) -> dict:
    articles = aggregate_analyst(topic=state.topic, count=state.count, sources=state.sources)
    if articles:
        for a in articles:
            save_news_article(state.user_email, a)
        return {"news_articles": articles}
    return {}

def summarize_news_node(state: AnalystState) -> dict:
    if state.news_articles:
        return {"insights": [summarize_articles(state.news_articles)]}
    return {}

def generate_insights_node(state: AnalystState) -> dict:
    combined_q = "Summarize insights from my KPIs, trends, and news together"
    return {"insights": state.insights + [generate_insight_summary(combined_q, state.dict(), None)]}

def compile_report_node(state: AnalystState) -> dict:
    final_report = {
        "kpi_data": state.kpis,
        "trend_summaries": state.trend_summaries,
        "news_articles": state.news_articles,
        "insights": state.insights,
        "anomalies": state.anomalies,
        "stock_trends": state.stock_trends
    }
    return {"final_report": final_report}


# -----------------------------------------------------------------
# Graph
# -----------------------------------------------------------------
def build_analyst_graph():
    graph = StateGraph(AnalystState)

    graph.add_node("load_prefs", load_user_prefs_node)
    graph.add_node("load_history", load_history_node)
    graph.add_node("fetch_stock_data", fetch_stock_data_node)
    graph.add_node("detect_changes", detect_significant_changes_node)
    graph.add_node("generate_trend_summaries", generate_trend_summaries_node)
    graph.add_node("fetch_kpis", fetch_kpi_data_node)
    graph.add_node("detect_anomalies", anomaly_detection_node)
    graph.add_node("fetch_news", fetch_news_node)
    graph.add_node("summarize_news", summarize_news_node)
    graph.add_node("generate_insights", generate_insights_node)
    graph.add_node("compile_report", compile_report_node)

    graph.set_entry_point("load_prefs")
    graph.add_edge("load_prefs", "load_history")

    graph.add_edge("load_history", "fetch_stock_data")
    graph.add_edge("fetch_stock_data", "detect_changes")
    graph.add_edge("detect_changes", "generate_trend_summaries")

    graph.add_edge("load_history", "fetch_kpis")
    graph.add_edge("fetch_kpis", "detect_anomalies")

    graph.add_edge("load_history", "fetch_news")
    graph.add_edge("fetch_news", "summarize_news")

    graph.add_edge("generate_trend_summaries", "generate_insights")
    graph.add_edge("detect_anomalies", "generate_insights")
    graph.add_edge("summarize_news", "generate_insights")

    graph.add_edge("generate_insights", "compile_report")
    graph.add_edge("compile_report", END)

    return graph

app = build_analyst_graph().compile()
# -----------------------------------------------------------------