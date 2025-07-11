# streamlit_ui/pages/user_profile.py

import streamlit as st
import sqlite3
import time
from components.auth_guard import require_login
from components.auth_ui import show_auth_ui


# ✅ Protect page
require_login()

# ✅ Sidebar login/logout
show_auth_ui()

# ✅ Session vars
email = st.session_state["user_email"]
name = st.session_state["user_name"]
current_role = st.session_state["user_role"]

# ✅ Show current info
st.title("👤 User Profile")
st.markdown(f"**Name:** `{name}`")
st.markdown(f"**Email:** `{email}`")
st.markdown(f"**Current Role:** `{current_role}`")

# 🔄 Role selection
st.markdown("### 🔄 Change Your Role")
roles = ["Startup Founder", "Analyst", "Researcher"]
new_role = st.selectbox("Select new role", roles, index=roles.index(current_role))

if new_role != current_role:
    if st.button("✅ Save Preference"):
        try:
            conn = sqlite3.connect("streamlit_ui/db/prefs.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (email, user_type)
                VALUES (?, ?)
                ON CONFLICT(email) DO UPDATE SET user_type=excluded.user_type;
            """, (email, new_role))
            conn.commit()
            conn.close()

            st.success(f"🎉 Role updated to: {new_role}. Redirecting...")
            time.sleep(2)

            # Update session and rerun
            st.session_state["user_role"] = new_role

            if new_role == "Startup Founder":
                st.switch_page("pages/founder_dashboard.py")
            elif new_role == "Analyst":
                st.switch_page("pages/analyst_dashboard.py")
            elif new_role == "Researcher":
                st.switch_page("pages/researcher_dashboard.py")
            else:
                st.warning("Unrecognized role, staying on profile page.")

        except Exception as e:
            st.error(f"❌ Failed to update role: {e}")
