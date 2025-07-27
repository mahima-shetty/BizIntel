# app/agents/deep_dive_agent.py

import os
from datetime import datetime

from app.agents.fmp_business_summary_agent import get_fmp_data, summarize_company_overview
from app.agents.researcher_summary_yfinance_agent import get_researcher_business_summary_from_yfinance
from app.agents.edgar_agent import get_business_model_and_strategy
from app.agents.swot_agent import generate_swot_analysis
from app.agents.snapshot_agent import get_company_snapshot


def company_deep_dive(ticker: str) -> str:
    """Full company deep dive using snapshot, FMP, Yahoo Finance, EDGAR, and SWOT."""

    # 1️⃣ Snapshot info
    snapshot = get_company_snapshot(ticker)
    market_cap = snapshot.get("marketCap", 0)
    market_cap_str = f"${round(market_cap / 1e9, 2)}B" if market_cap and market_cap > 0 else "N/A"

    snapshot_str = f"""
### 📌 Company Snapshot - {snapshot.get('shortName')}
- **Ticker:** {snapshot.get('ticker')}
- **Sector:** {snapshot.get('sector')}
- **Industry:** {snapshot.get('industry')}
- **CEO:** {snapshot.get('CEO')}
- **Employees:** {snapshot.get('employees')}
- **Market Cap:** {market_cap_str}
- **Headquarters:** {snapshot.get('headquarters')}
- **Founded:** {snapshot.get('founded')}
""".strip()

    # 2️⃣ FMP Data (Primary)
    fmp_data = get_fmp_data(ticker)
    fmp_summary = fmp_data.get("business_summary", "")
    earnings = fmp_data.get("earnings_transcripts", "")
    eight_ks = fmp_data.get("sec_8k_filings", "")
    ten_ks = fmp_data.get("sec_10k_filings", "")

    # 3️⃣ Yahoo Finance (Secondary)
    yfin_data = get_researcher_business_summary_from_yfinance(ticker)
    yfin_summary = yfin_data.get("business_model", "")

    # 4️⃣ EDGAR (Always include)
    edgar_data = get_business_model_and_strategy(ticker)
    edgar_summary = edgar_data.get("llm_summary", "")

    # 5️⃣ Summarize all content using LLM
    llm_input = {
        
        "edgar_summary": edgar_summary,
        "yahoo_finance_summary": yfin_summary,
        "business_summary": fmp_summary,
        "earnings_transcripts": earnings,
        "sec_8k_filings": eight_ks,
        "sec_10k_filings": ten_ks
    }

    try:
        final_summary = summarize_company_overview(llm_input)
    except Exception as e:
        print(f"[ERROR] LLM summarization failed: {e}")
        # Fallback to concatenated version
        final_summary = f"""
From EDGAR:
{edgar_summary or '⚠️ Not available.'}

From FMP:
{fmp_summary or '⚠️ Not available.'}

From Yahoo Finance:
{yfin_summary or '⚠️ Not available.'}
""".strip()

    strategy_str = f"""
### 🧩 Business Model & Strategy

{final_summary}
""".strip()





    # 6️⃣ SWOT using LLM summary
    swot = generate_swot_analysis(ticker, {
        "summary": final_summary,
        "sector": snapshot.get("sector"),
        "industry": snapshot.get("industry")
    })







    # 🧾 Final assembled report
    full_report = f"""
🔍 Company Deep Dive: {ticker}

{snapshot_str}

---

{strategy_str}

---

### 🧭 SWOT Analysis
{swot}
""".strip()

    print(f"[SUCCESS] Deep dive generated for {ticker}")
    return full_report
