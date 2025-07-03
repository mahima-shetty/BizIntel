from fastapi import FastAPI
from app.routes import ingest, summarize, user
from app.agents.aggregator import aggregate_news

app = FastAPI(title="BizIntel API")

# Include modular routes
app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(summarize.router, prefix="/summary", tags=["Summarization"])
app.include_router(user.router, prefix="/user", tags=["User"])

@app.get("/news")
def get_news(topic: str = "AI", count: int = 10):
    articles = aggregate_news(topic, count)
    return {"articles": articles}




