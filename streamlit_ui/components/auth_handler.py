# streamlit_ui/components/auth_handler.py

import streamlit as st
import jwt
import os
from dotenv import load_dotenv
from sqlite3 import connect

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "TwoZeroTwoFive")
DB_PATH = "streamlit_ui/db/prefs.db"

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
