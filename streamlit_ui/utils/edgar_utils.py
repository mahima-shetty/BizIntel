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
    url = "https://www.sec.gov/files/company_tickers.json"
    res = requests.get(url, headers=SEC_HEADERS)
    res.raise_for_status()
    data = res.json()
    for entry in data.values():
        if entry["ticker"].lower() == ticker.lower():
            return str(entry["cik_str"]).zfill(10)
    raise ValueError(f"CIK not found for ticker: {ticker}")


def _get_latest_10k_text(ticker: str) -> str:
    try:
        cik = get_cik_for_ticker(ticker)
        cik_no_zeros = str(int(cik))
        print(f"[INFO] ✅ CIK for {ticker}: {cik}")

        # Step 1: Get recent filings
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        res = requests.get(submissions_url, headers=SEC_HEADERS)
        res.raise_for_status()
        filings = res.json().get("filings", {}).get("recent", {})
        accession_numbers = filings.get("accessionNumber", [])
        form_types = filings.get("form", [])

        acc_no_clean = None
        for form, acc in zip(form_types, accession_numbers):
            if form == "10-K":
                acc_no_clean = acc.replace("-", "")
                break

        if not acc_no_clean:
            raise Exception("No 10-K filing found.")

        # Step 2: Get index.json
        index_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_clean}/index.json"
        res = requests.get(index_url, headers=SEC_HEADERS)
        res.raise_for_status()
        index_data = res.json()

        primary_doc = None
        for item in index_data.get("directory", {}).get("item", []):
            name = item["name"].lower()
            if name.endswith(".htm") and not name.startswith("exhibit"):
                primary_doc = item["name"]
                break

        if not primary_doc:
            raise Exception("No valid .htm doc found.")

        doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_zeros}/{acc_no_clean}/{primary_doc}"
        print(f"[INFO] ✅ 10-K HTML URL: {doc_url}")

        # Step 3: Download and parse HTML
        res = requests.get(doc_url, headers=SEC_HEADERS)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()

        raw_text = soup.get_text(separator="\n")

        # Step 4: Remove metadata
        lines = raw_text.splitlines()
        clean_lines = []
        for line in lines:
            line = line.strip()

            if not line:
                continue

            if re.fullmatch(r"\d{6,}", line):  # numeric only (CIK etc.)
                continue
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", line):  # date
                continue
            if re.fullmatch(r"country:[a-z]{2}", line.lower()):
                continue
            if re.search(r"(us-gaap|xbrli:|iso4217:|fasb\.org|ms:|srt:|dei:)", line.lower()):
                continue
            if line.lower() in ("true", "false", "fy"):
                continue

            clean_lines.append(line)

        # Step 5: Rejoin broken numeric lines
        joined_lines = []
        buffer = ""

        def is_numeric_fragment(x):
            return (
                re.fullmatch(r"\(?-?\d{1,3}(,\d{3})*(\.\d+)?\)?%?", x)
                or x in ("$", "(", ")")
                or x.startswith("$")
            )

        for line in clean_lines:
            if buffer and is_numeric_fragment(line.strip()):
                buffer += " " + line.strip()
            else:
                if buffer:
                    joined_lines.append(buffer.strip())
                buffer = line.strip()
        if buffer:
            joined_lines.append(buffer.strip())

        text = "\n".join(joined_lines)
        text = re.sub(r"\n{2,}", "\n\n", text)
        text = re.sub(r"(?:\n\d{4}-\d{2}-\d{2}){2,}$", "", text).strip()

        # Step 6: Save output
        os.makedirs("debug_outputs", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"debug_outputs/10k_{ticker}_{ts}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"[DEBUG] Saved cleaned 10-K to {path}")

        return text

    except Exception as e:
        print(f"❌ ERROR fetching 10-K for {ticker}: {e}")
        return ""
