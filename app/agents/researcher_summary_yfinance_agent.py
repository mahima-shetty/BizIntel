import yfinance as yf
import os
from datetime import datetime

def get_researcher_business_summary_from_yfinance(ticker: str) -> dict:
    """
    Fetches the long business summary from Yahoo Finance for the Researcher Dashboard.
    Saves output to debug_outputs/ for inspection.
    """
    try:
        info = yf.Ticker(ticker).info
        summary = info.get("longBusinessSummary")

        if summary and isinstance(summary, str) and len(summary.strip()) > 50:
            cleaned_summary = summary.strip()

            # 🔽 Save to debug_outputs/
            os.makedirs("debug_outputs", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_path = f"debug_outputs/yfinance_summary_{ticker}_{timestamp}.txt"

            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(cleaned_summary)

            print(f"[DEBUG] ✅ Saved Yahoo summary to: {debug_path}")

            return {
                "business_model": cleaned_summary,
                "llm_summary": cleaned_summary
            }
        else:
            print(f"[⚠️] No usable longBusinessSummary for {ticker}.")
            return {}
    except Exception as e:
        print(f"[❌] Failed to fetch Yahoo summary for {ticker}: {e}")
        return {}
