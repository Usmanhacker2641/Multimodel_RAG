import streamlit as st

def render_settings_panel():
    """Renders the settings panel for model and RAG parameters."""
    st.title("⚙️ Settings")

    st.subheader("API Keys")
    hf_api_key = st.text_input("Hugging Face API Key", type="password", value=st.session_state.get("hf_api_key", ""))
    deepseek_api_key = st.text_input("DeepSeek API Key", type="password", value=st.session_state.get("deepseek_api_key", ""))
    gemini_api_key = st.text_input("Gemini API Key", type="password", value=st.session_state.get("gemini_api_key", ""))

    st.session_state.hf_api_key = hf_api_key
    st.session_state.deepseek_api_key = deepseek_api_key
    st.session_state.gemini_api_key = gemini_api_key

    st.subheader("Model Parameters")
    temp = st.slider("Temperature", 0.0, 2.0, st.session_state.get("temperature", 0.7), 0.1)
    max_tokens = st.slider("Max Tokens", 100, 32000, st.session_state.get("max_tokens", 2000), 100)
    
    st.session_state.temperature = temp
    st.session_state.max_tokens = max_tokens

    st.subheader("RAG Settings")
    chunk_size = st.slider("Chunk Size", 100, 5000, 1000, 100)
    top_k = st.slider("Top-K Chunks", 1, 20, 5, 1)

    if st.button("Save Settings"):
        # Here you would call an API to save the settings
        st.success("Settings saved!")
