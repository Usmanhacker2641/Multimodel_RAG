import streamlit as st
from frontend.model_selector import main as _model_selector_main


def render_model_selector():
    _model_selector_main()
