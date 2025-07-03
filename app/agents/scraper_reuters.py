import feedparser

def scrape_reuters(topic="AI", count=5):
    url = (
        "https://news.google.com/rss/"
        "search?q=site:reuters.com/technology+OR+site:reuters.com/world+"
        f"{topic}"
    )
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries[:count]:
        articles.append({
            "title": entry.title,
            "description": entry.get("summary", ""),
            "url": entry.link,
            "source": "Reuters"
        })
    return articles


if __name__ == "__main__":
    articles = scrape_reuters()
    print("Fetched", len(articles))
    for a in articles:
        print(a["title"], "|", a["url"])
