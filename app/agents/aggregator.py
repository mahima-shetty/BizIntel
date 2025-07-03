from app.agents.news_agent import get_news as fetch_newsapi
from app.agents.cnbc_agent import fetch_cnbc_news

def aggregate_news(topic: str = "AI", count: int = 5):
    combined = []

    # Pull from both sources
    newsapi_articles = fetch_newsapi(topic, count)
    cnbc_articles = fetch_cnbc_news(topic, count)

    combined.extend(newsapi_articles)
    combined.extend(cnbc_articles)

    # Deduplicate by URL
    seen = set()
    deduped = []
    for article in combined:
        if article["url"] not in seen:
            deduped.append(article)
            seen.add(article["url"])

    return deduped[:count]  # Return up to `count` items total
