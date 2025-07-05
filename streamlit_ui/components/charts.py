import streamlit as st
import plotly.express as px
import pandas as pd
from collections import Counter

def display_charts(prefs, articles):
    if not articles:
        st.warning("No data available to display charts.")
        return

    # Count the number of articles per source
    source_counts = Counter([a.get("source", "Unknown") for a in articles])
    df = pd.DataFrame({
        "Source": list(source_counts.keys()),
        "Articles": list(source_counts.values())
    })

    st.markdown("### 📊 Source Contribution")
    fig = px.pie(df, names='Source', values='Articles', title=f"Article Distribution by Source - {prefs['topic']}")
    st.plotly_chart(fig, use_container_width=True)
