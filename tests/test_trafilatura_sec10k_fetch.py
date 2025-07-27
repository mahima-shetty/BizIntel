import requests
from trafilatura import fetch_url, extract
import os
# from bizintel.utils.sec_utils import get_cik_for_ticker  # Adjust this import based on your structure

SEC_HEADERS = {
    "User-Agent": "BizIntel Research Bot (msshetty237@gmail.com)",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}




def get_cik_for_ticker(ticker: str) -> str:
    """Map ticker to CIK using SEC company_tickers.json"""
    url = "https://www.sec.gov/files/company_tickers.json"
    res = requests.get(url, headers=SEC_HEADERS)
    if res.status_code != 200:
        raise RuntimeError(f"❌ SEC response {res.status_code} — {res.text[:200]}")

    try:
        data = res.json()
    except Exception as e:
        raise RuntimeError(f"Failed to parse JSON: {e}")

    for entry in data.values():
        if entry["ticker"].lower() == ticker.lower():
            return str(entry["cik_str"]).zfill(10)

    raise ValueError(f"CIK not found for ticker: {ticker}")


def scrape_10k_with_trafilatura(ticker: str) -> str:
    try:
        # Step 1: Get CIK
        cik = get_cik_for_ticker(ticker)
        cik_padded = str(cik).zfill(10)
        cik_no_zeros = str(int(cik))  # remove leading zeros
        print(f"[INFO] ✅ CIK for {ticker}: {cik} -> {cik_padded}")

        # Step 2: Get recent filings
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
        res = requests.get(submissions_url, headers=SEC_HEADERS)
        res.raise_for_status()
        data = res.json()

        filings = data.get("filings", {}).get("recent", {})
        accession_numbers = filings.get("accessionNumber", [])
        form_types = filings.get("form", [])
        primary_docs = filings.get("primaryDocument", [])

        # Find latest 10-K
        acc_no_clean = None
        primary_doc = None
        for form, acc, doc in zip(form_types, accession_numbers, primary_docs):
            if form == "10-K":
                acc_no_clean = acc.replace("-", "")
                primary_doc = doc
                break

        if not acc_no_clean or not primary_doc:
            raise Exception("❌ No recent 10-K filing found.")

        # Optional: Try fetching index.json to confirm .htm
        index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_clean}/index.json"
        index_res = requests.get(index_url, headers=SEC_HEADERS)
        if index_res.status_code == 200:
            index_data = index_res.json()
            for item in index_data.get("directory", {}).get("item", []):
                name = item["name"].lower()
                if name.endswith(".htm") and not name.startswith("exhibit"):
                    primary_doc = item["name"]
                    break
        else:
            print(f"[WARN] ⚠ index.json not available, using: {primary_doc}")

        if not primary_doc:
            raise Exception("❌ Could not locate primary document URL.")

        doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_clean}/{primary_doc}"
        print(f"[INFO] 🔗 Final URL: {doc_url}")

        # Step 3: Fetch HTML manually with headers
        html_response = requests.get(doc_url, headers=SEC_HEADERS)
        html_response.raise_for_status()
        html_text = html_response.text

        # Step 4: Extract clean text using trafilatura
        extracted = extract(html_text, include_comments=False, include_tables=False)
        if not extracted or len(extracted) < 1000:
            raise Exception("❌ Extracted content too short or empty.")

        print(f"[INFO] ✅ Extracted length: {len(extracted)} chars")
            # Save to debug file under /tests/debug_outputs/


        debug_dir = "tests/debug_outputs"
        os.makedirs(debug_dir, exist_ok=True)

        debug_path = os.path.join(debug_dir, f"{ticker.upper()}_10k_trafilatura.txt")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(extracted)

        print(f"[DEBUG] ✅ Extracted 10-K saved to {debug_path}")
        return extracted

    except Exception as e:
        print(f"[ERROR] {e}")
        raise



# ✅ Run directly for testing
if __name__ == "__main__":
    ticker = "C"  # Change ticker for testing
    text = scrape_10k_with_trafilatura(ticker)
    print("\n--- START OF EXTRACTED TEXT ---\n")
    print(text[:3000])  # Print only first 3000 chars
    print("\n--- END OF EXTRACTED TEXT ---\n")
