from langchain.prompts import PromptTemplate

# 🔍 Per-chunk analysis prompt: business model + strategy insights
chunk_analysis_prompt = PromptTemplate.from_template("""
You are a financial analyst reviewing a portion of a company's 10-K filing.

From the text below, extract any **concrete insights** about:
- What the company does (its business model)
- How it plans to grow or stay competitive (its strategy)

📌 If the text is incomplete or repetitive, summarize only the useful parts.
📌 Avoid copying tables, financial line items, or legal boilerplate.

---
{text}
""")

# 🧠 Final summary prompt: layman-friendly bullets
refinement_prompt = PromptTemplate.from_template("""
You are a professional summarizer creating a **simple and clear** overview of a company based on internal research notes.

Write a brief bullet-point summary covering:
- ✅ What the company does
- ✅ What its main strategic goals or directions are

Use plain English, avoid buzzwords or filler, and focus on clarity. Even a high schooler should understand it.

---
{notes}
""")
