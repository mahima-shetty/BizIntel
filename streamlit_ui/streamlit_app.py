# streamlit_ui/streamlit_app.py

from components.auth_handler import handle_auth

# Handle Google login, JWT token parsing, session, and logout
handle_auth()

# 🧠 Add your main dashboard UI below (for logged-in users only)
# You can route to different pages based on user email/role here
