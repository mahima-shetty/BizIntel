import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import streamlit as st
from components.sidebar import load_sidebar
from components.insights import display_insights
from components.charts import display_charts
from app.agents.aggregator import aggregate_news


# Global styles
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        box-sizing: border-box;
        padding: 0;
        margin: 0;
    }
    .stButton>button {
        background-color: #2E86AB;
        color: white;
        border: None;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #1B4F72;
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)



st.set_page_config(page_title="BizIntel Dashboard", layout="wide")

# Sidebar
user_prefs = load_sidebar()


# Fetch articles once
articles = aggregate_news(user_prefs["topic"], user_prefs["count"], user_prefs["sources"])


# Title
st.markdown("""
    <h1 style='text-align: center; color: #2E86AB; font-size: 40px; font-family: "Segoe UI", sans-serif;'>
        BizIntel : Autonomous Business Analyst Agent
    </h1>
    <p style='text-align: center; font-size: 18px; color: gray;'>
        Stay updated on the latest AI, Tech & Market news – curated by autonomous agents.
    </p>
""", unsafe_allow_html=True)



# Display insights
display_insights(user_prefs, articles)

# Display charts (if any)
display_charts(user_prefs, articles)