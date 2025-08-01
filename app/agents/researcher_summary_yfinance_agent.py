from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import yfinance as yf
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")


def get_researcher_business_summary_from_yfinance(ticker: str) -> dict:
    try:
        print(f"[INFO] 📉 Pulling Yahoo Finance summary for {ticker}...")

        info = yf.Ticker(ticker).info
        raw_summary = info.get("longBusinessSummary")

        if not raw_summary or not isinstance(raw_summary, str) or len(raw_summary.strip()) < 50:
            raise ValueError("Yahoo summary missing or too short.")

        # Save raw summary for debug
        os.makedirs("debug_outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_path = f"debug_outputs/yfinance_summary_{ticker}_{timestamp}.txt"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(raw_summary)

        print(f"[DEBUG] ✅ Saved raw Yahoo summary to: {debug_path}")

        # Prompt setup
        template = """
You are a business research assistant. Given the long business description below from Yahoo Finance for the company {ticker}, extract:

1. A concise **Business Model** summary (what the company does, how it makes money).
2. A plausible **Strategy** summary (its priorities, direction, or competitive approach).

Format:
Business Model: <...>
Strategy: <...>

Description:
\"\"\"
{raw_summary}
\"\"\"
        """.strip()

        prompt_template = PromptTemplate.from_template(template)
        chain = prompt_template | llm

        response = chain.invoke({
            "ticker": ticker,
            "raw_summary": raw_summary
        })

        # Extract text if response is a message object
        if hasattr(response, "content"):
            response = response.content

        print(f"[DEBUG] 💬 LLM raw response:\n{response}")

        # ✅ Robust parsing using regex
        business_model_match = re.search(r"(?i)business model[:\-]*\s*(.*?)(?:\n|strategy[:\-])", response, re.DOTALL)
        strategy_match = re.search(r"(?i)strategy[:\-]*\s*(.*)", response, re.DOTALL)

        business_model = business_model_match.group(1).strip() if business_model_match else ""
        strategy = strategy_match.group(1).strip() if strategy_match else ""

        if not business_model:
            raise ValueError("LLM response did not contain a recognizable Business Model section.")

        return {
            "business_model": business_model,
            "strategy": strategy
        }

    except Exception as e:
        print(f"[❌] Failed to process Yahoo summary for {ticker}: {e}")
        return {
            "business_model": "",
            "strategy": ""
        }
