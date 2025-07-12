# streamlit_ui/pages/user_profile.py

import streamlit as st
import sqlite3
import time
from components.auth_guard import require_login
from components.auth_ui import show_auth_ui
from components.auth_handler import handle_auth, get_current_user_data

from streamlit_ui.components.sidebar import render_sidebar

# ✅ Protect page
require_login()

# ✅ Sidebar login/logout
show_auth_ui()


token = st.session_state.get("token")
# if not token:
#     st.warning("Please login.")
#     st.stop()

user_data = get_current_user_data(token)
st.markdown(user_data)


role = user_data.get("role", "guest").lower()
prefs = user_data.get("preferences", {})



# ✅ Session vars
email = st.session_state["user_email"]
name = st.session_state["user_name"]

# 🔄 Fetch current role from DB
try:
    conn = sqlite3.connect("streamlit_ui/db/prefs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_type FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    current_role = row[0] if row else "Analyst"
    st.session_state["user_role"] = current_role  # ✅ from DB
    st.markdown(f"1st call from db role: {current_role}") #should be removed
except Exception as e:
    st.warning(f"⚠️ Could not fetch role from DB: {e}")
    current_role = "Analyst"

render_sidebar(role, prefs)


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
            st.markdown(f"2nd call from db role: {new_role}") #should be removed

            import requests

            
            try:
                response = requests.post("http://localhost:8000/refresh-token", json={
                    "email": email,
                    "role": new_role,
                    "username": name
                })

                if response.status_code == 200:
                    new_token = response.json()["token"]
                    st.session_state["token"] = new_token
                    st.success("✅ Role updated and token refreshed.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Role updated but failed to refresh JWT token.")

            except Exception as e:
                st.error(f"❌ Role updated but failed to refresh token: {e}")


        except Exception as e:
            st.error(f"❌ Failed to update role: {e}")
