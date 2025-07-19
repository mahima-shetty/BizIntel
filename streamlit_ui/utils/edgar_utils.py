import os
import re
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup

dl = Downloader(company_name="BizIntel", email_address="msshetty237@gmail.com")


# def extract_item_section(text: str, start_header: str, end_header: str) -> str:
#     """
#     Extracts the content between two headers from EDGAR filings,
#     skipping TOC matches by picking the longest match.
#     Cleans the first line if it’s a header/title.
#     """
#     def normalize(header: str) -> str:
#         header = re.escape(header)
#         header = header.replace(r'\.', r'\.?\s*')   # optional period + flexible space
#         header = header.replace(r'\ ', r'\s+')      # normalize all spaces
#         return header

#     start_pattern = normalize(start_header)
#     end_pattern = normalize(end_header)
#     pattern = rf"{start_pattern}(.*?){end_pattern}"

#     matches = list(re.finditer(pattern, text, re.IGNORECASE | re.DOTALL))

#     if not matches:
#         print(f"[WARN] No match found for: {start_header} → {end_header}")
#         return ""

#     section = max(matches, key=lambda m: len(m.group(1))).group(1).strip()

#     # Clean header lines if present
#     lines = section.splitlines()
#     if lines and any(kw in lines[0].lower() for kw in ["item", "business", "discussion", "risk", "overview", "table of contents"]):
#         lines = lines[1:]

#     return "\n".join(lines).strip()


def extract_item_section(text: str, start_header: str, end_header: str) -> str:
    """
    Extract content between two headers (start → end) from EDGAR filings.
    Ignores early matches like Table of Contents.
    Cleans out TOC artifacts at top of section.
    """
    def normalize(header: str) -> str:
        header = re.escape(header)
        header = header.replace(r'\.', r'\.?\s*')  # optional period
        header = header.replace(r'\ ', r'\s+')     # flexible spaces
        return header

    start_pattern = normalize(start_header)
    end_pattern = normalize(end_header)

    start_matches = list(re.finditer(start_pattern, text, re.IGNORECASE))
    end_matches = list(re.finditer(end_pattern, text, re.IGNORECASE))

    if not start_matches or not end_matches:
        print(f"[WARN] No matches found for: {start_header} → {end_header}")
        return ""

    # Find the LAST start header before the first valid end header that comes after it
    valid_sections = []
    for s in reversed(start_matches):
        for e in end_matches:
            if e.start() > s.end():
                section_text = text[s.end():e.start()].strip()
                valid_sections.append((s, e, section_text))
                break  # only first end match after this start

    if not valid_sections:
        print(f"[WARN] No valid section found between {start_header} → {end_header}")
        return ""

    # Pick the longest real section (not TOC-based)
    _, _, section = max(valid_sections, key=lambda tup: len(tup[2]))

    lines = section.splitlines()

    def is_toc_line(line: str) -> bool:
        line = line.strip().lower()
        return (
            re.match(r"^\d{1,3}$", line) or
            re.match(r".{1,50}\.{2,}\s*\d+$", line) or
            re.match(r"^(overview|business|competition|loan|deposit|segment|summary|regulation|portfolio|assets|liabilities)$", line)
        )

    # Skip leading TOC-like lines
        # Remove leading TOC garbage until we hit a real sentence
    cleaned_lines = []
    seen_real_content = False

    for line in lines:
        stripped = line.strip()

        # Skip empty or short TOC-style lines
        if not seen_real_content:
            if (
                stripped == ""
                or re.match(r"^\d{1,3}$", stripped)
                or re.search(r"[—–\-]\s*\d{1,4}$", stripped)  # "Supervision — 3"
                or len(stripped.split()) <= 6  # e.g., "Short-term and other borrowed funds"
            ):
                continue

            # Detect start of real content (first full sentence-ish line)
            if re.match(r"^[A-Z][^.]{20,200}\.$", stripped):
                seen_real_content = True
                cleaned_lines.append(stripped)
        else:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()





def truncate_to_sentence(text: str, max_chars: int = 3000) -> str:
    """
    Truncate text to max_chars, ending cleanly at the last full sentence.
    """
    if len(text) <= max_chars:
        return text.strip()

    truncated = text[:max_chars]
    last_period = truncated.rfind(".")
    if last_period != -1:
        return truncated[:last_period + 1].strip()

    last_space = truncated.rfind(" ")
    if last_space != -1:
        return truncated[:last_space].strip()

    return truncated.strip()


def clean_strategy_section(text: str) -> str:
    """
    Skips forward-looking disclaimers and starts from 'Overview' when present.
    """
    idx = text.lower().find("overview")
    return text[idx:].strip() if idx != -1 else text


def clean_html(text: str) -> str:
    """
    Strips all HTML tags and inline styling from text.
    """
    return BeautifulSoup(text, "html.parser").get_text(separator="\n")


def _get_latest_10k_text(ticker: str) -> str:
    """
    Downloads and parses the latest 10-K filing text from EDGAR.
    """
    try:
        dl.get("10-K", ticker)

        base_path = f"sec-edgar-filings/{ticker}/10-K/"
        if not os.path.exists(base_path):
            raise FileNotFoundError(f"{base_path} not found")

        subfolders = sorted(os.listdir(base_path), reverse=True)
        for folder in subfolders:
            txt_path = os.path.join(base_path, folder, "full-submission.txt")
            if os.path.exists(txt_path):
                with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                    html = f.read()
                    soup = BeautifulSoup(html, "html.parser")
                    for tag in soup(["script", "style"]):
                        tag.decompose()
                    return soup.get_text(separator="\n")

        return ""

    except Exception as e:
        print(f"[EDGAR ERROR] {e}")
        return ""


def get_edgar_summary(ticker: str) -> dict:
    """
    Returns a merged 'business_strategy' section and risks from the latest 10-K.
    """
    text = _get_latest_10k_text(ticker)
    if not text:
        print("[DEBUG] No 10-K text found.")
        return {}

    print("🧪 Scanning for key section headers...")
    for line in text.splitlines():
        if "item" in line.lower():
            print(line.strip())

    # Extract raw sections
    business_raw = extract_item_section(text, "Item 1. Business", "Item 1A.")
    strategy_raw = extract_item_section(text, "Item 7.", "Item 7A.")

    # Clean and merge
    business_clean = clean_html(business_raw)
    strategy_clean = clean_strategy_section(clean_html(strategy_raw))

    merged = business_clean.strip() + "\n\n" + strategy_clean.strip()

    return {
        "business_strategy": truncate_to_sentence(merged, 3000),
        "risks": truncate_to_sentence(
            clean_html(extract_item_section(text, "Risk Factors", "Unresolved Staff Comments")),
            3000
        )
    }

