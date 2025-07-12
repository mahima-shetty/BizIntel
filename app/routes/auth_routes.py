# app/routes/auth_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.core.jwt_utils import create_jwt_token
from app.config.settings import oauth, JWT_SECRET
from fastapi.responses import JSONResponse
import jwt
import sqlite3
import os
import time

auth_router = APIRouter()


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "TwoZeroTwoFive")  # Load from .env ideally
JWT_ALGORITHM = "HS256"


@auth_router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]
    email = user_info["email"]
    name = user_info["name"]

    # 🔍 Fetch role from DB
    try:
        conn = sqlite3.connect("streamlit_ui/db/prefs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_type FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        role = row[0] if row else "Analyst"
    except Exception:
        role = "Analyst"

    # ✅ Now include role in JWT payload
    payload = {
        "sub": email,
        "name": name,
        "email": email,
        "role": role,
        "exp": time.time() + 3600,  # 1 hour
    }

    jwt_token = create_jwt_token(payload)
    return RedirectResponse(f"http://localhost:8501?token={jwt_token}")



@auth_router.post("/refresh-token")
async def refresh_token(request: Request):
    try:
        data = await request.json()
        email = data["email"]
        username = data["username"]
        role = data["role"]

        payload = {
            "email": email,
            "username": username,
            "role": role,
            "exp": time.time() + 3600  # 1 hour expiry
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)

        return JSONResponse(content={"token": token}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# @auth_router.post("/refresh-token")
# async def refresh_token(request: Request):
#     data = await request.json()
#     email = data.get("email")
#     role = data.get("role")
#     username = data.get("username")

#     if not email or not role:
#         return JSONResponse({"error": "Missing email or role"}, status_code=400)

#     payload = {
#         "email": email,
#         "role": role,
#         "username": username
#     }

#     token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
#     return {"token": token}