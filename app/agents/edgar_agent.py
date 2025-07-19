from streamlit_ui.utils.edgar_utils import _get_latest_10k_text
from app.agents.llm_10k_summarizer import summarize_10k_text
from app.agents.company_summary_agent import summarize_company_from_edgar
import streamlit as st

MAX_SECTION_LENGTH = 3000  # safe token limit

def get_business_model_and_strategy(ticker: str) -> dict:
    """
    Loads full 10-K, summarizes using LLM, and returns both raw + friendly summaries.
    """
    try:
        raw_text = _get_latest_10k_text(ticker)
        
        if not raw_text or len(raw_text) < 1000:
            print(f"[EDGAR AGENT] Empty or too short filing for {ticker}")
            return {
                "business_model": "Not available.",
                "strategy": "Not available.",
                "llm_summary": "LLM summary not available."
            }

        # Use full 10-K chunked summarization
        merged_summary = summarize_10k_text(raw_text).strip()

        if not merged_summary or len(merged_summary) < 300:
            return {
                "business_model": "Not available.",
                "strategy": "Not available.",
                "llm_summary": "LLM summary not available."
            }

        # Optional: truncate before feeding to layman formatter
        trimmed = merged_summary[:MAX_SECTION_LENGTH]

        # Friendly version: bullet-point summary
        llm_friendly = summarize_company_from_edgar(ticker, {"business_strategy": trimmed})

        return {
            "business_model": trimmed,
            "strategy": trimmed,
            "llm_summary": llm_friendly
        }

    except Exception as e:
        print(f"[EDGAR AGENT ERROR] {e}")
        return {
            "business_model": "Error fetching data.",
            "strategy": "Error fetching data.",
            "llm_summary": "LLM summary failed."
        }
