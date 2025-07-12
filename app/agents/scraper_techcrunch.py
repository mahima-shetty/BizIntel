import feedparser

def scrape_techcrunch_via_rss():
    feed_url = "https://news.google.com/rss/search?q=site:techcrunch.com+AI"
    feed = feedparser.parse(feed_url)

    articles = []
    for entry in feed.entries[:10]:  # Top 10 articles
        title = entry.get("title", "No Title")
        link = entry.get("link", "")
        summary = entry.get("summary", "")

        articles.append({
            "title": title,
            "url": link,
            "description": summary,
            "source": "TechCrunch"
        })
        print(f"[RSS] Fetched: {title}")

    return articles


# Debug / standalone testing
if __name__ == "__main__":
    articles = scrape_techcrunch_via_rss()
    print("Fetched", len(articles))
    for a in articles:
        print(a["title"], "|", a["url"])
