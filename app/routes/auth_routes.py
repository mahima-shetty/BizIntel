# app/routes/auth_routes.py
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.core.jwt_utils import create_jwt_token
from app.config.settings import oauth, JWT_SECRET

import time

auth_router = APIRouter()


@auth_router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@auth_router.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    payload = {
        "sub": user_info["email"],
        "name": user_info["name"],
        "exp": time.time() + 3600,  # 1 hour
    }

    jwt_token = create_jwt_token(payload)
    return RedirectResponse(f"http://localhost:8501?token={jwt_token}")
