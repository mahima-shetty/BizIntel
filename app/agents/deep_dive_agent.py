# app/agents/deep_dive_agent.py

from app.agents.snapshot_agent import get_company_snapshot
from app.agents.edgar_agent import get_business_model_and_strategy
import streamlit as st

def company_deep_dive(ticker: str) -> str:
    """Combines company snapshot and EDGAR analysis into a narrative output."""

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
    else:
        strategy_str = f"""
### 🧩 Business Model & Strategy (from 10-K)
{edgar_data.get("business_model", "Not available.")}

### 🧠 Summary for Easy Reading
{edgar_data.get("llm_summary", "Summary not available.")}
"""

    # Combine sections (outside the if-block)
    final_report = f"""
## 🔍 Company Deep Dive: {ticker}

{snapshot_str}

---

{strategy_str}
"""
    st.success("✅ Done! Business model and strategy ready.")
    return final_report.strip()
