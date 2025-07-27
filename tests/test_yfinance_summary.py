import yfinance as yf

def get_business_summary(ticker: str):
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info

        summary = info.get("longBusinessSummary")
        if summary and isinstance(summary, str) and len(summary.strip()) > 50:
            print(f"\n[✅] Summary found for {ticker}:\n")
            print(summary.strip())
        else:
            print(f"\n[⚠️] No usable longBusinessSummary found for {ticker}.")
    except Exception as e:
        print(f"\n[❌] Error fetching summary for {ticker}: {e}")

if __name__ == "__main__":
    test_tickers = ["AAPL", "MS", "TSLA", "XYZQ"]  # XYZQ = non-existent test ticker
    for tkr in test_tickers:
        print(f"\n==== {tkr} ====")
        get_business_summary(tkr)
