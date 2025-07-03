import feedparser 

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
                "url": link,
                "published": pub_date
            })

        if len(articles) >= count:
            break

    return articles
