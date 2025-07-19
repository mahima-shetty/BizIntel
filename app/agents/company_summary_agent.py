# app/agents/company_summary_agent.py

import os
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv

load_dotenv(override=True)

# 🔒 Deterministic LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)
print("[DEBUG] Using Groq Key:", os.getenv("GROQ_API_KEY")[:6] + "****")


# ✅ Updated to accept a merged section
# company_summary_prompt = PromptTemplate(
#     input_variables=["ticker", "business_strategy"],
#     template="""
# You are a financial analyst assistant.

# Here's information from the company's 10-K filing:

# 📌 Ticker: {ticker}

# 🏢 Business Overview & Strategy:
# {business_strategy}

# Write a clear, professional 5-sentence summary explaining:
# - The company's core business
# - Strategic priorities
# - Any recent changes or positioning insights
# Avoid fluff or speculation beyond this data.
# """
# )
company_summary_prompt = PromptTemplate(
    input_variables=["ticker", "business_strategy"],
    template="""
You are an assistant that explains business strategy in simple terms.

Here's the company's official 10-K filing content:

📌 Ticker: {ticker}

🏢 Business Overview & Strategy:
{business_strategy}

Write a simple, clear explanation of what this company does and how it plans to grow — for someone without a finance background.

Format your output as:
- A plain English summary anyone can understand
- 4 to 6 bullet points
- Avoid financial jargon or long sentences
- Focus on what the company sells, how it works, and what its priorities are
"""
)


chain: RunnableSequence = company_summary_prompt | llm | StrOutputParser()


def summarize_company_from_edgar(ticker: str, edgar_data: dict) -> str:
    content = edgar_data.get("business_strategy", "").strip()

    if not content or len(content) < 300:  # less than ~50 words = junk
        return "⚠️ Not enough EDGAR data to generate a meaningful summary."

    return chain.invoke({
        "ticker": ticker,
        "business_strategy": content
    }).strip()
