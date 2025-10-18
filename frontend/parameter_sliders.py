import streamlit as st

def render_parameter_sliders():
    """
    Renders advanced parameter sliders for fine-tuning generation behavior.
    Includes temperature, top-p, max tokens, penalties, and chunk size controls.
    """
    
    with st.expander("🎛️ Advanced Settings", expanded=False):
        st.markdown("""
            <style>
            .slider-container {
                padding: 15px;
                border-radius: 10px;
                background-color: #f8f9fa;
                margin-bottom: 15px;
                border-left: 4px solid #4CAF50;
            }
            .param-label {
                color: #555;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 5px;
            }
            .param-description {
                color: #777;
                font-size: 12px;
                font-style: italic;
                margin-bottom: 10px;
            }
            .section-divider {
                border-top: 1px solid #e0e0e0;
                margin: 20px 0;
            }
            .section-title {
                color: #333;
                font-size: 16px;
                font-weight: 700;
                margin-bottom: 15px;
                padding-left: 10px;
                border-left: 3px solid #2196F3;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Generation Parameters Section
        st.markdown('<div class="section-title">🔥 Generation Parameters</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="param-label">Temperature</div>', unsafe_allow_html=True)
            temperature = st.slider(
                "temp_slider",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Controls randomness in responses. Lower = more focused, Higher = more creative",
                label_visibility="collapsed"
            )
            st.markdown(f'<div class="param-description">Current: {temperature} | Controls creativity</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="param-label">Top P (Nucleus Sampling)</div>', unsafe_allow_html=True)
            top_p = st.slider(
                "top_p_slider",
                min_value=0.0,
                max_value=1.0,
                value=0.9,
                step=0.05,
                help="Controls diversity via nucleus sampling. Considers tokens with top_p probability mass",
                label_visibility="collapsed"
            )
            st.markdown(f'<div class="param-description">Current: {top_p} | Controls diversity</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Token and Length Controls
        st.markdown('<div class="section-title">📝 Token & Length Controls</div>', unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown('<div class="param-label">Max Output Tokens</div>', unsafe_allow_html=True)
            max_tokens = st.number_input(
                "max_tokens_input",
                min_value=50,
                max_value=4096,
                value=1024,
                step=50,
                help="Maximum number of tokens to generate in the response",
                label_visibility="collapsed"
            )
            st.markdown(f'<div class="param-description">Current: {max_tokens} tokens | Maximum response length</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="param-label">Chunk Size</div>', unsafe_allow_html=True)
            chunk_size = st.number_input(
                "chunk_size_input",
                min_value=100,
                max_value=2000,
                value=500,
                step=50,
                help="Size of text chunks for document processing and retrieval",
                label_visibility="collapsed"
            )
            st.markdown(f'<div class="param-description">Current: {chunk_size} chars | Document split size</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Penalty Parameters Section
        st.markdown('<div class="section-title">⚖️ Penalty Parameters</div>', unsafe_allow_html=True)
        
        col5, col6 = st.columns(2)
        
        with col5:
            st.markdown('<div class="param-label">Frequency Penalty</div>', unsafe_allow_html=True)
            frequency_penalty = st.slider(
                "freq_penalty_slider",
                min_value=0.0,
                max_value=2.0,
                value=0.0,
                step=0.1,
                help="Reduces repetition of tokens based on their frequency. Higher = less repetition",
                label_visibility="collapsed"
            )
            st.markdown(f'<div class="param-description">Current: {frequency_penalty} | Reduces word repetition</div>', unsafe_allow_html=True)
        
        with col6:
            st.markdown('<div class="param-label">Presence Penalty</div>', unsafe_allow_html=True)
            presence_penalty = st.slider(
                "pres_penalty_slider",
                min_value=0.0,
                max_value=2.0,
                value=0.0,
                step=0.1,
                help="Encourages new topics by penalizing tokens that have already appeared",
                label_visibility="collapsed"
            )
            st.markdown(f'<div class="param-description">Current: {presence_penalty} | Encourages topic diversity</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Advanced Retrieval Settings
        st.markdown('<div class="section-title">🔍 Retrieval Settings</div>', unsafe_allow_html=True)
        
        col7, col8 = st.columns(2)
        
        with col7:
            st.markdown('<div class="param-label">Top K Results</div>', unsafe_allow_html=True)
            top_k = st.slider(
                "top_k_slider",
                min_value=1,
                max_value=20,
                value=5,
                step=1,
                help="Number of most relevant chunks to retrieve from documents",
                label_visibility="collapsed"
            )
            st.markdown(f'<div class="param-description">Current: {top_k} chunks | Retrieval depth</div>', unsafe_allow_html=True)
        
        with col8:
            st.markdown('<div class="param-label">Chunk Overlap</div>', unsafe_allow_html=True)
            chunk_overlap = st.number_input(
                "chunk_overlap_input",
                min_value=0,
                max_value=500,
                value=50,
                step=10,
                help="Number of overlapping characters between consecutive chunks",
                label_visibility="collapsed"
            )
            st.markdown(f'<div class="param-description">Current: {chunk_overlap} chars | Context preservation</div>', unsafe_allow_html=True)
        
        # Reset to Defaults Button
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 1])
        with col_reset2:
            if st.button("🔄 Reset to Defaults", use_container_width=True):
                st.rerun()
        
        # Return all parameters as a dictionary
        return {
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "chunk_size": chunk_size,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "top_k": top_k,
            "chunk_overlap": chunk_overlap
        }


def get_default_parameters():
    """
    Returns default parameter values.
    """
    return {
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 1024,
        "chunk_size": 500,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "top_k": 5,
        "chunk_overlap": 50
    }


# Example usage in main app
if __name__ == "__main__":
    st.set_page_config(page_title="Parameter Sliders", layout="wide")
    st.title("🎚️ Advanced Parameter Control Panel")
    
    st.markdown("""
        Fine-tune your generation behavior with precision controls.
        Each parameter is carefully calibrated for optimal performance.
    """)
    
    params = render_parameter_sliders()
    
    # Display selected parameters
    st.markdown("---")
    st.subheader("📊 Current Configuration")
    st.json(params)