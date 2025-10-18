import requests
import streamlit as st
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path
import json

"""
API Client for Multimodal RAG Frontend
--------------------------------------
Central communication hub between Streamlit UI and FastAPI backend.
Handles all HTTP requests, error management, and response formatting.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds


# ============================================================================
# Helper Functions
# ============================================================================

def _make_request(
    method: str,
    endpoint: str,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Internal helper to make HTTP requests with consistent error handling.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        headers: Request headers
        data: JSON payload
        files: File upload payload
        params: URL parameters
    
    Returns:
        Response JSON or error dictionary
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            files=files,
            params=params,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        logger.error(f"Request timeout: {endpoint}")
        return {"error": "⏱️ Request timed out. Please try again."}
    
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection failed: {endpoint}")
        return {"error": "🔌 Cannot connect to backend. Please ensure the server is running."}
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code}: {endpoint}")
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        return {"error": f"❌ Server error: {error_detail}"}
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": f"⚠️ Unexpected error: {str(e)}"}


def _get_auth_headers(api_key: str) -> Dict[str, str]:
    """Generate authorization headers with API key."""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


# ============================================================================
# Upload APIs
# ============================================================================

def upload_text(
    text: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Upload text content to the backend."""
    logger.info("Uploading text content")
    data = {"text": text}
    if metadata:
        for key, value in metadata.items():
            data[key] = value
    
    return _make_request(
        method="POST",
        endpoint="/api/upload/",
        data=data
    )


def upload_url(url: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch and upload content from a URL."""
    logger.info(f"Uploading URL: {url}")
    data = {"url": url}
    if metadata:
        for key, value in metadata.items():
            data[key] = value
    
    return _make_request(
        method="POST",
        endpoint="/api/upload/",
        data=data
    )


def upload_file_bytes(
    file_bytes: bytes,
    filename: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Upload a file to the backend."""
    logger.info(f"Uploading file: {filename}")
    files = {"file": (filename, file_bytes)}
    data = metadata or {}
    
    return _make_request(
        method="POST",
        endpoint="/api/upload/",
        files=files,
        data=data
    )


# ============================================================================
# Query & RAG APIs
# ============================================================================

def query_rag(
    question: str,
    mode: str = "rag",
    top_k: int = 5,
    api_keys: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Submit a query to the RAG pipeline."""
    logger.info(f"Submitting query: {question[:50]}...")
    
    # Prepare form data for FastAPI Form parameters
    data = {
        "question": question,
        "mode": mode,
        "top_k": str(top_k)
    }
    
    # Add API keys if provided
    if api_keys:
        if api_keys.get("hf_api_key"):
            data["hf_api_key"] = api_keys["hf_api_key"]
        if api_keys.get("deepseek_api_key"):
            data["deepseek_api_key"] = api_keys["deepseek_api_key"]
        if api_keys.get("gemini_api_key"):
            data["gemini_api_key"] = api_keys["gemini_api_key"]
    
    # Use requests directly to send form data
    try:
        response = requests.post(
            f"{BASE_URL}/query/",
            data=data,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Query request timeout")
        return {"status": "error", "message": "Request timed out"}
    except requests.exceptions.ConnectionError:
        logger.error("Connection failed")
        return {"status": "error", "message": "Cannot connect to backend"}
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e.response.status_code}")
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        return {"status": "error", "message": f"Server error: {error_detail}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# History APIs
# ============================================================================

def get_history(session_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch chat history from the backend."""
    logger.info("Fetching chat history")
    
    params = {"limit": limit}
    if session_id:
        params["session_id"] = session_id
    
    result = _make_request(
        method="GET",
        endpoint="/api/history/",
        params=params
    )
    
    if isinstance(result, list):
        return result
    return result.get("history", [])


# ============================================================================
# Feedback APIs
# ============================================================================

def submit_feedback(
    message_id: str,
    feedback_type: str,
    comment: Optional[str] = None
) -> Dict[str, Any]:
    """Submit user feedback for a response."""
    logger.info(f"Submitting {feedback_type} feedback")
    
    data = {
        "message_id": message_id,
        "feedback_type": feedback_type
    }
    if comment:
        data["comment"] = comment
    
    return _make_request(
        method="POST",
        endpoint="/api/feedback/",
        data=data
    )


# ============================================================================
# Model APIs
# ============================================================================

def get_models() -> List[Dict[str, str]]:
    """Get list of available LLM models."""
    logger.info("Fetching available models")
    
    result = _make_request(
        method="GET",
        endpoint="/api/models/"
    )
    
    if isinstance(result, list):
        return result
    return result.get("models", [])


# ============================================================================
# Health Check
# ============================================================================

def health_check() -> Dict[str, Any]:
    """
    Check if backend server is healthy and responsive.
    
    Returns:
        Health status dictionary
    """
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.json()
    except:
        return {"status": "unhealthy", "error": "Cannot reach backend"}


# ============================================================================
# Streamlit UI Helpers
# ============================================================================

def display_error(error_response: Dict[str, Any]) -> None:
    """Display error message in Streamlit UI."""
    if "error" in error_response:
        st.error(error_response["error"])
        logger.error(f"UI Error: {error_response['error']}")


def display_success(message: str) -> None:
    """Display success message in Streamlit UI."""
    st.success(f"✅ {message}")
    logger.info(f"Success: {message}")


def show_loading(message: str = "Processing..."):
    """Context manager for showing loading spinner."""
    return st.spinner(message)