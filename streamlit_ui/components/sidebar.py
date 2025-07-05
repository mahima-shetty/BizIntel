import streamlit as st

def load_sidebar():
    
    st.sidebar.image("streamlit_ui/assets/logonew.jpg", use_container_width=True)
    st.sidebar.markdown("### 🔍 Filter Preferences")

    topic = st.sidebar.selectbox("Select Topic", ["AI", "Finance", "Technology", "Startups"])
    count = st.sidebar.slider("Number of Articles", 5, 20, 10)
    sources = st.sidebar.multiselect(
        "Preferred News Sources",
        ["TechCrunch", "Reuters", "CNBC", "NewsAPI"],
        default=["TechCrunch", "Reuters"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("Crafted with 💙 for GenAI enthusiasts.")
    return {"topic": topic, "count": count, "sources" : sources}


    
