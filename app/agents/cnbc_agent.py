import feedparser
from datetime import datetime

CNBC_FEED_URL = "https://www.cnbc.com/id/100003114/device/rss/rss.html"

def fetch_cnbc_news(topic: str = "AI", count: int = 5):
    """
    Fetch CNBC news articles filtered by topic.

    Args:
        topic (str): Keyword to filter articles.
        count (int): Number of articles to return.

    Returns:
        list: Filtered list of article dictionaries.
    """
    feed = feedparser.parse(CNBC_FEED_URL)
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("description", "")
        link = entry.get("link", "")
        pub_date = entry.get("published", datetime.utcnow().isoformat())

        combined_text = f"{title} {summary}".lower()
        if topic.lower() in combined_text:
            articles.append({
                "title": title,
                "description": summary,
                "source": "CNBC",
                "url": link,
                "published_at": pub_date
            })

        if len(articles) >= count:
            break

    return articles

# ───────────────
# Debug standalone
if __name__ == "__main__":
    print("AI Articles:")
    for a in fetch_cnbc_news("AI"):
        print(a["title"], "|", a["url"])

    print("\nFinance Articles:")
    for a in fetch_cnbc_news("Finance"):
        print(a["title"], "|", a["url"])
