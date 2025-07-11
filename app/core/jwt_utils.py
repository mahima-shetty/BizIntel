# app/core/jwt_utils.py
import jwt
from app.config.settings import JWT_SECRET


def create_jwt_token(payload: dict) -> str:
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_jwt_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
