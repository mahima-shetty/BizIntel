import os
import requests
from datetime import datetime
import json
from datetime import datetime
import os
from langchain_groq import ChatGroq

from dotenv import load_dotenv

load_dotenv(override=True)

# 🔒 Deterministic LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)

def _get_fmp_api_key() -> str:
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        raise ValueError("FMP_API_KEY not set in environment variables.")
    return api_key


def get_fmp_business_summary(ticker: str) -> str:
    try:
        api_key = _get_fmp_api_key()
        url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data and isinstance(data, list):
            return data[0].get("description", "No business description found.")
        else:
            return "No profile found for this ticker."
    except Exception as e:
        print(f"[ERROR] FMP profile fetch failed: {e}")
        return "⚠️ Unable to retrieve business summary."


def get_fmp_earnings_transcripts(ticker: str) -> list:
    try:
        api_key = _get_fmp_api_key()
        url = f"https://financialmodelingprep.com/stable/earnings-transcript-list?apikey={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [entry for entry in data if entry.get("symbol") == ticker.upper()] if isinstance(data, list) else []
    except Exception as e:
        print(f"[ERROR] FMP earnings transcript fetch failed: {e}")
        return []


def get_fmp_sec_filings(ticker: str, form_type: str = "8-K", from_date="2024-01-01", to_date=None, limit=100) -> list:
    try:
        api_key = _get_fmp_api_key()
        if not to_date:
            to_date = datetime.today().strftime("%Y-%m-%d")
        url = (
            f"https://financialmodelingprep.com/stable/sec-filings-search/form-type"
            f"?formType={form_type}&from={from_date}&to={to_date}&page=0&limit={limit}&apikey={api_key}"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [entry for entry in data if entry.get("symbol") == ticker.upper()] if isinstance(data, list) else []
    except Exception as e:
        print(f"[ERROR] FMP {form_type} filings fetch failed: {e}")
        return []


def get_fmp_sec_8k_filings(ticker: str, from_date="2024-01-01", to_date=None, limit=100) -> list:
    return get_fmp_sec_filings(ticker, form_type="8-K", from_date=from_date, to_date=to_date, limit=limit)


def get_fmp_sec_10k_filings(ticker: str, from_date="2024-01-01", to_date=None, limit=5) -> list:
    return get_fmp_sec_filings(ticker, form_type="10-K", from_date=from_date, to_date=to_date, limit=limit)





def get_fmp_data(ticker: str) -> dict:
    """
    Combines business summary, transcripts, 8-Ks and 10-Ks.
    Also saves results to a debug JSON file.
    """
    data = {
        "business_summary": get_fmp_business_summary(ticker),
        "earnings_transcripts": get_fmp_earnings_transcripts(ticker),
        "sec_8k_filings": get_fmp_sec_8k_filings(ticker),
        "sec_10k_filings": get_fmp_sec_10k_filings(ticker),
    }

    # Save to debug_outputs
    try:
        os.makedirs("debug_outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"debug_outputs/fmp_data_{ticker}_{timestamp}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"[DEBUG] 💾 FMP data saved to {filepath}")
    except Exception as e:
        print(f"[ERROR] Failed to save debug file: {e}")

    return data




def summarize_company_overview(input_data: dict) -> str:
    """
    Summarizes FMP + YFinance + 8-K + 10-K content into a unified business strategy.
    """
    try:
        prompt = f"""
You are a business analyst. Summarize the following information about a company into a clear strategic overview.

BUSINESS SUMMARY:
{input_data.get('business_summary', '')}

EARNINGS TRANSCRIPTS:
{input_data.get('earnings_transcripts', '')}

8-K FILINGS:
{input_data.get('sec_8k_filings', '')}

10-K FILINGS:
{input_data.get('sec_10k_filings', '')}

Format your answer in 2 sections:
- Overview of Business Model
- Key Strategic Priorities
        """.strip()

        result = llm.invoke(prompt)  # Use your preferred LLM chain
        return result.content.strip()
    except Exception as e:
        print(f"[ERROR] LLM overview summary failed: {e}")
        return "⚠️ Unable to generate company overview."


