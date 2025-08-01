import os
from typing import Dict
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_core.language_models import BaseLanguageModel  # Optional for type hinting
import pickle
from dotenv import load_dotenv
import json5, json
import regex as re

load_dotenv(override=True)

# 🔒 Deterministic LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)

# ✅ This is now the **only** JSON parsing function we need

def extract_json_from_response(response) -> dict:
    """
    Handles both dict responses with 'result' as stringified JSON,
    and plain string responses. Extracts the first valid JSON block.
    """
    try:
        # Step 1: Unwrap if inside a dict with stringified 'result'
        if isinstance(response, dict) and "result" in response:
            raw_text = response["result"]
        elif isinstance(response, str):
            raw_text = response
        else:
            raw_text = str(response)

        # Step 2: Greedy match from first '{' to last '}'
        match = re.search(r"\{[\s\S]*\}", raw_text)
        if not match:
            print("[WARN] ❌ No JSON object found.")
            return {"raw": raw_text.strip()}

        json_str = match.group(0)

        # Step 3: Try loading with json5 (handles trailing commas etc.)
        try:
            return json5.loads(json_str)
        except json.JSONDecodeError:
            print("[WARN] ✂️ Malformed JSON — applying patch.")
            patched = re.sub(r",\s*([\]}])", r"\1", json_str)
            return json5.loads(patched)

    except Exception as e:
        print(f"[ERROR] JSON recovery failed: {e}")
        return {"raw": str(response).strip()}



def clean_json_like_output(raw: str) -> str:
    """
    Strips markdown-style code fences and leading/trailing whitespace.
    """
    return re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()

def load_vectorstore_from_text_file(ticker: str, raw_text: str) -> FAISS:
    """
    Builds or loads a FAISS vectorstore for a given ticker from raw EDGAR text.
    Saves to disk to avoid recomputation.
    """
    save_path = f"vectorstores/{ticker}_10k_faiss"
    os.makedirs(save_path, exist_ok=True)

    faiss_file = os.path.join(save_path, "faiss_store.pkl")

    if os.path.exists(faiss_file):
        try:
            with open(faiss_file, "rb") as f:
                vectorstore = pickle.load(f)
                return vectorstore
        except Exception as e:
            print(f"[VEC LOAD ERROR] ❌ Could not load saved vectorstore for {ticker}: {e}")

    print(f"[INFO] 🔧 Building new vectorstore for {ticker}")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.create_documents([raw_text])

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embedding=embeddings)

    try:
        with open(faiss_file, "wb") as f:
            pickle.dump(vectorstore, f)
        print(f"[INFO] ✅ Vectorstore saved at {faiss_file}")
    except Exception as e:
        print(f"[VEC SAVE ERROR] ❌ Failed to save vectorstore for {ticker}: {e}")

    return vectorstore

def get_llm_summary_from_chunks(vectorstore: FAISS, question: str, llm) -> Dict[str, str]:
    """
    Uses RetrievalQA to answer a structured multi-part query and returns parsed JSON.
    Falls back to raw text if JSON parsing fails.
    """
    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False
        )

        response = qa_chain.invoke({"query": question})

        # DEBUG logs
        print("[DEBUG] type of response:", type(response))
        print("[DEBUG] response:", response)

        # Extract raw result
        if isinstance(response, dict) and "result" in response:
            raw = response["result"]
        elif isinstance(response, str):
            raw = response
        else:
            raw = str(response)

        # ✅ Clean markdown wrappers and try JSON parse
        raw_cleaned = clean_json_like_output(raw)
        return extract_json_from_response(raw_cleaned)

    except Exception as e:
        print(f"[RAG ERROR] RetrievalQA failed: {e}")
        return {"error": str(e)}

def get_business_strategy_from_rag(ticker: str, raw_text: str) -> Dict[str, str]:
    """
    Asks a structured multi-question prompt to the LLM via RAG and returns dict.
    """
    try:
        vectorstore = load_vectorstore_from_text_file(ticker, raw_text)

        question = (
            "Provide a structured JSON output containing the following fields:\n"
            "1. business_model: What you think company’s business model would be, in 3 sentences.\n"
            "2. strategy: What you think company’s corporate or competitive strategy would be, in 3 sentences.\n"
            "3. swot: What you think company's SWOT analysis would be with four keys - strengths, weaknesses, opportunities, threats - each as a list of bullet points.\n\n"
            "Format your answer strictly as JSON."
        )

        result = get_llm_summary_from_chunks(vectorstore, question, llm)

        if isinstance(result, dict):
            return {
                "business_model": result.get("business_model", "N/A"),
                "strategy": result.get("strategy", "N/A"),
                "swot": result.get("swot", "N/A"),
                "source": "EDGAR"
            }
        else:
            return {
                "business_model": str(result),
                "strategy": "",
                "swot": "",
                "source": "EDGAR"
            }

    except Exception as e:
        print(f"[RAG AGENT ERROR] Failed to get strategy from RAG for {ticker}: {e}")
        return {
            "business_model": "Error fetching data.",
            "strategy": "Error fetching data.",
            "swot": "Error fetching SWOT.",
            "source": "EDGAR"
        }
