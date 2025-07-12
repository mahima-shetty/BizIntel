import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def get_news(topic: str = "AI", count: int = 5):
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
            "source": "NewsAPI",
            "description": article["description"],
            "url": article["url"]
        }
        for article in articles
    ]

if __name__ == "__main__":
    articles = get_news()
    print("Fetched", len(articles))
    for a in articles:
        print(a["title"], "|", a["url"])

# def get_news(topic: str):
#     api_key = os.getenv("NEWS_API_KEY")
#     url = f"https://newsapi.org/v2/everything?q={topic}&language=en&pageSize=5&apiKey={api_key}"
#     response = requests.get(url)
#     articles = response.json().get("articles", [])
    
#     return [
#         {"title": a["title"], "description": a["description"], "url": a["url"]}
#         for a in articles
#     ]
