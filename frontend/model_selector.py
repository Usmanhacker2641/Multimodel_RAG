import streamlit as st
from typing import Dict, List, Optional

# Model configurations with icons and details
MODEL_PROVIDERS = {
    "OpenAI": {
        "icon": "🤖",
        "color": "#10a37f",
        "models": [
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ],
        "description": "Advanced language models from OpenAI"
    },
    "Anthropic": {
        "icon": "🧠",
        "color": "#d4a373",
        "models": [
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            "claude-2.1"
        ],
        "description": "Constitutional AI models by Anthropic"
    },
    "Hugging Face": {
        "icon": "🤗",
        "color": "#ff9d00",
        "models": [
            "mistral-7B",
            "llama-2-7b",
            "llama-2-13b",
            "falcon-7b",
            "mpt-7b"
        ],
        "description": "Open-source models from Hugging Face"
    },
    "Google": {
        "icon": "🔷",
        "color": "#4285f4",
        "models": [
            "gemini-pro",
            "gemini-pro-vision",
            "palm-2"
        ],
        "description": "Google's generative AI models"
    },
    "Cohere": {
        "icon": "⚡",
        "color": "#39594d",
        "models": [
            "command",
            "command-light",
            "command-nightly"
        ],
        "description": "Enterprise-grade language models"
    }
}

def initialize_session_state():
    """Initialize session state variables for model selection."""
    if 'selected_providers' not in st.session_state:
        st.session_state.selected_providers = []
    if 'selected_models' not in st.session_state:
        st.session_state.selected_models = {}
    if 'model_configurations' not in st.session_state:
        st.session_state.model_configurations = {}

def apply_custom_styles():
    """Apply custom CSS styling for the model selector interface."""
    st.markdown("""
        <style>
        .model-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        .provider-box {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin: 15px 0;
            border-left: 5px solid;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        }
        
        .provider-box:hover {
            transform: translateX(5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        .model-header {
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            background: linear-gradient(120deg, #667eea, #764ba2, #f093fb);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 30px;
        }
        
        .provider-title {
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .model-description {
            color: #666;
            font-size: 0.95rem;
            margin-top: 8px;
            font-style: italic;
        }
        
        .selection-summary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin-top: 30px;
        }
        
        .stCheckbox > label {
            font-size: 1.1rem;
            font-weight: 500;
        }
        
        .model-dropdown {
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            font-size: 0.85rem;
            font-weight: 600;
            margin-left: 10px;
        }
        
        .control-panel-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_control_panel_header():
    """Render the main header for the model control panel."""
    st.markdown("""
        <div class="control-panel-header">
            <h1 style="margin: 0; font-size: 2.5rem;">🎛️ Model Control Panel</h1>
            <p style="margin-top: 10px; font-size: 1.1rem; opacity: 0.9;">
                Select and configure your AI models for intelligent document processing
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_provider_selection(provider_name: str, provider_data: Dict) -> bool:
    """
    Render a provider selection card with checkbox and details.
    
    Args:
        provider_name: Name of the AI provider
        provider_data: Dictionary containing provider details
        
    Returns:
        Boolean indicating if provider is selected
    """
    col1, col2 = st.columns([1, 20])
    
    with col1:
        st.markdown(f"<div style='font-size: 2rem;'>{provider_data['icon']}</div>", 
                   unsafe_allow_html=True)
    
    with col2:
        is_selected = st.checkbox(
            f"{provider_name}",
            key=f"provider_{provider_name}",
            value=provider_name in st.session_state.selected_providers
        )
        st.markdown(f"<div class='model-description'>{provider_data['description']}</div>", 
                   unsafe_allow_html=True)
    
    return is_selected

def render_model_dropdown(provider_name: str, models: List[str]):
    """
    Render model selection dropdown for a specific provider.
    
    Args:
        provider_name: Name of the AI provider
        models: List of available models
    """
    st.markdown("<div class='model-dropdown'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_model = st.selectbox(
            f"Select {provider_name} Model",
            options=[""] + models,
            key=f"model_{provider_name}",
            help=f"Choose a specific model from {provider_name}"
        )
        
        if selected_model:
            st.session_state.selected_models[provider_name] = selected_model
    
    with col2:
        if provider_name in st.session_state.selected_models:
            if st.button("🗑️ Remove", key=f"remove_{provider_name}"):
                st.session_state.selected_models.pop(provider_name, None)
                st.rerun()
    
    # Advanced configuration options
    if selected_model:
        with st.expander("⚙️ Advanced Settings"):
            temp = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                key=f"temp_{provider_name}",
                help="Controls randomness in responses"
            )
            
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=8000,
                value=2000,
                step=100,
                key=f"tokens_{provider_name}",
                help="Maximum length of generated response"
            )
            
            st.session_state.model_configurations[provider_name] = {
                "model": selected_model,
                "temperature": temp,
                "max_tokens": max_tokens
            }
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_selection_summary():
    """Render a summary of all selected models and configurations."""
    if st.session_state.selected_models:
        st.markdown("---")
        st.markdown("### 📊 Active Model Configuration")
        
        for provider, model in st.session_state.selected_models.items():
            config = st.session_state.model_configurations.get(provider, {})
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                icon = MODEL_PROVIDERS[provider]["icon"]
                st.markdown(f"**{icon} {provider}**")
            
            with col2:
                st.info(f"Model: `{model}`")
            
            with col3:
                if config:
                    st.caption(f"🌡️ {config.get('temperature', 'N/A')}")
        
        # Export configuration button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("💾 Save Configuration", use_container_width=True):
                st.success("✅ Configuration saved to session state!")
                st.balloons()

def get_selected_configuration() -> Dict:
    """
    Get the complete model configuration from session state.
    
    Returns:
        Dictionary containing all selected models and their configurations
    """
    return {
        "providers": st.session_state.selected_providers,
        "models": st.session_state.selected_models,
        "configurations": st.session_state.model_configurations
    }

def main():
    """Main function to render the model selector interface."""
    # Initialize session state
    initialize_session_state()
    
    # Apply custom styling
    apply_custom_styles()
    
    # Render header
    render_control_panel_header()
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["🎯 Model Selection", "📋 Configuration Summary"])
    
    with tab1:
        st.markdown("### Select Your AI Providers")
        st.markdown("Choose one or more AI providers to power your document processing pipeline")
        
        # Track current selections
        current_selections = []
        
        # Render each provider
        for provider_name, provider_data in MODEL_PROVIDERS.items():
            with st.container():
                st.markdown(
                    f"<div class='provider-box' style='border-left-color: {provider_data['color']};'>",
                    unsafe_allow_html=True
                )
                
                is_selected = render_provider_selection(provider_name, provider_data)
                
                if is_selected:
                    current_selections.append(provider_name)
                    render_model_dropdown(provider_name, provider_data['models'])
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Update session state
        st.session_state.selected_providers = current_selections
    
    with tab2:
        st.markdown("### 📊 Current Configuration")
        
        if not st.session_state.selected_models:
            st.info("👈 No models selected yet. Please select providers and models from the selection tab.")
        else:
            render_selection_summary()
            
            # Display JSON configuration
            with st.expander("🔍 View Raw Configuration"):
                st.json(get_selected_configuration())

if __name__ == "__main__":
    main()