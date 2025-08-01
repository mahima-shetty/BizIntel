#apps/agents/edgar_agents.py

from streamlit_ui.utils.edgar_utils import _get_latest_10k_text
from app.agents.llm_10k_summarizer import summarize_10k_text
from app.agents.company_summary_agent import summarize_company_from_edgar
from app.agents.researcher_10k_filings_agent import scrape_10k_with_trafilatura  # adjust path
import streamlit as st

MAX_SECTION_LENGTH = 3000  # token limit for LLM

def truncate_to_sentence(text: str, max_chars: int = 3000) -> str:
    """
    Truncates text to the last full sentence within the max character limit.
    """
    if len(text) <= max_chars:
        return text.strip()

    truncated = text[:max_chars]
    last_period = truncated.rfind(".")
    if last_period != -1:
        return truncated[:last_period + 1].strip()

    last_space = truncated.rfind(" ")
    return truncated[:last_space].strip() if last_space != -1 else truncated.strip()



@st.cache_data(show_spinner=False)
def get_business_model_and_strategy(ticker: str) -> dict:
    try:
        # Step 1: Try scraping 10-K with trafilatura
        
        raw_text = scrape_10k_with_trafilatura(ticker)

        if not raw_text or len(raw_text) < 1000:
            print(f"[EDGAR AGENT] ❌ Empty or too short 10-K extracted for {ticker}")
            return {
                "business_model": "Not available.",
                "strategy": "Not available.",
                "llm_summary": "LLM summary not available."
            }

        # Step 2: Generate vectorstore and apply RAG summarization
        from app.agents.business_strategy_rag_agent import (
            get_business_strategy_from_rag,
        )
        rag_results = get_business_strategy_from_rag(ticker, raw_text)

        business_model = rag_results.get("business_model", "Not available.")
        strategy = rag_results.get("strategy", "Not available.")
        swot = rag_results.get("swot", "Not available.")

        # Step 3: Optionally pass through LLM for a friendly summary
        try:
            from app.agents.company_summary_agent import summarize_company_from_edgar
            llm_friendly = summarize_company_from_edgar(ticker, {
                "business_model": business_model,
                "strategy": strategy,
                "swot_analysis": swot,
            })
        except Exception as e:
            print(f"[LLM FORMATTER ERROR] {e}")
            llm_friendly = "⚠️ LLM formatting failed."

        return {
            "business_model": business_model,
            "strategy": strategy,
            "swot": swot,
            "llm_summary": llm_friendly
        }

    except Exception as e:
        print(f"[ERROR] get_business_model_and_strategy failed for {ticker}: {e}")
        return {
            "business_model": "Error fetching data.",
            "strategy": "Error fetching data.",
            "swot": "Error fetching SWOT.",
            "llm_summary": "LLM summary failed."
        }

