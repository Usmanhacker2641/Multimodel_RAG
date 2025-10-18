import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Generate log filename with timestamp
LOG_FILENAME = f"rag_app_{datetime.now().strftime('%Y%m%d')}.log"
LOG_PATH = LOG_DIR / LOG_FILENAME

# Define log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Create formatter
formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)

# Create file handler
file_handler = logging.FileHandler(LOG_PATH, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# Create and configure logger
logger = logging.getLogger("RAGAppLogger")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent propagation to root logger
logger.propagate = False

# Log startup message
logger.info("=" * 80)
logger.info("RAG Application Logger Initialized")
logger.info(f"Log file location: {LOG_PATH}")
logger.info("=" * 80)


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a child logger for specific modules.
    
    Args:
        name: Name of the module/component requesting the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    if name:
        return logger.getChild(name)
    return logger


# Example usage functions
def log_api_request(endpoint: str, method: str, user_id: str = None):
    """Log API request details"""
    logger.info(f"API Request - Endpoint: {endpoint}, Method: {method}, User: {user_id}")


def log_file_upload(filename: str, size: int, status: str):
    """Log file upload events"""
    logger.info(f"File Upload - Name: {filename}, Size: {size} bytes, Status: {status}")


def log_embedding_generation(doc_count: int, duration: float):
    """Log embedding generation metrics"""
    logger.info(f"Embedding Generation - Documents: {doc_count}, Duration: {duration:.2f}s")


def log_llm_response(query: str, response_time: float, tokens: int = None):
    """Log LLM query and response metrics"""
    logger.info(f"LLM Response - Query: '{query[:50]}...', Time: {response_time:.2f}s, Tokens: {tokens}")


def log_error(error_type: str, error_message: str, traceback: str = None):
    """Log errors with optional traceback"""
    logger.error(f"Error - Type: {error_type}, Message: {error_message}")
    if traceback:
        logger.error(f"Traceback: {traceback}")


# Export main logger and utility functions
__all__ = [
    'logger',
    'get_logger',
    'log_api_request',
    'log_file_upload',
    'log_embedding_generation',
    'log_llm_response',
    'log_error'
]