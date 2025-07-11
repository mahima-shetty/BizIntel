# streamlit_ui/components/auth_handler.py

import streamlit as st
import jwt
import os
from dotenv import load_dotenv
from sqlite3 import connect

import sys
import requests
import streamlit as st
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
# Use one of the import methods for decode_jwt_token()
from app.core.jwt_utils import decode_jwt_token

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "TwoZeroTwoFive")
DB_PATH = "streamlit_ui/db/prefs.db"


load_dotenv()
API_BASE_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

def get_current_user_data(token: str) -> dict:
    try:
        decoded = decode_jwt_token(token)
        user_id = decoded.get("sub")

        # ✅ Fallback to sub if email is missing
        email = decoded.get("email") or user_id

        # ✅ Role fallback
        role = decoded.get("role", "Analyst")

        # Fetch preferences from FastAPI
        response = requests.get(
            f"{API_BASE_URL}/api/user/preferences",
            headers={"Authorization": f"Bearer {token}"}
        )

        prefs = response.json() if response.status_code == 200 else {}

        return {
            "user_id": user_id,
            "email": email,
            "role": role,
            # ✅ Prevent split() on None
            "username": decoded.get("name") or email.split("@")[0],
            "preferences": prefs
        }

    except Exception as e:
        st.error(f"Auth failed: {e}")
        st.session_state.pop("token", None)
        st.stop()


def fetch_user_role(email):
    try:
        conn = connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT user_type FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else "Analyst"
    except Exception:
        return "Analyst"
    
    
def handle_auth():
    st.title("🚀 BizIntel Dashboard")

    query_token = st.query_params.get("token", None)

    if query_token and "user_email" not in st.session_state:
        try:
            decoded = jwt.decode(query_token, JWT_SECRET, algorithms=["HS256"])

            # ✅ CRITICAL: Save the raw token for later use
            st.session_state["token"] = query_token

            st.session_state["user_email"] = decoded["sub"]
            st.session_state["user_name"] = decoded["name"]
            st.session_state["user_role"] = fetch_user_role(decoded["sub"])

            st.query_params.clear()
            st.rerun()

        except jwt.ExpiredSignatureError:
            st.error("❌ Token expired.")
        except jwt.InvalidTokenError as e:
            st.error(f"❌ Invalid token: {e}")
            st.stop()

    if "user_email" not in st.session_state:
        st.markdown("[🔐 Login with Google](http://localhost:8000/login)")
        st.stop()

    st.success(f"✅ Logged in as {st.session_state['user_name']} ({st.session_state['user_email']})")
