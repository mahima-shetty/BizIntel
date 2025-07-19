# streamlit_ui/pages/researcher_dashboard.py

import streamlit as st
from streamlit_ui.utils.researcher_prefs import load_researcher_prefs, save_researcher_prefs
from streamlit_ui.components.sidebar import render_sidebar
from app.agents.deep_dive_agent import company_deep_dive

# ─────────────────────────────────────────────
# 🔍 Load or Default Preferences
def load_user_preferences(email):
    prefs = load_researcher_prefs(email)
    if not prefs:
        prefs = {
            "ticker": "AAPL",
            "depth": "standard"
        }
        st.warning("⚠️ No researcher preferences found. Using defaults.")
    return prefs

# ─────────────────────────────────────────────
# 🧠 Company Deep Dive Section
def show_company_deep_dive_section(prefs):
    st.subheader("🏢 Company Deep Dive")

    ticker = st.text_input("Enter Ticker Symbol", prefs.get("ticker", "AAPL")).upper()
    prefs["ticker"] = ticker

    if st.button("🔍 Run Deep Dive"):
        with st.spinner(f"Generating deep dive for {ticker}..."):
            output = company_deep_dive(ticker)
            st.markdown(output)

# ─────────────────────────────────────────────
# 📋 Preferences Section
def show_researcher_preferences_form(prefs):
    st.markdown("## ⚙️ Research Preferences")

    with st.form("update_researcher_prefs"):
        ticker = st.text_input("Default Ticker", prefs.get("ticker", "AAPL"))
        depth = st.selectbox("Depth of Analysis", ["standard", "deep"], index=0)
        submitted = st.form_submit_button("💾 Save Preferences")
        if submitted:
            return {"ticker": ticker, "depth": depth}
    return None

# ─────────────────────────────────────────────
# 🚀 Entry Point
def show_researcher_dashboard():
    st.title("🔬 Researcher Dashboard")

    user_email = st.session_state.get("user_email")
    if not user_email:
        st.error("⚠️ User not logged in.")
        st.stop()

    prefs = load_user_preferences(user_email)
    render_sidebar("researcher", prefs)

    show_company_deep_dive_section(prefs)
    st.markdown("---")

    updated_prefs = show_researcher_preferences_form(prefs)
    if updated_prefs:
        save_researcher_prefs(user_email, updated_prefs)
        st.success("✅ Preferences saved. Refreshing...")
        st.rerun()

# ⌛ Trigger
if __name__ == "__main__" or __name__ == "__streamlit__": 
    show_researcher_dashboard()
