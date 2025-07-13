from collections import defaultdict
from datetime import datetime

from app.agents.news_agent import get_news as fetch_newsapi
from app.agents.cnbc_agent import fetch_cnbc_news
from app.agents.scraper_reuters import scrape_reuters
from app.agents.scraper_techcrunch import scrape_techcrunch_via_rss as scrape_techcrunch
from app.agents.finnhub_agent import fetch_finnhub_news  # ✅ make sure this exists

from dateutil.parser import parse as parse_date  # Add this import at the top
from datetime import timezone



def aggregate_analyst(topic: str = "AI", count: int = 10, sources: list = None):
    combined = []
    
    selected_sources = set(sources or ["NewsAPI", "CNBC", "Reuters", "TechCrunch", "Finnhub"])

    if "NewsAPI" in selected_sources:
        try:
            newsapi_articles = fetch_newsapi(topic, count)
            combined.extend(newsapi_articles)
        except Exception as e:
            print(f"[NewsAPI Error]: {e}")

    if "CNBC" in selected_sources:
        try:
            cnbc_articles = fetch_cnbc_news(topic, count)
            combined.extend(cnbc_articles)
        except Exception as e:
            print(f"[CNBC Error]: {e}")

    if "TechCrunch" in selected_sources:
        try:
            techcrunch_articles = scrape_techcrunch(topic, count)
            combined.extend(techcrunch_articles)
        except Exception as e:
            print(f"[TechCrunch Error]: {e}")

    if "Reuters" in selected_sources:
        try:
            reuters_articles = scrape_reuters(topic, count)
            combined.extend(reuters_articles)
        except Exception as e:
            print(f"[Reuters Error]: {e}")

    if "Finnhub" in selected_sources:
        try:
            finnhub_articles = fetch_finnhub_news(topic=topic, count=count)
            combined.extend(finnhub_articles)
        except Exception as e:
            print(f"[Finnhub Error]: {e}")

    for a in combined:
        if "source" not in a or not a["source"]:
            print("[WARN] Missing source for article:", a.get("title", "Untitled"))

    seen = set()
    deduped = []
    for article in combined:
        url = article.get("url")
        if url and url not in seen:
            if "published_at" not in article:
                article["published_at"] = datetime.utcnow().isoformat()
            deduped.append(article)
            seen.add(url)

    source_buckets = defaultdict(list)
    for article in deduped:
        source = article.get("source", "Unknown")
        source_buckets[source].append(article)

    balanced = []
    for group in source_buckets.values():
        balanced.extend(group[:3])

    def safe_parse_date(article):
        try:
            dt = parse_date(article.get("published_at", ""))
            return dt.replace(tzinfo=None)  # ⬅️ strip timezone
        except Exception:
            return datetime.min   # fallback to oldest possible date

    balanced = sorted(balanced, key=safe_parse_date, reverse=True)


    return balanced[:count]
