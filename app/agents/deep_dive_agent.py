# app/agents/deep_dive_agent.py

from app.agents.fmp_business_summary_agent import get_fmp_business_summary
from app.agents.researcher_summary_yfinance_agent import get_researcher_business_summary_from_yfinance
from app.agents.swot_agent import generate_swot_analysis_from_summary
from app.agents.edgar_agent import get_business_model_and_strategy
from app.agents.company_summary_agent import summarize_company_from_yfinance


def company_deep_dive(ticker: str) -> dict:
    """
    Perform a deep dive analysis on a company.
    Priority:
        1. EDGAR Agent (10-K + RAG)
        2. yFinance fallback
    """
    business_model = ""
    strategy = ""
    summary = ""
    swot = ""
    source = ""

    # Step 1: Try EDGAR + RAG
    try:
        print(f"[INFO] 🧾 Using EDGAR agent for {ticker}...")
        edgar_data = get_business_model_and_strategy(ticker)
        business_model = edgar_data.get("business_model", "")
        strategy = edgar_data.get("strategy", "")
        summary = edgar_data.get("llm_summary", "")
        swot = edgar_data.get("swot", "")
        
        print(f"Business: {business_model}")
        print(f"Strategy: {strategy}")
        print(f"Summary: {summary}")
        print(f"SWOT: {swot}")
        
        if summary and len(summary) > 200:
            source = "EDGAR"
            return {
                "business_model": business_model,
                "strategy": strategy,
                "summary": summary,
                "swot": swot,
                "source": source
            }
    except Exception as e:
        print(f"[WARN] ❌ EDGAR agent failed: {e}")

    # # Step 2: Try FMP
    # try:
    #     print(f"[INFO] 📊 Falling back to FMP summary for {ticker}...")
    #     fmp_summary = get_fmp_business_summary(ticker)
    #     summary = summarize_company_overview(fmp_summary, ticker)
    #     swot = generate_swot_analysis_from_summary(summary, ticker)
    #     source = "FMP"
    #     return {
    #         "summary": summary,
    #         "swot": swot,
    #         "source": source
    #     }
    # except Exception as e:
    #     print(f"[WARN] ❌ FMP fallback failed: {e}")

    # Step 3: Try yFinance
    try:
        print(f"[INFO] 📉 Falling back to yFinance summary for {ticker}...")
        y_summary = get_researcher_business_summary_from_yfinance(ticker)

        if not y_summary or not y_summary.get("business_model"):
            raise ValueError("yFinance summary is empty or invalid")

        business_model = y_summary.get("business_model", "")
        strategy = y_summary.get("strategy", "")

        summary = summarize_company_from_yfinance(business_model, strategy, ticker)  # if you renamed it
        swot = generate_swot_analysis_from_summary(summary, ticker)
        source = "yFinance"
        
        if summary and len(summary) > 200:
            source = "yFinance"
            return {
                "business_model": business_model,
                "strategy": strategy,
                "summary": summary,
                "swot": swot,
                "source": source
            }
    except Exception as e:
        print(f"[ERROR] ❌ yFinance fallback failed: {e}")

    return {
        "summary": "Summary unavailable.",
        "swot": "SWOT unavailable.",
        "source": "None"
    }
