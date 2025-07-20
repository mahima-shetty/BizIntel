# app/agents/industry_benchmarks_agent.py

import pandas as pd
from app.agents.peer_comparison_agent import get_peer_comparison

def compute_industry_benchmarks(ticker: str) -> pd.DataFrame:
    """
    Compute median industry metrics based on peer comparison.
    Returns a DataFrame with Company vs. Peer Median side-by-side.
    """
    raw_df = get_peer_comparison(ticker)
    if raw_df.empty or len(raw_df) < 2:
        return pd.DataFrame()

    metrics = [
        "Market Cap", "P/E Ratio", "EPS",
        "Revenue (TTM)", "Net Income (TTM)", "Return on Equity"
    ]

    # Separate target company
    company_row = raw_df[raw_df["Ticker"] == ticker.upper()].iloc[0]
    peer_df = raw_df[raw_df["Ticker"] != ticker.upper()]

    data = []
    for metric in metrics:
        company_val = company_row.get(metric)
        peer_vals = peer_df[metric].dropna()
        median_val = peer_vals.median() if not peer_vals.empty else None

        data.append({
            "Metric": metric,
            "Company": company_val,
            "Peer Median": median_val  # Label updated here
        })

    return pd.DataFrame(data)


