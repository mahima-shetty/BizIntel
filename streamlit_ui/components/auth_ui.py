# streamlit_ui/components/auth_ui.py

import streamlit as st

def show_auth_ui():
    st.sidebar.markdown("### 🔐 Session Control")
    if "user_email" in st.session_state:
        st.sidebar.success(f"{st.session_state['user_email']}")
        if st.sidebar.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.query_params.clear()
            st.rerun()
    else:
        st.sidebar.warning("You're not logged in.")
        st.sidebar.markdown("[🔐 Login](http://localhost:8000/login)")
