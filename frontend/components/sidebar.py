import streamlit as st

def render_sidebar():
    """Renders the sidebar with all the controls from the image."""
    st.header("Multi-LLM RAG Chat")
    
    # Mode Selection
    st.subheader("Mode Selection")
    st.radio("Mode", ["RAG Mode", "Multi-LLM"], key="mode_selection", horizontal=True)

    st.markdown("---")

    # Model Selection
    st.subheader("Select Models")
    st.checkbox("GPT-4 Turbo", value=True, key="model_gpt4_turbo")
    st.checkbox("UX Pilot 3 Sonnet", value=True, key="model_ux_pilot_3")
    st.checkbox("Llama 2 70B", value=False, key="model_llama2_70b")
    st.checkbox("Mistral Large", value=False, key="model_mistral_large")
    st.checkbox("Enable Aggregator LLM", value=True, key="enable_aggregator")

    st.markdown("---")

    # Parameters
    st.subheader("Parameters")
    st.slider("Chunk Size", 512, 4096, 512, key="chunk_size")
    st.slider("Chunk Overlap", 0, 512, 50, key="chunk_overlap")
    st.slider("Temperature", 0.0, 1.0, 0.7, key="temperature")
    st.slider("Top P", 0.0, 1.0, 0.9, key="top_p")
    st.slider("Max Tokens", 256, 4096, 1024, key="max_tokens")
    st.number_input("Top K", 1, 20, 10, key="top_k")
