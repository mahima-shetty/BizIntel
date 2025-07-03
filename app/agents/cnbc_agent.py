import feedparser 
from datetime import datetime

CNBC_FEED_URL = "https://www.cnbc.com/id/100003114/device/rss/rss.html"

def fetch_cnbc_news(topic: str = "AI", count: int = 5):
    feed = feedparser.parse(CNBC_FEED_URL)

    articles = []
    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("description", "")
        link = entry.get("link", "")
        pub_date = entry.get("published", "")

        if topic.lower() in title.lower() or topic.lower() in summary.lower():
            articles.append({
                "title": title,
                "description": summary,
                "source": "CNBC", 
                "url": link,
                "published": pub_date
            })

        if len(articles) >= count:
            break
        
        

    return articles


if __name__ == "__main__":
    articles = fetch_cnbc_news()
    print("Fetched", len(articles))
    for a in articles:
        print(a["title"], "|", a["url"])