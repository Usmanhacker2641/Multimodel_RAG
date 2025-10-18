import streamlit as st
import time
from datetime import datetime
from frontend.api_client import query_rag

def render_chat_interface():
    """Renders the chat history, query input, and multi-model response cards connected to the backend."""
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'last_response' not in st.session_state:
        st.session_state.last_response = None

    # Display past messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    user_query = st.chat_input("Ask a question about your documents...")

    if user_query:
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_query)
        
        # Add to message history
        st.session_state.messages.append({
            "role": "user",
            "content": user_query,
            "timestamp": datetime.now().isoformat()
        })

        # Query the backend
        with st.spinner("🔍 Searching knowledge base and generating responses..."):
            # Prepare API keys from session state
            api_keys = {}
            if st.session_state.get("hf_api_key"):
                api_keys["hf_api_key"] = st.session_state["hf_api_key"]
            if st.session_state.get("deepseek_api_key"):
                api_keys["deepseek_api_key"] = st.session_state["deepseek_api_key"]
            if st.session_state.get("gemini_api_key"):
                api_keys["gemini_api_key"] = st.session_state["gemini_api_key"]
            
            response = query_rag(user_query, mode="rag", top_k=5, api_keys=api_keys if api_keys else None)

        if response.get("status") == "error":
            st.error(f"❌ Query failed: {response.get('message', 'Unknown error')}")
        elif response.get("status") == "success":
            st.session_state.last_response = response
            
            # Display assistant's aggregated answer
            final_answer = response.get("final_answer", "")
            if final_answer:
                with st.chat_message("assistant"):
                    st.markdown(final_answer)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_answer,
                    "timestamp": datetime.now().isoformat()
                })

    # Display multi-model responses if available
    if st.session_state.last_response:
        response = st.session_state.last_response
        multi_llm_answers = response.get("multi_llm_answers", [])
        retrieved_chunks = response.get("retrieved_chunks", [])

        if multi_llm_answers:
            st.markdown("---")
            st.subheader("🤖 Individual Model Responses")
            
            # Display in columns
            cols = st.columns(min(len(multi_llm_answers), 3))
            
            for idx, model_resp in enumerate(multi_llm_answers):
                col_idx = idx % len(cols)
                with cols[col_idx]:
                    render_model_card(model_resp)

        if retrieved_chunks:
            st.markdown("---")
            with st.expander(f"📚 Retrieved Context ({len(retrieved_chunks)} chunks)"):
                for idx, chunk in enumerate(retrieved_chunks, 1):
                    st.markdown(f"**Chunk {idx}** (score: {chunk.get('score', 0):.3f})")
                    st.markdown(f"> {chunk.get('text', '')[:300]}...")
                    if chunk.get("metadata"):
                        st.caption(f"Source: {chunk['metadata'].get('source', 'unknown')}")
                    st.markdown("---")


def render_model_card(model_response: dict):
    """Render an individual model response card."""
    model_label = model_response.get("model_label", "Model")
    response_text = model_response.get("response", "")
    confidence = model_response.get("confidence", 0.0)
    tokens = model_response.get("tokens", 0)
    latency = model_response.get("latency_ms", 0)

    st.markdown(f"""
        <div class="card response-card">
            <h3>{model_label}</h3>
            <p class="metadata">{latency/1000:.1f}s • {tokens} tokens</p>
            <div style="margin: 1rem 0;">
                {response_text}
            </div>
            <p align="right">Confidence: {confidence*100:.0f}%</p>
        </div>
    """, unsafe_allow_html=True)
