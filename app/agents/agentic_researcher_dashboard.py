# app/agents/agentic_researcher_dashboard.py

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional

from app.agents.deep_dive_agent import company_deep_dive
from app.agents.peer_comparison_agent import get_peer_comparison, get_formatted_peer_df, generate_peer_comparison_insight
from app.agents.industry_benchmarks_agent import compute_industry_benchmarks
from streamlit_ui.utils.researcher_prefs import load_researcher_prefs

# ─────────────────────────────────────────────
class ResearcherState(TypedDict):
    user_email: str
    prefs: Dict[str, Any]
    ticker: Optional[str]
    depth: Optional[str]
    deep_dive_result: Optional[Dict[str, Any]]
    peer_raw: Optional[Any]
    peer_formatted: Optional[Any]
    benchmarks_df: Optional[Any]
    peer_insight: Optional[str]
    final_report: Optional[Dict[str, Any]]

# ─────────────────────────────────────────────
def load_preferences(state: ResearcherState) -> ResearcherState:
    prefs = load_researcher_prefs(state["user_email"])
    if not prefs:
        prefs = {"ticker": "AAPL", "depth": "standard"}
    # seed state
    return {
        **state,
        "prefs": prefs,
        "ticker": state.get("ticker") or prefs.get("ticker"),
        "depth": state.get("depth") or prefs.get("depth", "standard")
    }

def run_deep_dive(state: ResearcherState) -> ResearcherState:
    ticker = state.get("ticker")
    if not ticker:
        return {**state, "deep_dive_result": None}
    try:
        result = company_deep_dive(ticker)
    except Exception as e:
        result = {"error": str(e)}
    return {**state, "deep_dive_result": result}

def fetch_peer_data(state: ResearcherState) -> ResearcherState:
    ticker = state.get("ticker")
    # sort_by can be passed via prefs or state; default to "Market Cap"
    sort_by = state.get("prefs", {}).get("sort_by", "Market Cap")
    try:
        raw = get_peer_comparison(ticker, sort_by)
        formatted = get_formatted_peer_df(raw)
    except Exception as e:
        raw, formatted = None, None
    return {**state, "peer_raw": raw, "peer_formatted": formatted}

def compute_benchmarks_node(state: ResearcherState) -> ResearcherState:
    ticker = state.get("ticker")
    if not ticker:
        return {**state, "benchmarks_df": None}
    try:
        df = compute_industry_benchmarks(ticker)
    except Exception as e:
        df = None
    return {**state, "benchmarks_df": df}

def generate_peer_insight_node(state: ResearcherState) -> ResearcherState:
    raw = state.get("peer_raw")
    ticker = state.get("ticker")
    if raw is None or ticker is None:
        return {**state, "peer_insight": None}
    try:
        insight = generate_peer_comparison_insight(ticker, raw)
    except Exception as e:
        insight = f"⚠️ Error generating insight: {e}"
    return {**state, "peer_insight": insight}

def compile_report(state: ResearcherState) -> ResearcherState:
    report = {
        "prefs": state.get("prefs"),
        "ticker": state.get("ticker"),
        "depth": state.get("depth"),
        "deep_dive_result": state.get("deep_dive_result"),
        "peer_raw": state.get("peer_raw"),
        "peer_formatted": state.get("peer_formatted"),
        "benchmarks_df": state.get("benchmarks_df"),
        "peer_insight": state.get("peer_insight"),
    }
    return {**state, "final_report": report}

# ─────────────────────────────────────────────
graph = StateGraph(ResearcherState)

graph.add_node("load_preferences", load_preferences)
graph.add_node("run_deep_dive", run_deep_dive)
graph.add_node("fetch_peer_data", fetch_peer_data)
graph.add_node("compute_benchmarks", compute_benchmarks_node)
graph.add_node("generate_peer_insight", generate_peer_insight_node)
graph.add_node("compile_report", compile_report)

# simple linear flow (Streamlit can call whole flow or you can call specific entry points)
graph.set_entry_point("load_preferences")
graph.add_edge("load_preferences", "run_deep_dive")
graph.add_edge("run_deep_dive", "fetch_peer_data")
graph.add_edge("fetch_peer_data", "compute_benchmarks")
graph.add_edge("compute_benchmarks", "generate_peer_insight")
graph.add_edge("generate_peer_insight", "compile_report")
graph.add_edge("compile_report", END)

app = graph.compile()
