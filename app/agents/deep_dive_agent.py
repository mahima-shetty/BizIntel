# app/agents/deep_dive_agent.py
from app.agents.snapshot_agent import get_company_snapshot
from app.agents.edgar_agent import get_business_model_and_strategy
from app.agents.swot_agent import generate_swot_analysis  # ⬅️ You'll create this
import streamlit as st

def company_deep_dive(ticker: str) -> str:
    """Combines company snapshot, EDGAR, and SWOT into a narrative output."""

    # 1. Snapshot
    snapshot = get_company_snapshot(ticker)
    snapshot_str = f"""
### 📌 Company Snapshot - {snapshot['shortName']}
- **Ticker:** {snapshot['ticker']}
- **Sector:** {snapshot['sector']}
- **Industry:** {snapshot['industry']}
- **CEO:** {snapshot['CEO']}
- **Employees:** {snapshot['employees']}
- **Market Cap:** ${round(snapshot['marketCap'] / 1e9, 2)}B
- **Headquarters:** {snapshot['headquarters']}
- **Founded:** {snapshot['founded']}
"""

    # 2. Business Model + Strategy
    edgar_data = get_business_model_and_strategy(ticker)

    if not edgar_data:
        strategy_str = "⚠️ No EDGAR summary available for this company."
        swot = "⚠️ Cannot generate SWOT without strategy content."
    else:
        strategy_str = f"""
### 🧩 Business Model & Strategy (from 10-K)
{edgar_data.get("business_model", "Not available.")}

### 🧠 Summary for Easy Reading
{edgar_data.get("llm_summary", "Summary not available.")}
"""
        # 3. Generate SWOT
        swot = generate_swot_analysis(ticker, {
            "summary": edgar_data.get("llm_summary", ""),
            "sector": snapshot["sector"],
            "industry": snapshot["industry"]
        })

    # Final output
    final_report = f"""
## 🔍 Company Deep Dive: {ticker}

{snapshot_str}

---

{strategy_str}

---

### 🧭 SWOT Analysis
{swot}
"""
    st.success("✅ Done! Business model, strategy, and SWOT ready.")
    return final_report.strip()
