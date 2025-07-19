# app/agents/llm_10k_prompts.py

from langchain.prompts import PromptTemplate

# 🔍 Per-chunk analysis: extract business model & strategy points
chunk_analysis_prompt = PromptTemplate.from_template("""
You are a financial analyst reading a portion of a company's 10-K filing.

Carefully extract key insights about:
- What the company does (business model)
- How it plans to grow or compete (strategic priorities)

If the chunk is incomplete, summarize only what’s visible. Focus on clarity, not filler.

---
{text}
""")

# 🧠 Final summary: clean, layman-friendly bullets
refinement_prompt = PromptTemplate.from_template("""
You are an assistant summarizing draft notes from a company's 10-K filing.

Based on the content below, write a clear and simple explanation of:
- The company's core business
- Its strategy or future direction

✅ Write in bullet points
✅ Use plain English (avoid financial jargon)
✅ Keep it informative, not fluffy

---
{notes}
""")
