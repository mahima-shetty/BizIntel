import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import streamlit as st
from components.sidebar import load_sidebar
from components.insights import display_insights
from components.charts import display_charts
from app.agents.aggregator import aggregate_news


# after user_prefs loaded



st.set_page_config(page_title="BizIntel Dashboard", layout="wide")

# Sidebar
user_prefs = load_sidebar()


# Fetch articles once
articles = aggregate_news(user_prefs["topic"], user_prefs["count"])

# Title
st.markdown("<h1 style='color:#2E86AB;'>🧠 BizIntel AI News Dashboard</h1>", unsafe_allow_html=True)
st.markdown("Stay updated on the latest AI, Tech & Market news – curated by autonomous agents.")

# Display insights
display_insights(user_prefs, articles)

# Display charts (if any)
display_charts(user_prefs, articles)