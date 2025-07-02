from fastapi import APIRouter, Body
from llm.summarizer import summarize_articles


router = APIRouter()



@router.post("")
@router.post("/")
def get_summary(text: str = Body(..., embed=True)):
    summary = summarize_articles(text)
    return {"summary": summary}
