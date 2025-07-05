from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import os

def summarize_articles(articles: list[str]) -> str:
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        "You are an elite financial news analyst for a fast-paced GenAI market intelligence platform. Your job? Slice through noise and distill real insights. If the text is relevant to business, tech, finance, or the markets — summarize it crisply in exactly 5 impactful bullet points. Each point should be insightful, fact-rich, and free of fluff.
        But — if the content has no tie to the world of market dynamics, macroeconomics, companies, or AI-driven trends — respond with: ' Unable to summarize: content is not market-related.'"
        "{text}"
        """,
    )

    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"  # ✅ Make sure this model exists on Groq
    )

    chain: RunnableSequence = prompt | llm

    joined_text = "\n\n".join(articles)

    result = chain.invoke({"text": joined_text})
    return result.content  # 🚨 .content gives actual string from response
