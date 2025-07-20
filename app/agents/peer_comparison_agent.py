# app/agents/peer_comparison_agent.py

import os
import yfinance as yf
import pandas as pd
import finnhub
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Setup Finnhub client
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

# Define metrics to extract
METRICS = {
    "Market Cap": lambda info: info.get("marketCap"),
    "P/E Ratio": lambda info: info.get("trailingPE"),
    "EPS": lambda info: info.get("trailingEps"),
    "Revenue (TTM)": lambda info: info.get("totalRevenue"),
    "Net Income (TTM)": lambda info: info.get("netIncomeToCommon") or info.get("netIncome"),
    "Return on Equity": lambda info: info.get("returnOnEquity"),
}



llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)

peer_summary_prompt = PromptTemplate.from_template("""
You are a financial analyst assistant. Here is a table comparing financial metrics of a company and its peers:

{table}

Write a brief, plain-English summary of how the main company ({ticker}) compares to its peers. Focus on areas of strength and weakness. Avoid speculation. Make it suitable for a business intelligence dashboard.
""")


def _format_value(val):
    if val is None:
        return "—"
    if isinstance(val, (int, float)):
        if abs(val) > 1e9:
            return f"${val / 1e9:.1f}B"
        elif abs(val) > 1e6:
            return f"${val / 1e6:.1f}M"
        else:
            return f"{val:.2f}"
    return str(val)


def get_peer_comparison(ticker: str, sort_by: str = "Market Cap") -> pd.DataFrame:
    """
    Returns a DataFrame comparing the given ticker with its peers.
    Peers are fetched from Finnhub, data from yfinance.
    """
    try:
        peers = finnhub_client.company_peers(ticker.upper())
    except Exception as e:
        print(f"[ERROR] Finnhub peer fetch failed for {ticker}: {e}")
        peers = []

    if not peers:
        print(f"[INFO] No peers found for {ticker}, using only the main ticker.")
        peers = []

    ticker_upper = ticker.upper()
    peers = [p for p in peers if p != ticker_upper]  # remove self if present
    peer_list = [ticker_upper] + peers[:4]  # keep main ticker first


    data = []
    for t in peer_list:
        try:
            info = yf.Ticker(t).info
            row = {"Ticker": t, "Short Name": info.get("shortName", t)}
            for metric, extractor in METRICS.items():
                row[metric] = extractor(info)
            data.append(row)
        except Exception as e:
            print(f"[WARN] Failed to fetch yfinance data for {t}: {e}")
            continue

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    if sort_by in df.columns:
        df = df.sort_values(by=sort_by, ascending=False, na_position="last")

    return df


def get_formatted_peer_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a formatted version of the peer comparison DataFrame.
    """
    if df.empty:
        return df

    fmt_df = df.copy()

    for col in ["Market Cap", "Revenue (TTM)", "Net Income (TTM)"]:
        if col in fmt_df.columns:
            fmt_df[col] = fmt_df[col].apply(_format_value)

    if "Return on Equity" in fmt_df.columns:
        fmt_df["Return on Equity"] = fmt_df["Return on Equity"].apply(
            lambda x: f"{x*100:.1f}%" if isinstance(x, (float, int)) else "—"
        )

    return fmt_df


    
def generate_peer_comparison_insight(ticker: str, df: pd.DataFrame) -> str:
    import os
    from langchain_groq import ChatGroq
    from langchain_core.output_parsers import StrOutputParser

    if not isinstance(df, pd.DataFrame) or df.empty:
        print("[DEBUG] Peer DataFrame is empty or invalid.")
        return "⚠️ No valid peer data available for analysis."

    try:
        company_name = df.loc[df["Ticker"] == ticker.upper(), "Short Name"].values[0]
    except IndexError:
        company_name = ticker.upper()
    print(f"[DEBUG] Generating insight for: {company_name} ({ticker})")

    summary = f"## Peer Comparison Data for {company_name} ({ticker.upper()})\n\n"
    try:
        summary += df.to_markdown(index=False)
    except Exception as e:
        print(f"[ERROR] Markdown formatting failed: {e}")
        return f"⚠️ Failed to format peer data for LLM: {e}"

    prompt = f"""
You are a financial analyst. Based on the peer comparison table below, write a short paragraph summarizing how {company_name} compares to its competitors.

Focus on whether it outperforms or underperforms in key areas like:
- Valuation (P/E)
- Profitability (Return on Equity)
- Revenue
- Earnings

Do not repeat the table — just summarize insights.

{summary}
"""

    try:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-70b-8192",
            temperature=0,
        )
        parser = StrOutputParser()
        chain = llm | parser

        print("[DEBUG] Sending prompt to LLM...")
        result = chain.invoke(prompt)
        print("[DEBUG] LLM response received.")

        if not result or not result.strip():
            print("[DEBUG] LLM returned empty result.")
            return "⚠️ LLM returned no insight."
        
        print("[DEBUG] LLM Output Preview:\n", repr(result))
        return result.strip()

    except Exception as e:
        print(f"[ERROR] LLM generation failed: {e}")
        return f"⚠️ Error generating insight: {e}"

