# llm_10k_summarizer.py

import os
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.agents.llm_10k_prompts import chunk_analysis_prompt, refinement_prompt
import concurrent
import time
import streamlit as st
from dotenv import load_dotenv
load_dotenv(override=True)


# 🔗 Load LLaMA 3 model from Groq
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)

parser = StrOutputParser()

def clean_html_10k(filepath: str) -> str:
    """
    Loads and strips unwanted tags from a 10-K HTML file.
    Returns plain readable text.
    """
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "table", "td", "th"]):
        tag.decompose()

    return soup.get_text(separator="\n")


def split_into_chunks(text: str, chunk_size: int = 9000, overlap: int = 500):
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]

        # Cut at last period to avoid mid-sentence cuts
        last_period = chunk.rfind(".")
        if last_period != -1 and last_period > 2000:
            chunk = chunk[:last_period + 1]

        chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks


# # 📄 Prompt for chunk-level summarization
# chunk_analysis_prompt = PromptTemplate.from_template("""
# You're a financial analyst reviewing a portion of a 10-K filing.

# Your task:
# - Identify what the company does (its business model)
# - Highlight strategic priorities or growth goals

# If the content appears incomplete, summarize what is available.

# ---
# {text}
# """)


# # 🧾 Final prompt to polish and simplify combined notes
# refinement_prompt = PromptTemplate.from_template("""
# Here are rough draft notes extracted from a company's 10-K filing.

# Write a clean, layman-friendly summary that covers:
# - What the company does (its business model)
# - What strategies or goals it's pursuing

# Return your output in clear, point-wise bullet format.

# ---
# {notes}
# """)
import time

def process_chunk(chunk, idx, total):
    print(f"🧠 Processing chunk {idx+1}/{total}...")
    try:
        chain = chunk_analysis_prompt | llm | parser
        result = chain.invoke({"text": chunk})
        time.sleep(100)  # ← pause 5 seconds between requests
        return result
    except Exception as e:
        print(f"[ERROR] Chunk failed: {e}")
        return None




def summarize_10k_text(raw_text: str) -> str:
    """
    Cleans and chunks a full 10-K filing, extracts business strategy insights using LLM.
    Returns a readable plain-English bullet point summary.
    """
    # ⛏️ Step 1: Clean garbage lines (short, digits, TOC noise)
    lines = raw_text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()

        if not line or len(line) < 30 or line.isdigit():
            continue

        if any(kw in line.lower() for kw in [
            "table of contents", "see note", "unaudited", "amount", "year ended", "page ", "item "
        ]):
            continue

        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    # 🔪 Step 2: Chunk for LLM
    chunks = split_into_chunks(cleaned_text, chunk_size=9000, overlap=500)[:20]
    


    # Optional: Limit to top N chunks if needed (e.g. for speed during dev)
    # chunks = chunks[:25]  # Uncomment for limiting during testing

    print(f"[INFO] 🔹 Total usable chunks: {len(chunks)}")

    summaries = []

    # 🤖 Step 3: Extract partial insights
    # for idx, chunk in enumerate(chunks):
    #     print(f"🧠 Processing chunk {idx + 1}/{len(chunks)}...")
    #     try:
    #         chain = chunk_analysis_prompt | llm | parser
    #         result = chain.invoke({"text": chunk})
    #         summaries.append(result.strip())
    #     except Exception as e:
    #         print(f"[ERROR] Failed on chunk {idx + 1}: {e}")
    #         continue

    # if not summaries:
    #     return "⚠️ No meaningful content extracted from the 10-K."
    
    
    summaries = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_chunk, chunk, idx, len(chunks)) for idx, chunk in enumerate(chunks)]
        for future in concurrent.futures.as_completed(futures):
            try:
                summaries.append(future.result())
            except Exception as e:
                print(f"[ERROR] Chunk failed: {e}")
                continue
    if not summaries:
        return "⚠️ No meaningful content extracted from the 10-K."

    combined_notes = "\n\n".join(summaries)
    combined_notes = combined_notes[:22000]
    
    
    # 🧠 Step 4: Refine to final summary
    final_chain = refinement_prompt | llm | parser
    try:
        final_summary = final_chain.invoke({"notes": combined_notes})
        return final_summary.strip()
    except Exception as e:
        print(f"[ERROR] Final summarization failed: {e}")
        return "⚠️ Unable to generate summary from extracted notes."

