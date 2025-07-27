from sec_edgar_downloader import Downloader
import os

def fetch_10k_text(ticker: str) -> str:
    # Step 1: Download 10-K
    dl = Downloader(company_name='BizIntel', email_address='msshetty237@gmail.com')
    print(f"[INFO] 🔽 Downloading latest 10-K for {ticker}...")
    dl.get("10-K", ticker, limit=1)

    # Step 2: Locate the downloaded file path
    filing_dir = f"sec-edgar-filings/{ticker}/10-K/"
    subfolders = sorted(os.listdir(filing_dir), reverse=True)
    if not subfolders:
        raise Exception("No 10-K filings found for this ticker.")

    latest_filing = subfolders[0]
    full_submission_path = os.path.join(filing_dir, latest_filing, "full-submission.txt")

    # Step 3: Read the content
    with open(full_submission_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return content

if __name__ == "__main__":
    ticker = "MS"  # Try "AAPL" or "AMZN" too
    content = fetch_10k_text(ticker)
    
    print("[INFO] ✅ Successfully fetched 10-K content.")
    print(content[:2000])  # Print first 2000 chars for preview
