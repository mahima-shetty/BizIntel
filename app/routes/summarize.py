from fastapi import APIRouter, Body
from llm.summarizer import summarize

router = APIRouter()



@router.post("")
@router.post("/")
def get_summary(text: str = Body(..., embed=True)):
    summary = summarize(text)
    return {"summary": summary}
