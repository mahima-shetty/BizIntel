from fastapi import FastAPI
from app.routes import ingest, summarize, user

app = FastAPI(title="BizIntel API")

# Include modular routes
app.include_router(ingest.router, prefix="/ingest", tags=["Ingestion"])
app.include_router(summarize.router, prefix="/summary", tags=["Summarization"])
app.include_router(user.router, prefix="/user", tags=["User"])

@app.get("/")
def root():
    return {"status": "🚀 BizIntel backend running!"}



