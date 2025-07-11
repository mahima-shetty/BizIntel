# auth_server.py
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os, time
import jwt
from dotenv import load_dotenv

load_dotenv()


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=os.getenv("JWT_SECRET_KEY", "TwoZeroTwoFive"))

# Enable frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = Config(environ=os.environ)
oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "TwoZeroTwoFive")

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    print("Redirect URI:", redirect_uri) #should be removed
    print("Using Client ID:", os.getenv("GOOGLE_CLIENT_ID")) #should be removed
    
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    print("✅ Sending token:", token) #should be removed
    
    user_info = token["userinfo"]

    payload = {
        "sub": user_info["email"],
        "name": user_info["name"],
        "exp": time.time() + 3600,
    }

    jwt_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    print("🚀 Final JWT in redirect:", jwt_token) #should be removed
    return RedirectResponse(f"http://localhost:8501?token={jwt_token}")
