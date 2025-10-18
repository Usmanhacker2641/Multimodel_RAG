from fastapi import APIRouter, Form, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from services.model_config import update_model_settings, get_model_settings
from core.logger import setup_logger

# Import model config service (you'll need to create this)
try:
    from services.model_config import update_model_settings, get_model_settings
except ImportError:
    # Fallback if service doesn't exist yet
    def update_model_settings(*args, **kwargs):
        raise HTTPException(status_code=500, detail="Model config service not implemented")
    
    def get_model_settings():
        raise HTTPException(status_code=500, detail="Model config service not implemented")

logger = setup_logger("backend.model")
router = APIRouter(prefix="/model", tags=["Model Config"])


# Pydantic models for validation
class ModelConfig(BaseModel):
    temperature: float = Field(ge=0.0, le=2.0, description="Controls randomness (0-2)")
    top_p: float = Field(ge=0.0, le=1.0, description="Nucleus sampling threshold")
    max_tokens: int = Field(ge=1, le=32000, description="Maximum response length")
    freq_penalty: float = Field(ge=-2.0, le=2.0, description="Frequency penalty")
    pres_penalty: float = Field(ge=-2.0, le=2.0, description="Presence penalty")
    chunk_size: int = Field(ge=100, le=5000, description="RAG chunk size")


@router.post("/update")
async def update_config(
    temperature: float = Form(default=0.7, ge=0.0, le=2.0),
    top_p: float = Form(default=0.9, ge=0.0, le=1.0),
    max_tokens: int = Form(default=2000, ge=1, le=32000),
    freq_penalty: float = Form(default=0.0, ge=-2.0, le=2.0),
    pres_penalty: float = Form(default=0.0, ge=-2.0, le=2.0),
    chunk_size: int = Form(default=1000, ge=100, le=5000),
):
    """
    Update AI model configuration parameters.
    
    - **temperature**: Controls randomness (0.0 = deterministic, 2.0 = very random)
    - **top_p**: Nucleus sampling threshold
    - **max_tokens**: Maximum length of generated response
    - **freq_penalty**: Reduces repetition of frequent tokens
    - **pres_penalty**: Reduces repetition of any tokens
    - **chunk_size**: Size of text chunks for RAG processing
    """
    try:
        logger.info("Updating model config: temp=%.2f top_p=%.2f max_tokens=%d", temperature, top_p, max_tokens)
        update_model_settings(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            freq_penalty=freq_penalty,
            pres_penalty=pres_penalty,
            chunk_size=chunk_size
        )
        logger.info("Model configuration updated successfully")
        return {
            "status": "success",
            "message": "Model configuration updated successfully",
            "config": {
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
                "freq_penalty": freq_penalty,
                "pres_penalty": pres_penalty,
                "chunk_size": chunk_size
            }
        }
    except Exception as e:
        logger.exception("Failed to update model config: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")


@router.get("/get")
async def get_config():
    """
    Retrieve current AI model configuration parameters.
    """
    try:
        logger.info("Retrieving model configuration")
        config = get_model_settings()
        logger.info("Model configuration retrieved successfully")
        return {
            "status": "success",
            "config": config
        }
    except Exception as e:
        logger.exception("Failed to retrieve model config: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve config: {str(e)}")


@router.get("/defaults")
async def get_defaults():
    """
    Get default recommended settings for model configuration.
    """
    return {
        "status": "success",
        "defaults": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 2000,
            "freq_penalty": 0.0,
            "pres_penalty": 0.0,
            "chunk_size": 1000
        },
        "descriptions": {
            "temperature": "Controls randomness (0.0-2.0). Lower = more focused, Higher = more creative",
            "top_p": "Nucleus sampling (0.0-1.0). Controls diversity of output",
            "max_tokens": "Maximum response length (1-32000)",
            "freq_penalty": "Reduces repetition (-2.0 to 2.0)",
            "pres_penalty": "Encourages new topics (-2.0 to 2.0)",
            "chunk_size": "Text chunk size for RAG (100-5000)"
        }
    }


@router.post("/reset")
async def reset_config():
    """
    Reset model configuration to default values.
    """
    try:
        update_model_settings(
            temperature=0.7,
            top_p=0.9,
            max_tokens=2000,
            freq_penalty=0.0,
            pres_penalty=0.0,
            chunk_size=1000
        )
        return {
            "status": "success",
            "message": "Configuration reset to defaults"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset config: {str(e)}")