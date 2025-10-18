import streamlit as st
from .analytics_panel import render_analytics_panel
from .settings_panel import render_settings_panel
from .upload_panel import render_upload_panel

def render_main_content():
    """Renders the main content area based on page selection."""
    page = st.session_state.get("page", "Chat")

    if page == "Data Management":
        render_upload_panel()
    elif page == "Analytics":
        render_analytics_panel()
    elif page == "Settings":
        render_settings_panel()

