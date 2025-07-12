# app/agents/funding_agent.py

import feedparser
from datetime import datetime

FEED_URL = "https://news.google.com/rss/search?q=site:techcrunch.com+funding+OR+raises+OR+venture+capital"

FUNDING_KEYWORDS = [
    "raises", "funding", "series a", "series b", "seed", "venture capital", "round"
]

def fetch_funding_news(count: int = 5):
    feed = feedparser.parse(FEED_URL)
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "").lower()
        summary = entry.get("summary", "").lower()
        link = entry.get("link", "")
        pub_date = entry.get("published", "")

        # If any funding keyword is found
        if any(keyword in title or keyword in summary for keyword in FUNDING_KEYWORDS):
            articles.append({
                "title": entry.get("title", "No title"),
                "description": entry.get("summary", ""),
                "url": link,
                "source": "TechCrunch",
                "published": pub_date
            })

        if len(articles) >= count:
            break

    return articles

# Test it standalone
if __name__ == "__main__":
    funding = fetch_funding_news()
    print("Fetched:", len(funding))
    for f in funding:
        print(f["title"], "|", f["url"])
