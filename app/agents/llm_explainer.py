# app/agents/llm_explainer.py

import os
import pandas as pd
import numpy as np
from typing import Dict, List, TypedDict
from llama_index.llms.langchain import LangChainLLM
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv
load_dotenv(override=True)


# ✅ Create reusable, wrapped LLM for custom summaries
groq_llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192",
    temperature=0  # 🔒 Set to 0 to prevent hallucinations
)
wrapped_llm = LangChainLLM(llm=groq_llm)


# ==========================
# 🔍 Trend Summary Generator
# ==========================

trend_prompt = PromptTemplate(
    input_variables=["ticker", "summary"],
    template="""
You're a financial analyst. The stock {ticker} had significant movements recently:

{summary}

Analyze the volatility and suggest possible reasons or patterns that could explain these movements.
Provide a concise summary (3-5 sentences). Avoid assumptions not in the data.
"""
)

def generate_trend_summary(ticker: str, df_alerts):
    alert_summary = df_alerts[["Date", "Close", "% Change"]].to_string(index=False)
    prompt_text = trend_prompt.format(ticker=ticker, summary=alert_summary)
    response = wrapped_llm.complete(prompt_text)
    return response.text.strip()


# def generate_trend_summary(ticker, data):
#     # Ensure data is a DataFrame
#     print(f"Print DATA", data)
#     if isinstance(data, dict) and all(np.isscalar(v) for v in data.values()):
#         data = pd.DataFrame([data])
#     else:
#         data = pd.DataFrame(data)

#     if data.empty:
#         return f"No trend data available for {ticker}."

#     # Now df_alerts works
#     df_alerts = data.copy()
#     if "% Change" not in df_alerts.columns:
#         df_alerts["% Change"] = df_alerts["Close"].pct_change() * 100

#     alert_summary = df_alerts[["Date", "Close", "% Change"]].to_string(index=False)
#     return f"Trend Summary for {ticker}:\n{alert_summary}"






# ==========================
# 🧠 KPI + News Insight Engine
# ==========================

def summarize_kpi_and_news(prompt_text_dict: dict) -> str:
    """
    Accepts a dict with:
        - question
        - kpi_data (string)
        - news_data (string)
    """
    system_template = """
You are a financial analyst assistant. Given stock KPI changes and news,
provide a concise, insightful summary that answers the user's question
in a professional and clear tone.
"""

    prompt = PromptTemplate.from_template("""
{system_instructions}

--- USER QUESTION ---
{question}

--- KPI DATA ---
{kpi_data}

--- NEWS DATA ---
{news_data}

Return your answer in bullet points where appropriate.
""")

    chain: RunnableSequence = (
        prompt
        | ChatGroq(model="llama3-70b-8192", temperature=0)
        | StrOutputParser()
    )

    return chain.invoke({
        "system_instructions": system_template.strip(),
        "question": prompt_text_dict.get("question", ""),
        "kpi_data": prompt_text_dict.get("kpi_data", ""),
        "news_data": prompt_text_dict.get("news_data", "")
    })

# 🧠 Prompt formatting utility
def format_insight_prompt(question: str, kpi_dict: dict, news_list: list) -> str:
    # Convert KPI dict to readable string
    kpi_lines = []
    for ticker, daily_data in kpi_dict.items():
        kpi_lines.append(f"Ticker: {ticker}")
        for date, kpi in daily_data.items():
            kpi_lines.append(f"Date: {date}")
            for key, val in kpi.items():
                kpi_lines.append(f"- {key}: {val}")
            kpi_lines.append("")  # newline between entries
    kpi_str = "\n".join(kpi_lines)

    # Convert News list to readable string
    news_lines = []
    for article in news_list:
        title = article.get("title", "")
        source = article.get("source", "")
        date = article.get("date", "")
        news_lines.append(f"- {title} ({source}, {date})")
    news_str = "\n".join(news_lines)

    return f"""
User question: {question}

--- KPI DATA ---
{kpi_str}

--- NEWS DATA ---
{news_str}
""".strip()



company_deep_dive_prompt = PromptTemplate(
    input_variables=["ticker", "business_model", "strategy"],
        template="""
    You are a financial analyst assistant.

    Here's information extracted from the company's latest 10-K filing:

    📌 Ticker: {ticker}

    🏢 Business Overview:
    {business_model}

    📈 Strategy & Management Discussion:
    {strategy}

    Write a clear, professional 5-sentence summary explaining:
    - The company's core business
    - Strategic priorities
    - Any recent changes or positioning insights
    Avoid fluff or speculation beyond this data.
    """
    )

def generate_company_summary(ticker: str, edgar_data: dict) -> str:
    if not edgar_data:
        return "EDGAR data not available for summarization."

    filled_prompt = company_deep_dive_prompt.format(
        ticker=ticker,
        business_model=edgar_data.get("business_model", "Not available."),
        strategy=edgar_data.get("strategy", "Not available.")
    )

    response = wrapped_llm.complete(filled_prompt)
    return response.text.strip()
