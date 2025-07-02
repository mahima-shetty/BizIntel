import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_news(topic: str = "AI", count: int = 5):
    params = {
        "q": topic,
        "pageSize": count,
        "apiKey": API_KEY,
        "sortBy": "publishedAt",
        "language": "en"
    }
    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        return {"error": f"Failed to fetch news: {response.text}"}
    
    articles = response.json().get("articles", [])
    return [
        {
            "title": article["title"],
            "description": article["description"],
            "url": article["url"]
        }
        for article in articles
    ]
