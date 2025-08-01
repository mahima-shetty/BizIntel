# app/agents/company_summary_agent.py

import os
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-70b-8192")

# For raw 10-K text
overview_prompt = PromptTemplate.from_template(
    """You are a financial analyst creating a concise, investor-friendly company summary based on SEC 10-K data.

### Filing Text:
{text}

---

### Output Format:
**Summary:** <one-paragraph overview>

**SWOT Analysis:**
- **Strengths:** ...
- **Weaknesses:** ...
- **Opportunities:** ...
- **Threats:** ...
"""
)

def summarize_company_overview(edgar_text: str) -> dict:
    """
    Called from deep_dive_agent.py — uses raw 10-K text.
    """
    chain = RunnableSequence([overview_prompt, llm])
    result = chain.invoke({"text": edgar_text})
    return {
        "summary": result.content.strip(),
        "source": "EDGAR"
    }

# For cleaned dict input
rag_format_prompt = PromptTemplate.from_template(
    """Format the following company insights into a clear investor summary with SWOT analysis.

### Business Model:
{business_model}

### Strategy:
{strategy}

### SWOT:
{swot_analysis}

---

### Output Format:
**Summary:** <one-paragraph overview>

"""
)


# **SWOT Analysis:**
# - **Strengths:** ...
# - **Weaknesses:** ...
# - **Opportunities:** ...
# - **Threats:** ...

def summarize_company_from_edgar(ticker: str, summary_data: dict) -> str:
    """
    Called from get_business_model_and_strategy() after RAG.
    """
    try:
        chain = rag_format_prompt | llm
        result = chain.invoke(summary_data)
        return result.content.strip()
    except Exception as e:
        print(f"[LLM FORMAT ERROR - {ticker}] {e}")
        return "⚠️ LLM formatting failed."



from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq

def summarize_company_from_yfinance(business_model: str, strategy: str, ticker: str) -> str:
    """
    Generates a concise company summary using Groq-hosted LLaMA3 based on the business model and strategy.
    Returns a 3–5 sentence summary.
    """
    try:
        if not business_model or len(business_model.strip()) < 20:
            raise ValueError("Business model text is too short or missing.")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a business analyst."),
            ("user", 
             """Based on the company’s business model and strategy, generate a concise company summary.
Focus on what the company does, how it generates revenue, and any notable strategic priorities.

Business Model:
{business_model}

Strategy:
{strategy}

Output a short, 3–5 sentence company overview.""")
        ])

        llm = ChatGroq(
            model_name="llama3-8b-8192",
            temperature=0.3,
            max_tokens=1000,
        )

        chain: Runnable = prompt | llm
        response = chain.invoke({
            "business_model": business_model,
            "strategy": strategy or ""
        })

        summary = response.content.strip()
        if not summary:
            raise ValueError("LLM returned empty summary.")

        return summary

    except Exception as e:
        print(f"[❌] Failed to generate summary for {ticker}: {e}")
        return "Summary generation failed."