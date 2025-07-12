import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str, period: str = "6mo", interval: str = "1d"):
    """
    Fetch historical stock data for a given ticker.
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        hist.reset_index(inplace=True)
        return hist
    except Exception as e:
        print(f"[ERROR] Failed to fetch stock data for {ticker}: {e}")
        return pd.DataFrame()

def get_kpi_summary(ticker: str):
    """
    Returns key financial KPIs for a company.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "Company": info.get("longName", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
            "PE Ratio": info.get("trailingPE", "N/A"),
            "EPS": info.get("trailingEps", "N/A"),
            "Dividend Yield": info.get("dividendYield", "N/A"),
            "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
            "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
            "Sector": info.get("sector", "N/A"),
            "Industry": info.get("industry", "N/A")
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch KPIs for {ticker}: {e}")
        return {}

def plot_stock_price_chart(df: pd.DataFrame, ticker: str):
    """
    Generate a line chart using Streamlit.
    """
    import streamlit as st
    if df.empty:
        st.warning(f"No data available for {ticker}")
        return

    st.line_chart(df.set_index("Date")["Close"])
