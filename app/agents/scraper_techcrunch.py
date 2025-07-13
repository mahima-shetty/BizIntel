import feedparser

def scrape_techcrunch_via_rss(topic: str = "AI", count: int = 5):
    """
    Fetch TechCrunch news articles using Google News RSS based on topic and region.

    Args:
        topic (str): Main keyword/topic.
        region (str): Optional region keyword.
        count (int): Number of articles to return.

    Returns:
        list of dicts with title, url, description, and source.
    """
    combined_query = f"site:techcrunch.com+{topic}".strip().replace(" ", "+")
    feed_url = f"https://news.google.com/rss/search?q={combined_query}"
    feed = feedparser.parse(feed_url)

    articles = []
    for entry in feed.entries[:count]:
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


# ───────────────
# Debug / standalone testing
if __name__ == "__main__":
    print("Without region:")
    articles = scrape_techcrunch_via_rss("AI")
    for a in articles:
        print(a["title"], "|", a["url"])

    print("\nWith region:")
    articles = scrape_techcrunch_via_rss("AI")
    for a in articles:
        print(a["title"], "|", a["url"])
