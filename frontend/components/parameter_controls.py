import streamlit as st
from frontend.parameter_sliders import render_parameter_sliders, get_default_parameters


def render_parameter_controls():
    params = render_parameter_sliders()
    # Sync a few common params back to session_state for app-level use
    st.session_state.temperature = params.get("temperature", st.session_state.get("temperature", 0.7))
    st.session_state.top_p = params.get("top_p", st.session_state.get("top_p", 0.9))
    st.session_state.max_tokens = params.get("max_tokens", st.session_state.get("max_tokens", 1024))
