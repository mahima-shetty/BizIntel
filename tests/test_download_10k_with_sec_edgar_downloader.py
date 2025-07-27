import os
import re
from datetime import datetime
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup


def get_latest_10k_text(ticker: str, debug: bool = True) -> str:
    dl = Downloader(company_name="BizIntel", email_address="msshetty237@gmail.com")
    print(f"[INFO] 🔽 Downloading latest 10-K for {ticker}...")
    dl.get("10-K", ticker, limit=1)

    base_path = f"sec-edgar-filings/{ticker}/10-K/"
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"{base_path} not found")

    folders = sorted(os.listdir(base_path), reverse=True)
    for folder in folders:
        path = os.path.join(base_path, folder, "full-submission.txt")
        if not os.path.exists(path):
            continue

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()

        raw_text = soup.get_text(separator="\n")

        # Clean lines
        lines = raw_text.splitlines()
        clean_lines = []
        for line in lines:
            line = line.strip()

            if not line or line.lower() in ("true", "false", "fy"):
                continue

            if re.fullmatch(r"\d{6,}", line):  # numeric only
                continue

            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", line):  # date
                continue

            if re.fullmatch(r"country:[a-z]{2}", line.lower()):
                continue

            if re.search(r"(us-gaap|xbrli:|iso4217:|fasb\.org|ms:|srt:|dei:)", line.lower()):
                continue

            clean_lines.append(line)

        # Merge broken numeric lines (e.g. "$\n168,413")
        joined_lines = []
        buffer = ""

        def is_numeric_fragment(fragment):
            return (
                re.fullmatch(r"\(?-?\d{1,3}(,\d{3})*(\.\d+)?\)?%?", fragment)
                or fragment.strip() in ("(", ")", "$")
                or fragment.strip().startswith("$")
            )

        for line in clean_lines:
            stripped = line.strip()
            if not stripped:
                continue

            if buffer and is_numeric_fragment(stripped) and len(stripped) <= 10:
                buffer += " " + stripped
            else:
                if buffer:
                    joined_lines.append(buffer.strip())
                buffer = stripped

        if buffer:
            joined_lines.append(buffer.strip())

        final_text = "\n".join(joined_lines)
        final_text = re.sub(r"\n{2,}", "\n\n", final_text).strip()
        final_text = re.sub(r"(?:\n\d{4}-\d{2}-\d{2}){2,}$", "", final_text)

        if debug:
            os.makedirs("tests/debug_outputs", exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"tests/debug_outputs/10k_cleaned_{ticker}_{ts}.txt"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_text)
            print(f"[DEBUG] ✅ Cleaned 10-K saved to: {output_path}")

        return final_text

    raise RuntimeError(f"No valid 10-K found in: {base_path}")


def main():
    ticker = "BAC"
    print(f"\n📥 Fetching latest 10-K for {ticker}...\n")
    result = get_latest_10k_text(ticker)

    if result:
        print(f"\n✅ Retrieved {len(result):,} characters of text.\n")
        print("=" * 80)
        print(result[:5000])
        print("=" * 80)
    else:
        print("❌ Failed to extract any text.")


if __name__ == "__main__":
    main()
