from app.agents.aggregator import aggregate_news
from app.routes.summarize import get_summary  # or wherever your summarizer lives

if __name__ == "__main__":
    topic = "AI"
    count = 10

    articles = aggregate_news(topic, count)

    print(f"\n🔍 Aggregated {len(articles)} Articles:\n")

    for i, article in enumerate(articles, start=1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article.get('source')}")
        print(f"   URL: {article['url']}\n")

        if article.get("content"):
            summary = get_summary(article["content"])
            print(f"   🧠 Summary: {summary}\n")
