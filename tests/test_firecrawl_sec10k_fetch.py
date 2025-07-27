import os
import time
import requests
from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv(override=True)
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

SEC_HEADERS = {
    "User-Agent": "BizIntel Research Bot (msshetty237@gmail.com)",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

def get_cik(ticker: str) -> str:
    url = "https://www.sec.gov/files/company_tickers.json"
    res = requests.get(url, headers=SEC_HEADERS)
    res.raise_for_status()
    for entry in res.json().values():
        if entry["ticker"].lower() == ticker.lower():
            cik = str(entry["cik_str"]).zfill(10)
            print(f"[INFO] ✅ CIK for {ticker}: {cik}")
            return cik
    raise ValueError(f"[ERROR] CIK not found for ticker: {ticker}")

def get_10k_htm_url(ticker: str) -> str:
    cik = get_cik(ticker)
    cik_no_zeros = str(int(cik))
    submission_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    res = requests.get(submission_url, headers=SEC_HEADERS)
    res.raise_for_status()

    filings = res.json().get("filings", {}).get("recent", {})
    for form, acc_no in zip(filings.get("form", []), filings.get("accessionNumber", [])):
        if form == "10-K":
            acc_no_clean = acc_no.replace("-", "")
            break
    else:
        raise RuntimeError("❌ No 10-K found")

    index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_clean}/index.json"
    print(f"[DEBUG] Index URL: {index_url}")
    res = requests.get(index_url, headers=SEC_HEADERS)
    res.raise_for_status()

    for item in res.json().get("directory", {}).get("item", []):
        name = item["name"].lower()
        if name.endswith(".htm") and "10-k" in name and not name.startswith("exhibit"):
            url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_clean}/{item['name']}"
            print(f"[INFO] ✅ Latest 10-K URL for {ticker}: {url}")
            return url

    # Fallback
    for item in res.json().get("directory", {}).get("item", []):
        name = item["name"].lower()
        if name.endswith(".htm") and not name.startswith("exhibit"):
            url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_clean}/{item['name']}"
            print(f"[INFO] ⚠️ Fallback 10-K URL: {url}")
            return url

    raise RuntimeError("❌ Could not find any valid 10-K HTML document.")

def crawl_10k_with_firecrawl(ticker: str):
    firecrawl = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
    url = get_10k_htm_url(ticker)
    response = firecrawl.crawl_url(url=url)

    crawl_id = getattr(response, "crawl_id", None)
    if not crawl_id:
        raise RuntimeError("❌ Firecrawl crawl_id missing in response")

    print(f"[INFO] 🕒 Started crawl: ID {crawl_id}")

    for _ in range(10):
        result = firecrawl.get_crawl_result(crawl_id)
        status = result.status.upper()
        if status == "COMPLETED":
            print("[INFO] ✅ Crawl complete.")
            content = result.content or ""
            break
        elif status == "FAILED":
            raise RuntimeError("❌ Crawl failed.")
        else:
            print("[INFO] ⏳ Waiting for crawl to finish...")
            time.sleep(3)
    else:
        raise TimeoutError("⏰ Crawl timed out.")

    # Save outputs
    os.makedirs("debug_firecrawl", exist_ok=True)
    html_path = f"debug_firecrawl/{ticker}_10k.html"
    log_path = f"debug_firecrawl/{ticker}_log.txt"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Ticker: {ticker}\n")
        f.write(f"CIK: {get_cik(ticker)}\n")
        f.write(f"Final URL: {url}\n")
        f.write(f"Crawl ID: {crawl_id}\n")
        f.write(f"Status: {status}\n")

    print(f"[INFO] ✅ Saved output: {html_path} and {log_path}")

if __name__ == "__main__":
    crawl_10k_with_firecrawl("MS")
