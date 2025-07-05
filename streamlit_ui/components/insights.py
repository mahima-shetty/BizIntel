import streamlit as st
from app.agents.aggregator import aggregate_news as get_news_articles
from app.agents.summarization_agent import summarize_articles


def display_insights(user_prefs, articles):
    st.markdown("## Curated Insights")
    st.caption(f"Category selected: **{user_prefs.get('topic')}**")

    if not isinstance(articles, list) or len(articles) == 0:
        st.warning("🚫 No articles to display.")
        return

    for idx, article in enumerate(articles):
        with st.container():
            st.markdown(
                f"""
                <div style="
                    background-color: #ffffff;
                    box-shadow: 10px 5px 5px red;
                    border: 1px solid #e1e4e8;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                ">
                    <h4 style="color:#0a66c2; margin-bottom: 10px;">{article['title']}</h4>
                    <p style="color:#0a66c2;"><strong>Source:</strong> {article['source']}</p>
                    <p><a href="{article['url']}" target="_blank" style="text-decoration:none; color:#0366d6;">🔗 Read Full Article</a></p>
                </div>
                """,
                unsafe_allow_html=True
            )
             # "Fake" the button inside card by reducing margin
            col1, col2 = st.columns([0.05, 0.95])
            with col2:
                if st.button("📝 Summarize", key=f"summarize_{idx}"):
                    with st.spinner("Summarizing with LLaMA3..."):
                        summary = summarize_articles([article])
                        st.markdown("#### 📌 Summary")
                        st.success(summary)
                        
                        
            st.markdown(
                """<hr style='border: 1px solid #ddd; margin: 25px 0;'>""",
                unsafe_allow_html=True
            )
            # # Add Summarize Button just below the HTML card
            # if st.button("📝 Summarize", key=f"summarize_{idx}"):
            #     with st.spinner("Summarizing with LLaMA3..."):
            #         summary = summarize_articles([article])
            #         st.markdown(f"#### 📌 Summary", unsafe_allow_html=True)
            #         st.success(summary)
