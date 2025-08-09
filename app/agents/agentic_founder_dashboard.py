# app/agents/agentic_founder_dashboard.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from app.agents.aggregator import aggregate_news
from app.agents.summarization_agent import summarize_articles
from app.agents.funding_agent import fetch_funding_news
from streamlit_ui.utils.founder_prefs import load_founder_prefs

# ─────────────────────────────
# State Definition
class FounderDashboardState(TypedDict):
    user_email: str
    prefs: Dict
    market_news: List[Dict]
    summarized_news: str
    funding_updates: List[Dict]
    final_report: Dict

# ─────────────────────────────
# Nodes
def load_preferences(state: FounderDashboardState):
    prefs = load_founder_prefs(state["user_email"])
    if not prefs:
        prefs = {
            "topic": "Startups",
            "count": 5,
            "funding_count": 5,
            "sources": ["TechCrunch", "NewsAPI"],
            "notification_frequency": "Daily"
        }
    return {**state, "prefs": prefs}

def fetch_market_news(state: FounderDashboardState):
    topic = state["prefs"]["topic"]
    count = state["prefs"]["count"]
    sources = state["prefs"]["sources"]
    articles = aggregate_news(topic, count, sources)
    return {**state, "market_news": articles}

# def summarize_news(state: FounderDashboardState):
#     summary = summarize_articles(state["market_news"])
#     return {**state, "summarized_news": summary}

def summarize_news(state: FounderDashboardState):
    articles = state["market_news"]
    for article in articles:
        article["summary"] = summarize_articles([article])  # summarize individually
    return {**state, "market_news": articles}

def fetch_funding(state: FounderDashboardState):
    funding_news = fetch_funding_news(state["prefs"]["funding_count"])
    return {**state, "funding_updates": funding_news}

def compile_report(state: FounderDashboardState):
    report = {
        "market_news": state["market_news"],
        # "summary": state["summarized_news"],
        "funding_updates": state["funding_updates"],
        # "insights": [
        #     "Focus on emerging AI funding opportunities.",
        #     "Monitor policy changes affecting patents.",
        #     "Explore collaboration with PSBs for lending opportunities."
        # ]
    }
    return {**state, "final_report": report}

# ─────────────────────────────
# Build LangGraph
graph = StateGraph(FounderDashboardState)
graph.add_node("load_preferences", load_preferences)
graph.add_node("fetch_market_news", fetch_market_news)
graph.add_node("summarize_news", summarize_news)
graph.add_node("fetch_funding", fetch_funding)
graph.add_node("compile_report", compile_report)

graph.set_entry_point("load_preferences")
graph.add_edge("load_preferences", "fetch_market_news")
graph.add_edge("fetch_market_news", "summarize_news")
graph.add_edge("summarize_news", "fetch_funding")
graph.add_edge("fetch_funding", "compile_report")
graph.add_edge("compile_report", END)

app = graph.compile()
