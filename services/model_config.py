"""
Model configuration service for managing LLM and RAG parameters.
"""
from typing import Dict, Any
import json
import os
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 2000,
    "freq_penalty": 0.0,
    "pres_penalty": 0.0,
    "chunk_size": 1000,
    "top_k": 5,
    "models": [
        "google/flan-t5-base",
        "microsoft/phi-2",
        "mistralai/Mistral-7B-Instruct-v0.2"
    ]
}

CONFIG_FILE = "model_config.json"


def get_model_settings() -> Dict[str, Any]:
    """
    Get current model configuration settings.
    
    Returns:
        Dictionary of current model settings
    """
    config_path = Path(CONFIG_FILE)
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    
    return DEFAULT_CONFIG.copy()


def update_model_settings(**kwargs) -> Dict[str, Any]:
    """
    Update model configuration settings.
    
    Args:
        **kwargs: Settings to update
    
    Returns:
        Updated configuration dictionary
    """
    current_config = get_model_settings()
    
    # Update with provided values
    current_config.update(kwargs)
    
    # Save to file
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(current_config, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save config to file: {e}")
    
    return current_config


def reset_model_settings() -> Dict[str, Any]:
    """
    Reset model settings to default values.
    
    Returns:
        Default configuration dictionary
    """
    try:
        if Path(CONFIG_FILE).exists():
            os.remove(CONFIG_FILE)
    except Exception:
        pass
    
    return DEFAULT_CONFIG.copy()
