# app/routes/ingest.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/ping")
def ping():
    return {"message": "Ingest route works!"}
