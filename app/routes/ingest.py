from fastapi import APIRouter, Query
from app.agents import news_agent
from app.agents.news_agent import get_news
from app.agents.aggregator import aggregate_news
from llm.summarizer import summarize_articles


router = APIRouter()

@router.get("/news")
def fetch_and_summarize_news(topic: str = Query(..., example="AI")):
    articles = aggregate_news(topic)

    article_texts = [
        f"{a['title']}\n{a.get('description', '')}" for a in articles
    ]

    summary = summarize_articles(article_texts)

    return {
        "topic": topic,
        "summary": summary,
        "articles": articles
    }


