

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
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
        api_key=os.getenv("GROQ_API_KEY"),  # Ensure this is set
        model_name="llama3-70b-8192" 
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    joined_text = "\n\n".join(articles)

    result = chain.run(joined_text)
    return result
