import streamlit as st
from frontend.components.chat_interface import render_chat_interface
from frontend.components.settings_panel import render_settings_panel
from frontend.upload_panel import render_upload_panel
from frontend.styles import apply_custom_css
from frontend.session_manager import SessionManager

def main():
    """Main function to run the Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="Multi-LLM RAG System",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_custom_css()
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'page' not in st.session_state:
        st.session_state.page = "Chat"
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🤖 Multi-LLM RAG")
        st.markdown("---")
        
        # Navigation buttons
        if st.button("💬 Chat", use_container_width=True, type="primary" if st.session_state.page == "Chat" else "secondary"):
            st.session_state.page = "Chat"
            st.rerun()
        
        if st.button("📤 Upload", use_container_width=True, type="primary" if st.session_state.page == "Upload" else "secondary"):
            st.session_state.page = "Upload"
            st.rerun()
        
        if st.button("⚙️ Settings & API Keys", use_container_width=True, type="primary" if st.session_state.page == "Settings" else "secondary"):
            st.session_state.page = "Settings"
            st.rerun()
        
        st.markdown("---")
        
        # Model selection
        st.subheader("🎯 Active Models")
        st.checkbox("Mistral 7B (HuggingFace)", value=True, key="model_mistral_7b")
        st.checkbox("DeepSeek Chat", value=True, key="model_deepseek_chat")
        st.checkbox("Gemini Pro", value=True, key="model_gemini_pro")
        st.checkbox("Falcon 7B (HuggingFace)", value=False, key="model_falcon_7b")
        st.checkbox("Zephyr 7B (HuggingFace)", value=False, key="model_zephyr_7b")
        
        st.markdown("---")
        
        # Quick settings
        st.subheader("⚡ Quick Settings")
        st.slider("Top K Chunks", 1, 20, 5, key="top_k_chunks")
        st.selectbox("Mode", ["RAG Mode", "Direct Mode"], key="query_mode")
        
        st.markdown("---")
        
        # API Status
        st.subheader("🔑 API Status")
        hf_status = "✅" if st.session_state.get("hf_api_key") else "❌"
        ds_status = "✅" if st.session_state.get("deepseek_api_key") else "❌"
        gm_status = "✅" if st.session_state.get("gemini_api_key") else "❌"
        
        st.markdown(f"""
        - HuggingFace: {hf_status}
        - DeepSeek: {ds_status}
        - Gemini: {gm_status}
        """)
        
        if not any([st.session_state.get("hf_api_key"), st.session_state.get("deepseek_api_key"), st.session_state.get("gemini_api_key")]):
            st.warning("⚠️ Add API keys in Settings to enable real responses")
    
    # Main content area
    if st.session_state.page == "Chat":
        render_chat_interface()
    elif st.session_state.page == "Upload":
        render_upload_panel()
    elif st.session_state.page == "Settings":
        render_settings_panel()

if __name__ == "__main__":
    main()