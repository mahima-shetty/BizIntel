from llama_index.core import Document, SummaryIndex
from llama_index.llms.langchain import LangChainLLM
from langchain_groq import ChatGroq
import os

def summarize_articles(articles):
    if not articles:
        return "No articles to summarize."

    # Convert articles to LlamaIndex documents
    docs = [Document(text=a.get("content", a.get("title", ""))) for a in articles if a.get("content") or a.get("title")]

    # Wrap Groq LLaMA3-70B inside LangChainLLM
    groq_llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama3-70b-8192"
    )
    wrapped_llm = LangChainLLM(llm=groq_llm)

    # Create the summary index
    index = SummaryIndex.from_documents(docs, llm=wrapped_llm)

    # Use a query engine to get a summary
    query_engine = index.as_query_engine(llm=wrapped_llm)
    response = query_engine.query("You're a world-class AI news analyst. Summarize the main points from these news articles in exactly 5 short bullet points. "
    "Each bullet should be presented on a new line and begin with a '•' symbol. "
    "Keep each point to one sentence. Do not merge the bullet points together. "
    "Start with the line: '📝 Here's your summary for easy reading:'")
    
    return str(response)
