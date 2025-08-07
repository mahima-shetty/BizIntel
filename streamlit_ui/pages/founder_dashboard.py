# streamlit_ui/pages/founder_dashboard.py

import sys
import os
import streamlit as st
from bs4 import BeautifulSoup

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.agents.agentic_founder_dashboard import app
from utils.founder_prefs import load_founder_prefs, save_founder_prefs
from streamlit_ui.components.sidebar import render_sidebar


TRAILING_JUNK = ["TechCrunch", "Reuters", "CNBC", "NewsAPI"]
topic_options = ["AI", "Finance", "Technology", "Startups"]
freq_options = ["Daily", "Weekly", "Monthly"]
source_options = ["TechCrunch", "NewsAPI", "Reuters", "CNBC"]


# ─────────────────────────────────────────────
# 🧠 HTML Utility
def extract_main_text_and_link(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    link_tag = soup.find("a")
    link = link_tag["href"] if link_tag and link_tag.has_attr("href") else None
    text = soup.get_text(strip=True)
    return text, link


# ─────────────────────────────────────────────
# 🧠 Preferences Loader
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
# ⚙️ Preferences Form
def show_preferences_form(prefs):
    topic = prefs.get("topic", "Startups")
    count = int(prefs.get("count", 5))
    funding_count = int(prefs.get("funding_count", 5))
    sources = prefs.get("sources", ["TechCrunch", "NewsAPI"])
    notif_freq = prefs.get("notification_frequency", "Daily")

    topic = topic if topic in topic_options else topic_options[0]
    notif_freq = notif_freq if notif_freq in freq_options else freq_options[0]
    count = min(max(1, count), 10)
    funding_count = min(max(1, funding_count), 10)

    st.markdown("---")
    st.markdown("## Update Preferences:")
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




# def show_founder_dashboard():
#     st.title("🚀 Founder Dashboard")

#     user_email = st.session_state.get("user_email")
#     if not user_email:
#         st.error("⚠️ User not logged in.")
#         st.stop()

#     prefs = load_user_preferences(user_email)
#     render_sidebar("startup founder", prefs)
#     # Show Sections
#     show_news_section(prefs["topic"], prefs["count"], prefs["sources"])
#     show_funding_section(prefs["funding_count"])
#     updated_prefs = show_preferences_form(prefs)
#     if updated_prefs:
#         save_founder_prefs(user_email, updated_prefs)
#         st.success("✅ Preferences saved. Refreshing...")
#         st.rerun()


# def show_founder_dashboard():
#     st.title("🚀 Founder Dashboard")

#     user_email = st.session_state.get("user_email")
#     if not user_email:
#         st.error("⚠️ User not logged in.")
#         st.stop()

#     # Load preferences (or defaults)
#     prefs = load_user_preferences(user_email)

#     # Show agent-based autonomous output
#     st.write("### Generating AI Insights...")
#     with st.spinner("Thinking like an analyst..."):
#         report = run_founder_agent(prefs)

#     if "error" in report:
#         st.error("⚠️ Failed to generate insights. Try again.")
#     else:
#         # Market News
#         st.subheader("📢 Market News")
#         for news in report.get("market_news", []):
#             st.markdown(f"**[{news['title']}]({news['url']})** ({news['source']})")
#             st.caption(news["summary"])
#             st.markdown("---")

#         # Funding Updates
#         st.subheader("💰 Funding Updates")
#         for fund in report.get("funding_updates", []):
#             st.markdown(f"**[{fund['company']}]({fund['url']})** raised **${fund['amount']}** at a valuation of **{fund['valuation']}** ({fund['sector']})")
        

#         # Summary
#         st.subheader("📝 Summary")
#         st.info(report.get("summary", "No summary available."))

        
#         # Actionable Insights
#         st.subheader("📌 Actionable Insights")
#         for insight in report.get("insights", []):
#             st.markdown(f"- {insight}")

#         st.success("✅ Insights Ready!")
#         st.markdown(report)

# ─────────────────────────────────────────────
# 🚀 Founder Dashboard Main
def show_founder_dashboard():
    st.title("🚀 Founder Dashboard")
    user_email = st.session_state.get("user_email")
    if not user_email:
        st.error("⚠️ User not logged in.")
        st.stop()

    prefs = load_user_preferences(user_email)
    render_sidebar("startup founder", prefs)

    with st.spinner("🤖 Generating AI insights..."):
        result = app.invoke({"user_email": user_email})
    report = result.get("final_report", {})

    # Market News Section
    st.markdown("## 🗞️ Market Signals")
    for i, article in enumerate(report.get("market_news", [])):
        title = article.get("title", "No title")
        source = article.get("source", "Unknown")
        raw_content = article.get("content") or article.get("description") or ""
        content, extracted_link = extract_main_text_and_link(raw_content)

        # Clean redundant text
        title = title.strip()
        content = content.strip()
        if title and content.lower().startswith(title.lower()):
            content = content[len(title):].strip()
        for junk in TRAILING_JUNK:
            if content.lower().endswith(junk.lower()):
                content = content[:-len(junk)].strip()

        is_redundant = not content or len(content) < 20
        final_link = extracted_link or article.get("url")

        with st.expander(f"{i+1}. {title}"):
            st.markdown(f"### <b>{title}</b>", unsafe_allow_html=True)  # ⬅️ BIG BOLD TITLE
            st.write(f"📡 Source: {source}")
            
            if not is_redundant:
                st.write(content)

            if final_link:
                st.markdown(f"[🔗 Read Full Article]({final_link})", unsafe_allow_html=True)

            try:
                st.caption(f"🧠 Summary: {article['summary']}")
            except KeyError:
                st.caption("🧠 Summary: Not available.")

        st.markdown("---")

    # Funding Section
    st.markdown("## 💸 Startup Funding Highlights")
    for fund in report.get("funding_updates", []):
        with st.expander(fund.get("title", "Untitled")):
            st.write(f"**Source:** {fund.get('source', 'N/A')}")
            st.write(f"**Published:** {fund.get('published', 'N/A')}")
            st.markdown(f"[🔗 Read Full Article]({fund.get('url', '#')})", unsafe_allow_html=True)

    # # Summary
    # st.subheader("📝 Summary")
    # st.info(report.get("summary", "No summary available."))

    # # Insights
    # st.subheader("📌 Actionable Insights")
    # for insight in report.get("insights", []):
    #     st.markdown(f"- {insight}")

    # st.success("✅ Insights Ready!")

    # Preferences Update
    updated_prefs = show_preferences_form(prefs)
    if updated_prefs:
        save_founder_prefs(user_email, updated_prefs)
        st.success("✅ Preferences saved. Refreshing...")
        st.rerun()


# ─────────────────────────────────────────────
# 🔁 Streamlit Entry Point
if __name__ == "__main__" or __name__ == "__streamlit__":
    show_founder_dashboard()