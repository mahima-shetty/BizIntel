from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import os

def summarize_articles(articles: list[str]) -> str:
    prompt = PromptTemplate(
        input_variables=["text"],
        template="""
        You are a market news analyst. Summarize the following in 3 bullet points:
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
