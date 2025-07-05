import streamlit as st
from app.agents.aggregator import aggregate_news as get_news_articles
from app.agents.summarization_agent import summarize_articles 

def display_insights(user_prefs, articles):
    st.write("Category selected:", user_prefs.get("topic"))

    

    if not isinstance(articles, list) or len(articles) == 0:
        st.warning("No articles to display.")
        return

    for idx, article in enumerate(articles):
        with st.container():
            st.markdown(f"**{article['title']}**")
            st.markdown(f"*Source:* {article['source']}  \n[Read more]({article['url']})")

            # Use a unique key per button to track state
            if st.button("Summarize", key=f"summarize_{idx}"):
                with st.spinner("Summarizing with LLaMA3..."):
                    summary = summarize_articles([article])  # Wrap in list
                    st.success(summary)

            st.markdown("---")
