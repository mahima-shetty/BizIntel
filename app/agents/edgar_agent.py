from streamlit_ui.utils.edgar_utils import _get_latest_10k_text
from app.agents.llm_10k_summarizer import summarize_10k_text
from app.agents.company_summary_agent import summarize_company_from_edgar

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
        raw_text = _get_latest_10k_text(ticker)

        if not raw_text or len(raw_text) < 1000:
            print(f"[EDGAR AGENT] Empty or too short filing for {ticker}")
            return {
                "business_model": "Not available.",
                "strategy": "Not available.",
                "llm_summary": "LLM summary not available."
            }

        merged_summary = summarize_10k_text(raw_text).strip()

        if not merged_summary or len(merged_summary) < 300:
            return {
                "business_model": "Not available.",
                "strategy": "Not available.",
                "llm_summary": "LLM summary not available."
            }

        trimmed = truncate_to_sentence(merged_summary, MAX_SECTION_LENGTH)

        try:
            llm_friendly = summarize_company_from_edgar(ticker, {"business_strategy": trimmed})
        except Exception as e:
            print(f"[EDGAR FORMATTER ERROR] {e}")
            llm_friendly = "⚠️ Formatting failed."

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
