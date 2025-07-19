# app/agents/swot_agent.py

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 🔐 Load env vars
load_dotenv(override=True)

# ⚙️ Setup Groq LLM
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0
)
parser = StrOutputParser()

# 🧠 Advanced SWOT Prompt
swot_prompt = PromptTemplate.from_template("""
You're a senior business analyst preparing a detailed SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis.

Here is a summary of the company's business and strategy:

{summary}

Sector: {sector}
Industry: {industry}

Based on this data and your domain knowledge, provide a thorough SWOT analysis:

1. **Strengths** – What internal capabilities, assets, or market advantages does the company have?
2. **Weaknesses** – What are its internal challenges or gaps compared to competitors?
3. **Opportunities** – What trends, technologies, or new markets can the company leverage?
4. **Threats** – What external risks (macro, regulatory, competitive, etc.) could undermine its performance?

Include competitor risks, market shifts, and regulatory threats where relevant.

Format: 
- Use clear section headers (e.g., **Strengths**) 
- Provide 3–5 bullet points per section
- Be specific. Avoid generic corporate language.
- Target a professional reader in tech or finance.
""")

def generate_swot_analysis(ticker: str, context: dict) -> str:
    try:
        chain = swot_prompt | llm | parser
        return chain.invoke({
            "summary": context.get("summary", "No summary provided."),
            "sector": context.get("sector", "N/A"),
            "industry": context.get("industry", "N/A")
        }).strip()

    except Exception as e:
        print(f"[SWOT ERROR] Failed for {ticker}: {e}")
        return "⚠️ Failed to generate SWOT analysis."
