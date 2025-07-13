import feedparser

def scrape_reuters(topic="AI",count=5):
    """
    Fetch Reuters news articles via Google News RSS by topic and optional region.

    Args:
        topic (str): Main topic keyword.
        region (str): Optional region keyword.
        count (int): Number of articles to fetch.

    Returns:
        list of dict: Articles with title, description, URL, source.
    """
    combined_query = f"site:reuters.com+{topic}".strip().replace(" ", "+")
    url = f"https://news.google.com/rss/search?q={combined_query}"
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


# ───────────────
# Test it standalone
if __name__ == "__main__":
    print("Without region:")
    for a in scrape_reuters(topic="AI"):
        print(a["title"], "|", a["url"])

    print("\nWith region:")
    for a in scrape_reuters(topic="AI"):
        print(a["title"], "|", a["url"])
