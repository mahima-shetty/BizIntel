# app/agents/snapshot_agent.py

import yfinance as yf

def get_company_snapshot(ticker: str) -> dict:
    try:
        company = yf.Ticker(ticker)
        info = company.info

        return {
        "shortName": info.get("shortName", "N/A"),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "CEO": info.get("CEO", "N/A"),
        "employees": info.get("fullTimeEmployees", "N/A"),
        "ticker": ticker,
        "marketCap": round(info["marketCap"] / 1e9, 2) if isinstance(info.get("marketCap"), (int, float)) and info["marketCap"] > 0 else None,
        "headquarters": f"{info.get('city', 'N/A')}, {info.get('state', '')}",
        "founded": info.get("founded", "N/A")
    }

    
    except Exception as e:
        print(f"[Snapshot Agent] Error fetching data for {ticker}: {e}")
        return {
            "shortName": "N/A",
            "sector": "N/A",
            "industry": "N/A",
            "CEO": "N/A",
            "employees": "N/A",
            "ticker": ticker,
            "marketCap": 0,
            "headquarters": "N/A",
            "founded": "N/A"
        }
