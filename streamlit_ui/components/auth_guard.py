# streamlit_ui/components/auth_guard.py

import streamlit as st

def require_login():
    if "user_email" not in st.session_state:
        st.warning("⛔ You must be logged in to view this page.")
        st.markdown("[🔐 Click here to login](http://localhost:8000/login)")
        st.stop()
