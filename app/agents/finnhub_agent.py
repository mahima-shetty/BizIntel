import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")  # Make sure it's set in .env

def fetch_finnhub_news(topic: str = "", count: int = 10):
    if not FINNHUB_API_KEY:
        print("[ERROR] Finnhub API key not found.")
        return []

    try:
        # Construct the query (basic filtering for relevance)
        search_query = f"{topic}".strip()

        url = f"https://finnhub.io/api/v1/news"
        params = {
            "category": "general",  # Options: general, forex, crypto, merger
            "token": FINNHUB_API_KEY
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        articles = response.json()

        # Filter articles manually (Finnhub doesn't support custom query search directly)
        filtered = [
            {
                "title": a.get("headline", "No title"),
                "description": a.get("summary", ""),
                "url": a.get("url"),
                "source": "Finnhub",
                "published_at": a.get("datetime", datetime.utcnow().isoformat())
            }
            for a in articles
            if search_query.lower() in (a.get("headline", "") + a.get("summary", "")).lower()
        ]

        return filtered[:count]

    except Exception as e:
        print(f"[ERROR] Failed to fetch Finnhub news: {e}")
        return []


# ─────────────────────────────────────────────
# 🔍 Standalone Debug Check
if __name__ == "__main__":
    print("=== [Finnhub News Test] ===")

    print("\nNo Region:")
    try:
        articles = fetch_finnhub_news(topic="AI",  count=5)
        for a in articles:
            print(f"{a['title']} | {a['url']}")
    except Exception as e:
        print("Error fetching without region:", e)

    print("\nWith Region:")
    try:
        articles = fetch_finnhub_news(topic="Finance", count=5)
        for a in articles:
            print(f"{a['title']} | {a['url']}")
    except Exception as e:
        print("Error fetching with region:", e)
