# app/agents/swot_agent.py

import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# 🔐 Load env variables for Groq key
load_dotenv(override=True)

# 🧠 LLM setup
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)
parser = StrOutputParser()

# 🧾 Prompt for SWOT generation
swot_prompt = PromptTemplate.from_template("""
You're a business analyst tasked with generating a SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis.

Here is a summary of the company's business and strategy:

{summary}

Additional context:
- Sector: {sector}
- Industry: {industry}

Generate a professional SWOT analysis with 3-4 bullet points in each category.
Use plain English. Be concise. No financial jargon.
""")

# 🔧 Main callable function
def generate_swot_analysis(ticker: str, context: dict) -> str:
    try:
        chain = swot_prompt | llm | parser
        response = chain.invoke({
            "summary": context.get("summary", "No summary provided."),
            "sector": context.get("sector", "N/A"),
            "industry": context.get("industry", "N/A")
        })
        return response.strip()

    except Exception as e:
        print(f"[SWOT ERROR] Failed to generate SWOT for {ticker}: {e}")
        return "⚠️ SWOT generation failed."
