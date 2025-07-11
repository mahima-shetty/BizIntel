# app/core/jwt_utils.py
import jwt
from app.config.settings import JWT_SECRET


def create_jwt_token(payload: dict) -> str:
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    if isinstance(token, bytes):  # 👈 Ensure string type
        token = token.decode("utf-8")
    return token



def decode_jwt_token(token: str) -> dict:
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

