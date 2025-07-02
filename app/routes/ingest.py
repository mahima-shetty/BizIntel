from fastapi import APIRouter, Query
from app.agents import news_agent

router = APIRouter()

@router.get("/news")
def get_news(topic: str = Query("AI"), count: int = Query(3)):
    articles = news_agent.fetch_news(topic, count)
    return {"topic": topic, "articles": articles}
