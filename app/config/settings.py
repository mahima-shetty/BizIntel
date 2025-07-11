# app/config/settings.py
import os
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

load_dotenv()

# JWT secret
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "TwoZeroTwoFive")

# OAuth config
config = Config(environ=os.environ)
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)
