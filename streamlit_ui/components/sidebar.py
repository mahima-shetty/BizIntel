import streamlit as st

def load_sidebar():
    st.sidebar.image("C:/Users/msshe/Documents/Projects/BizIntel/streamlit_ui/assets/logonew.jpg",  use_container_width=True)
    st.sidebar.markdown("### 🔍 Filter Preferences")

    topic = st.sidebar.selectbox("Select Topic", ["AI", "Finance", "Technology", "Startups"])
    count = st.sidebar.slider("No. of Articles", 5, 20, 10)

    st.sidebar.markdown("---")
    st.sidebar.markdown("Crafted with 💙 for GenAI enthusiasts.")

    return {"topic": topic, "count": count}
