import streamlit as st

def render_sidebar(role, prefs):
    st.sidebar.title("📊 BizIntel")
    
    st.sidebar.markdown(f"**Role:** `{role.capitalize()}`")
    
    st.sidebar.markdown("---")
    

    # Role-based navigation links
    if role == "founder":
        st.sidebar.page_link("pages/founder_dashboard.py", label="Founder Dashboard")
    elif role == "analyst":
        st.sidebar.page_link("pages/analyst_dashboard.py", label="Analyst Dashboard")
    elif role == "researcher":
        st.sidebar.page_link("pages/researcher_dashboard.py", label="Researcher Dashboard")
    else:
        # 🧯 Fallback for unknown role
        st.sidebar.warning("❓ Unknown role. Defaulting to Analyst.")
        st.sidebar.page_link("pages/analyst_dashboard.py", label="📊 Analyst Dashboard")

    st.sidebar.page_link("pages/user_profile.py", label="👤 Profile / Preferences")
    st.sidebar.markdown("---")
