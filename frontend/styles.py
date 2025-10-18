import streamlit as st

def set_page_config():
    st.set_page_config(
        page_title="Multimodel RAG",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def apply_custom_css():
    st.markdown("""
        <style>
            /* Main app background */
            .main {
                background-color: #f0f2f6;
            }
            
            /* Sidebar styling */
            .css-1d391kg {
                background-color: #ffffff;
                border-right: 1px solid #e6e6e6;
            }
            
            /* Buttons */
            .stButton>button {
                background-color: #4CAF50;
                color: white;
                border-radius: 8px;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                transition-duration: 0.4s;
            }
            .stButton>button:hover {
                background-color: #45a049;
            }
            
            /* Chat messages */
            .st-emotion-cache-1c7y2kd {
                background-color: #ffffff;
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 1rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
            }
            
            /* User message */
            .st-emotion-cache-1c7y2kd.user-message {
                background-color: #e1f5fe;
            }
            
            /* Assistant message */
            .st-emotion-cache-1c7y2kd.assistant-message {
                background-color: #f1f8e9;
            }
            
            /* Headers */
            h1, h2, h3 {
                color: #2c3e50;
            }
        </style>
    """, unsafe_allow_html=True)
