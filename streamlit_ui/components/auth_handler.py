# streamlit_ui/components/auth_handler.py
import streamlit as st
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "TwoZeroTwoFive")


def handle_auth():
    st.title("📊 BizIntel Dashboard is on your way!")

    
    query_token = st.query_params.get("token", None)

    # First-time login via JWT token
    if query_token and "user" not in st.session_state:
        try:
            decoded = jwt.decode(query_token, JWT_SECRET, algorithms=["HS256"])
            st.session_state["user"] = decoded
            st.success(f"✅ Welcome, {decoded['name']} ({decoded['sub']})")
            st.query_params.clear()
            st.rerun()
        except jwt.ExpiredSignatureError:
            st.error("❌ Token expired.")
        except jwt.InvalidTokenError as e:
            st.error(f"❌ Invalid token: {e}")

    # Not logged in yet
    if "user" not in st.session_state:
        st.markdown("[🔐 Login with Google](http://localhost:8000/login)")
        st.stop()

    # Logged-in view
    user = st.session_state["user"]
    st.success(f"✅ Logged in as {user['name']} ({user['sub']})")

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()
