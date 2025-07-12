# streamlit_ui/pages/founder_dashboard.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
from bs4 import BeautifulSoup
from app.agents.aggregator import aggregate_news
from app.agents.summarization_agent import summarize_articles
from app.agents.funding_agent import fetch_funding_news
from utils.founder_prefs import load_founder_prefs, save_founder_prefs
from streamlit_ui.components.sidebar import render_sidebar


TRAILING_JUNK = ["TechCrunch", "Reuters", "CNBC", "NewsAPI"]
topic_options = ["AI", "Finance", "Technology", "Startups"]
freq_options = ["Daily", "Weekly", "Monthly"]
source_options = ["TechCrunch", "NewsAPI", "Reuters", "CNBC"]


# ─────────────────────────────────────────────
# 🧠 Utility: HTML extraction
def extract_main_text_and_link(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    link_tag = soup.find("a")
    link = link_tag["href"] if link_tag and link_tag.has_attr("href") else None
    text = soup.get_text(strip=True)
    return text, link


# ─────────────────────────────────────────────
# 📩 Section 1: Load user preferences
def load_user_preferences(email):
    prefs = load_founder_prefs(email)
    if not prefs:
        prefs = {
            "topic": "Startups",
            "count": 5,
            "funding_count": 5,
            "sources": ["TechCrunch", "NewsAPI"],
            "notification_frequency": "Daily"
        }
        st.warning("⚠️ No preferences found. Using defaults.")
    return prefs


# ─────────────────────────────────────────────
# 📰 Section 2: Show daily market news
def show_news_section(topic, count, sources):
    articles = aggregate_news(topic, count, sources)
    st.markdown("## 🗞️ Market Signals")

    for i, article in enumerate(articles):
        st.markdown(f"### {i+1}. {article.get('title', 'No title')}")
        st.write(f"📡 Source: {article.get('source', 'Unknown')}")

        raw_content = article.get("content") or article.get("description") or ""
        content, extracted_link = extract_main_text_and_link(raw_content)

        title = article.get("title", "").strip()
        content = content.strip()

        if title and content.lower().startswith(title.lower()):
            content = content[len(title):].strip()

        for junk in TRAILING_JUNK:
            if content.lower().endswith(junk.lower()):
                content = content[:-len(junk)].strip()

        is_redundant = not content or len(content) < 20

        if is_redundant:
            st.info("📖 Read more through the link below.")
        else:
            st.write(content)

        final_link = extracted_link or article.get("url")
        if final_link:
            st.markdown(f"[🔗 Read Full Article]({final_link})", unsafe_allow_html=True)

        if not is_redundant:
            if st.button(f"🧠 Summarize", key=f"summarize_{i}"):
                with st.spinner("Summarizing..."):
                    summary = summarize_articles([article])
                    st.success(summary)

        st.markdown("---")


# ─────────────────────────────────────────────
# 💸 Section 3: Funding Highlights
def show_funding_section(funding_count):
    st.markdown("## 💸 Startup Funding Highlights")
    funding_news = fetch_funding_news(count=funding_count)

    if not funding_news:
        st.info("No funding news found right now.")
    else:
        for f in funding_news:
            with st.expander(f["title"]):
                st.write(f"**Source:** {f['source']}")
                st.write(f"**Published:** {f.get('published', 'N/A')}")
                st.markdown(f"[🔗 Read Full Article]({f['url']})", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ⚙️ Section 4: Preferences Update Form
def show_preferences_form(prefs):
    topic_options = ["AI", "Finance", "Technology", "Startups"]
    freq_options = ["Daily", "Weekly", "Monthly"]
    source_options = ["TechCrunch", "NewsAPI", "Reuters", "CNBC"]

    # Set defaults with fallback
    topic = prefs.get("topic", "Startups")
    count = int(prefs.get("count", 5))
    funding_count = int(prefs.get("funding_count", 5))
    sources = prefs.get("sources", ["TechCrunch", "NewsAPI"])
    notif_freq = prefs.get("notification_frequency", "Daily")

    # Validate values
    topic = topic if topic in topic_options else topic_options[0]
    notif_freq = notif_freq if notif_freq in freq_options else freq_options[0]
    if not isinstance(count, int) or not (1 <= count <= 10):
        count = 5
    if not isinstance(funding_count, int) or not (1 <= funding_count <= 10):
        funding_count = 5

    st.markdown("---")
    
    st.markdown("## Update Preferences: ")
    with st.form("update_prefs_form"):
        topic = st.selectbox("📌 Topic", topic_options, index=topic_options.index(topic))
        count = st.slider("📰 Article Count", 1, 10, count)
        funding_count = st.slider("💸 Funding Count", 1, 10, funding_count)
        sources = st.multiselect("📡 Sources", source_options, default=sources)
        notif_freq = st.selectbox("⏰ Notification Frequency", freq_options, index=freq_options.index(notif_freq))

        submitted = st.form_submit_button("💾 Save Preferences")
        if submitted:
            updated_prefs = {
                "topic": topic,
                "count": count,
                "funding_count": funding_count,
                "sources": sources,
                "notification_frequency": notif_freq
            }
            return updated_prefs
    return None



# ─────────────────────────────────────────────
# 🚀 Main Entry Point
def show_founder_dashboard():
    st.title("🚀 Founder Dashboard")

    user_email = st.session_state.get("user_email")
    if not user_email:
        st.error("⚠️ User not logged in.")
        st.stop()

    prefs = load_user_preferences(user_email)
    render_sidebar("startup founder", prefs)
    # Show Sections
    show_news_section(prefs["topic"], prefs["count"], prefs["sources"])
    show_funding_section(prefs["funding_count"])
    updated_prefs = show_preferences_form(prefs)
    if updated_prefs:
        save_founder_prefs(user_email, updated_prefs)
        st.success("✅ Preferences saved. Refreshing...")
        st.rerun()


# At bottom of founder_dashboard.py
if __name__ == "__main__" or __name__ == "__streamlit__":
    show_founder_dashboard()