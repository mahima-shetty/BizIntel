import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def get_news(topic: str = "AI", count: int = 5):
    """
    Fetch news from NewsAPI based on topic and optional region.

    Args:
        topic (str): Search keyword.
        count (int): Number of articles.
        region (str): Optional region filter (e.g., "India", "Europe").

    Returns:
        list of dict: News articles.
    """
    query = f"{topic}".strip()

    params = {
        "q": query,
        "pageSize": count,
        "apiKey": API_KEY,
        "sortBy": "publishedAt",
        "language": "en"
    }

    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        return []

    articles = response.json().get("articles", [])

    return [
        {
            "title": article.get("title", "No Title"),
            "source": "NewsAPI",
            "description": article.get("description", ""),
            "url": article.get("url", ""),
            "published_at": article.get("publishedAt", datetime.utcnow().isoformat())
        }
        for article in articles
    ]


# ───────────────
# Test it standalone
if __name__ == "__main__":
    print("Without region:")
    for a in get_news(topic="AI"):
        print(a["title"], "|", a["url"])

    print("\nWith region:")
    for a in get_news(topic="AI"):
        print(a["title"], "|", a["url"])
