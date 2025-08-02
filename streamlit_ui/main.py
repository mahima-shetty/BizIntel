import streamlit as st
from components.auth_handler import handle_auth, get_current_user_data
from components.sidebar import render_sidebar
from streamlit_extras.switch_page_button import switch_page  # if you use external lib

st.set_page_config(page_title="BizIntel", layout="wide")

# Step 1: Handle login/authentication
handle_auth()

# Step 2: Read token and decode user info
token = st.session_state.get("token")
# if not token:
#     st.warning("Please login.")
#     st.stop()

user_data = get_current_user_data(token)
st.markdown(user_data)


role = user_data.get("role", "guest").lower()
prefs = user_data.get("preferences", {})



# Step 3: Render the sidebar
render_sidebar(role, prefs)

# # Step 4: Main content (optional home view)
# st.title("🏠 Welcome to BizIntel")
# st.markdown(f"Hello **{user_data.get('username', 'user')}** 👋")
# st.markdown("Use the sidebar to navigate your personalized dashboard.")

# # Step 4: Route to role-specific dashboard
# from pages.founder_dashboard import show_founder_dashboard
# You can import others later: analyst, researcher

st.info(f"Role (raw): {user_data.get('role')}")
st.info(f"Role (normalized): {role}")

# st.markdown("Use the sidebar to navigate your personalized dashboard.")
# if role == "startup founder":
#     show_founder_dashboard()
# elif role == "analyst":
#     st.info("🧠 Analyst Dashboard coming soon.")
# elif role == "researcher":
#     st.info("🔬 Researcher Dashboard coming soon.")
# else:
#     st.warning("❓ Unknown role. Please contact support.")



# ✅ Optional: Debug info (remove in production)
# st.caption("🔐 Debug Info:")
# st.json(user_data)


if role == "startup founder":
    st.switch_page("pages/founder_dashboard.py")
elif role == "analyst":
    st.switch_page("pages/analyst_dashboard.py")
elif role == "researcher":
    st.switch_page("pages/researcher_dashboard.py")
else:
    st.warning("❓ Unrecognized role.")