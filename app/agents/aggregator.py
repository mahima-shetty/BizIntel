from collections import defaultdict
from datetime import datetime
from app.agents.news_agent import get_news as fetch_newsapi
from app.agents.cnbc_agent import fetch_cnbc_news
from app.agents.scraper_reuters import scrape_reuters
from app.agents.scraper_techcrunch import scrape_techcrunch_via_rss as scrape_techcrunch


def aggregate_news(topic: str = "AI", count: int = 10):
    combined = []

    # Pull from different agents
    newsapi_articles = []
    cnbc_articles = []
    techcrunch_articles = []
    reuters_articles = []

    try:
        newsapi_articles = fetch_newsapi(topic, count)
        combined.extend(newsapi_articles)
    except Exception as e:
        print(f"[NewsAPI Error]: {e}")

    try:
        cnbc_articles = fetch_cnbc_news(topic, count)
        combined.extend(cnbc_articles)
    except Exception as e:
        print(f"[CNBC Error]: {e}")

    try:
        techcrunch_articles = scrape_techcrunch()
        combined.extend(techcrunch_articles)
    except Exception as e:
        print(f"[TechCrunch Error]: {e}")

    try:
        reuters_articles = scrape_reuters()
        combined.extend(reuters_articles)
    except Exception as e:
        print(f"[Reuters Error]: {e}")

    # Source summary logging
    print(f"[SUMMARY] NewsAPI: {len(newsapi_articles)} | CNBC: {len(cnbc_articles)} | Reuters: {len(reuters_articles)} | TechCrunch: {len(techcrunch_articles)}")

    # Fix missing source warnings
    for a in combined:
        if "source" not in a or not a["source"]:
            print("[WARN] Missing source for article:", a.get("title", "Untitled"), "URL:", a.get("url"))

    # Deduplicate by URL
    seen = set()
    deduped = []
    for article in combined:
        url = article.get("url")
        if url and url not in seen:
            # Ensure 'published_at' key exists
            if "published_at" not in article:
                article["published_at"] = datetime.utcnow().isoformat()
            deduped.append(article)
            seen.add(url)

    # Fair sampling from each source
    source_buckets = defaultdict(list)
    for article in deduped:
        source = article.get("source", "Unknown")
        source_buckets[source].append(article)

    balanced = []
    for group in source_buckets.values():
        balanced.extend(group[:3])  # take top 3 from each source

    # Sort all selected articles by recency
    balanced = sorted(balanced, key=lambda x: x.get("published_at", ""), reverse=True)

    return balanced[:count]
