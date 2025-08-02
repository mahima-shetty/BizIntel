import os
import re
import time
import nltk
import streamlit as st
import concurrent.futures
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.agents.llm_10k_prompts import chunk_analysis_prompt, refinement_prompt

load_dotenv(override=True)
import nltk

# Check if 'punkt' is already downloaded
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")
    
from nltk.tokenize import sent_tokenize

# Load LLaMA 3 model
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)
parser = StrOutputParser()

def clean_html_10k(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "table", "td", "th"]):
        tag.decompose()
    return soup.get_text(separator="\n")


def split_by_sentences(text: str, sentences_per_chunk: int = 40):
    sentences = sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk - 5):  # overlap 5
        chunk = " ".join(sentences[i:i + sentences_per_chunk])
        chunks.append(chunk.strip())
    return chunks


def process_chunk(chunk, idx, total):
    print(f"🧠 Processing chunk {idx+1}/{total}...")
    try:
        chain = chunk_analysis_prompt | llm | parser
        result = chain.invoke({"text": chunk})
        time.sleep(5)  # throttle to avoid Groq rate limits
        # Debug dump
        with open(f"debug_outputs/chunk_summary_{idx:02d}.txt", "w", encoding="utf-8") as f:
            f.write("INPUT CHUNK:\n" + chunk)
            f.write("\n\nLLM OUTPUT:\n" + result)
        return result
    except Exception as e:
        print(f"[ERROR] Chunk {idx+1} failed: {e}")
        return None


def summarize_10k_text(raw_text: str) -> str:
    # Clean & filter
    lines = raw_text.splitlines()
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if (
            not line
            or line.isdigit()
            or re.match(r"^[\d\s\.\$,()%]+$", line)
            or re.fullmatch(r"\d{4}-\d{2}-\d{2}", line)
            or re.search(r"^country:", line.lower())
            or any(kw in line.lower() for kw in ["unaudited", "table of contents", "page ", "item ", "see note"])
        ):
            continue
        cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)
    os.makedirs("debug_outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cleaned_path = f"debug_outputs/10k_cleaned_{timestamp}.txt"
    with open(cleaned_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)
    print(f"[DEBUG] 🧹 Cleaned 10-K text saved to: {cleaned_path}")

    # Chunking
    MAX_CHUNKS = 10
    chunks = split_by_sentences(cleaned_text, 40)[:MAX_CHUNKS]
    print(f"[INFO] 🧩 Processing {len(chunks)} chunks")

    summaries = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_chunk, chunk, idx, len(chunks)) for idx, chunk in enumerate(chunks)]
        for future in concurrent.futures.as_completed(futures):
            try:
                summaries.append(future.result())
            except Exception as e:
                print(f"[ERROR] Chunk processing failed: {e}")

    if not summaries:
        return "⚠️ No meaningful content extracted from the 10-K."

    # Combine summaries
    combined_notes = "\n\n".join(summaries)
    combined_summary_path = f"debug_outputs/10k_COMBINED_SUMMARY_{timestamp}.txt"
    with open(combined_summary_path, "w", encoding="utf-8") as f:
        f.write(combined_notes)
    print(f"[DEBUG] 📝 Combined summary saved to: {combined_summary_path}")

    # Final refinement
    try:
        final_chain = refinement_prompt | llm | parser
        final_summary = final_chain.invoke({"notes": combined_notes[:22000]})
        return final_summary.strip()
    except Exception as e:
        print(f"[ERROR] Final summarization failed: {e}")
        return "⚠️ Unable to generate summary from extracted notes."
