# tests/test_get_latest_10k_html_text_manual.py

import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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


def get_latest_10k_html_text(ticker: str, debug: bool = True) -> str:
    try:
        cik = get_cik_for_ticker(ticker)
        cik_no_zeros = str(int(cik))  # Remove leading zeros
        print(f"[INFO] ✅ CIK for {ticker}: {cik}")
        print(f"CIK no zeros: {cik_no_zeros}")

        # Step 1: Get recent filings
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        res = requests.get(submissions_url, headers=SEC_HEADERS)
        if res.status_code != 200:
            raise Exception(f"Failed to get submissions for CIK {cik}")
        data = res.json()

        filings = data.get("filings", {}).get("recent", {})
        accession_numbers = filings.get("accessionNumber", [])
        form_types = filings.get("form", [])

        acc_no_clean = None
        for form, acc in zip(form_types, accession_numbers):
            if form == "10-K":
                acc_no_clean = acc.replace("-", "")
                break

        if not acc_no_clean:
            raise Exception("No 10-K filing found.")

        # Step 2: Get index.json and primary .htm doc
        index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_clean}/index.json"
        print(f"Index URL: {index_url}")
        res = requests.get(index_url, headers=SEC_HEADERS)
        if res.status_code != 200:
            raise Exception("Filing index.json not found.")
        index_data = res.json()

        primary_doc = None
        for item in index_data.get("directory", {}).get("item", []):
            name = item["name"].lower()
            if name.endswith(".htm") and not name.startswith("exhibit"):
                primary_doc = item["name"]
                break

        if not primary_doc:
            raise Exception("No valid 10-K .htm file found.")

        doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_clean}/{primary_doc}"
        print(f"Final Link ::   {doc_url}")
        print(f"[INFO] ✅ Latest 10-K URL for {ticker}: {doc_url}")

        # Step 3: Fetch and clean HTML
        res = requests.get(doc_url, headers=SEC_HEADERS)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()

        raw_text = soup.get_text(separator="\n")

        
        if raw_text:
            os.makedirs("tests/debug_outputs", exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = f"tests/debug_outputs/raw_text_10k_{ticker}_{ts}.txt"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(raw_text)
            print(f"[DEBUG] Saved RAW_TEXT 10-K HTML text to {out_path}")
            
            
        # Remove XBRL & metadata garbage lines
        lines = raw_text.splitlines()
        clean_lines = []
        for line in lines:
            line = line.strip()

            # Skip numeric-only lines (e.g., CIKs)
            if re.fullmatch(r"\d{6,}", line):
                continue

            # Skip date lines
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", line):
                continue

            # Skip country codes like 'country:US', 'country:IN', etc.
            if re.fullmatch(r"country:[a-z]{2}", line.lower()):
                continue

            # Skip tags and metadata
            if re.search(r"(us-gaap|xbrli:|iso4217:|fasb\.org|ms:|srt:|dei:)", line.lower()):
                continue

            # Skip boolean/label junk
            if line.lower() in ("true", "false", "fy"):
                continue

            clean_lines.append(line)


        # Smart join: fix broken multi-line cells like "$\n168,413" => "$ 168,413"
        joined_lines = []
        buffer = ""

        def is_numeric_fragment(line):
            line = line.strip()
            return (
                re.fullmatch(r"\(?-?\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?%?", line)
                or line in ("(", ")", "$")
                or line.startswith("$")
            )

        for line in clean_lines:
            stripped = line.strip()

            if not stripped:
                continue

            # Continue building buffer if it's a broken numeric value
            if (
                buffer
                and is_numeric_fragment(stripped)
                and len(stripped) <= 10
            ):
                buffer += " " + stripped
            else:
                if buffer:
                    joined_lines.append(buffer.strip())
                buffer = stripped

        # Final flush
        if buffer:
            joined_lines.append(buffer.strip())



        # Join lines and remove excessive spacing
        text = "\n".join(joined_lines)
        text = re.sub(r"\n{2,}", "\n\n", text).strip()

        # Optional: drop trailing noise like '2024-12-31' at the end of the doc
        text = re.sub(r"(?:\n\d{4}-\d{2}-\d{2}){2,}$", "", text)



        # Step 4: Debug output
        if debug:
            os.makedirs("tests/debug_outputs", exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = f"tests/debug_outputs/10k_{ticker}_{ts}.txt"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"[DEBUG] Saved 10-K HTML text to {out_path}")

        return text

    except Exception as e:
        print(f"❌ ERROR fetching 10-K for {ticker}: {e}")
        return ""


def main():
    ticker = "AMZN"
    print(f"\n📥 Fetching latest 10-K for {ticker}...\n")
    result = get_latest_10k_html_text(ticker)

    if result:
        print(f"\n✅ Retrieved {len(result):,} characters of text.\n")
        print("=" * 80)
        print(result[:5000])  # Preview first few KBs
        print("=" * 80)
    else:
        print("❌ Failed to extract any text.")


if __name__ == "__main__":
    main()