from fastapi import APIRouter, Query
from app.agents import news_agent
from app.agents.news_agent import get_news


router = APIRouter()

@router.get("/news")
def get_news(topic: str = Query("AI"), count: int = Query(3)):
    articles = news_agent.fetch_news(topic, count)
    return {"topic": topic, "articles": articles}



@router.get("/news")
def fetch_news(topic: str = Query(..., example="AI")):
    return {"topic": topic, "articles": get_news(topic)}
