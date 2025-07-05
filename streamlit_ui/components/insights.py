import streamlit as st
import requests
from app.agents.aggregator import aggregate_news as get_news_articles



def display_insights(user_prefs, articles):
    print(user_prefs)
    print(type(user_prefs))
    articles = get_news_articles(topic=user_prefs["topic"], count=user_prefs["count"])
    
    
    
    # print("Articles type:", type(articles))
    # print("Articles data:", articles)


    # ✅ Check if articles is a list
    if not isinstance(articles, list):
        st.warning("No articles to display.")
        return
    
    st.write("Category selected:", user_prefs.get("topic"))

    
    for article in articles:
        st.markdown(f"**{article['title']}**")
        st.markdown(f"*Source:* {article['source']}  \n[Read more]({article['url']})")
        st.markdown("---")