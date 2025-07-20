# app/agents/peer_comparison_agent.py

import os
import yfinance as yf
import pandas as pd
import finnhub

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
