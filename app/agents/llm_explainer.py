# app/agents/llm_explainer.py

from llama_index.llms.langchain import LangChainLLM
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os

groq_llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192"
)
wrapped_llm = LangChainLLM(llm=groq_llm)

trend_prompt = PromptTemplate(
    input_variables=["ticker", "summary"],
    template="""
You're a financial analyst. The stock {ticker} had significant movements recently:

{summary}

Analyze the volatility and suggest possible reasons or patterns that could explain these movements.
Provide a concise summary (3-5 sentences).
"""
)

def generate_trend_summary(ticker: str, df_alerts):
    alert_summary = df_alerts[["Date", "Close", "% Change"]].to_string(index=False)
    prompt_text = trend_prompt.format(ticker=ticker, summary=alert_summary)

    # ✅ Use `.complete()` for raw strings with LlamaIndex-wrapped LangChain LLMs
    response = wrapped_llm.complete(prompt_text)
    return response.text.strip()

