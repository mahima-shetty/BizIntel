import streamlit as st
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "supersecretkey")

st.title("BizIntel DashBoard on its way!")

# Get token from query param
query_token = st.query_params.get("token")
token = query_token if query_token else None

# Handle token-based login
if token and "user" not in st.session_state:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        st.session_state["user"] = decoded
        st.success(f"✅ Welcome, {decoded['name']} ({decoded['sub']})")
    except jwt.ExpiredSignatureError:
        st.error("❌ Token expired.")
    except jwt.InvalidTokenError as e:
        st.error(f"❌ Invalid token: {e}")

# Show login link if not logged in
if "user" not in st.session_state:
    st.markdown("[🔐 Login with Google](http://localhost:8000/login)")
    st.stop()

# Show user info and logout button
user = st.session_state["user"]
# st.success(f"✅ Logged in as {user['name']} ({user['sub']})")

# Logout button
if st.button("🚪 Logout"):
    st.session_state.clear()
    st.query_params.clear()
    st.rerun()
