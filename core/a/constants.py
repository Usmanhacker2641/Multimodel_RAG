from enum import Enum
from typing import Final

# core/constants.py
"""
Constants module for Multimodel RAG system.
Holds default system settings for consistency and easy global configuration.
"""


# =============================================================================
# DEFAULT GENERATION PARAMETERS
# =============================================================================

DEFAULT_TEMPERATURE: Final[float] = 0.7
DEFAULT_TOP_P: Final[float] = 0.9
DEFAULT_TOP_K: Final[int] = 50
DEFAULT_MAX_TOKENS: Final[int] = 512
DEFAULT_FREQUENCY_PENALTY: Final[float] = 0.0
DEFAULT_PRESENCE_PENALTY: Final[float] = 0.0

# =============================================================================
# PARAMETER BOUNDS
# =============================================================================

MIN_TEMPERATURE: Final[float] = 0.0
MAX_TEMPERATURE: Final[float] = 1.0

MIN_TOP_P: Final[float] = 0.0
MAX_TOP_P: Final[float] = 1.0

MIN_FREQUENCY_PENALTY: Final[float] = -2.0
MAX_FREQUENCY_PENALTY: Final[float] = 2.0

MIN_PRESENCE_PENALTY: Final[float] = -2.0
MAX_PRESENCE_PENALTY: Final[float] = 2.0

# =============================================================================
# CHUNKING PARAMETERS
# =============================================================================

DEFAULT_CHUNK_SIZE: Final[int] = 500
DEFAULT_OVERLAP: Final[int] = 100
MIN_CHUNK_SIZE: Final[int] = 100
MAX_CHUNK_SIZE: Final[int] = 2000

# =============================================================================
# EMBEDDING PARAMETERS
# =============================================================================

DEFAULT_EMBEDDING_MODEL: Final[str] = "text-embedding-ada-002"
DEFAULT_EMBEDDING_DIMENSION: Final[int] = 1536

# =============================================================================
# RETRIEVAL PARAMETERS
# =============================================================================

DEFAULT_TOP_K_RESULTS: Final[int] = 5
DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.7
DEFAULT_CATEGORY_THRESHOLD: Final[float] = 0.6

# =============================================================================
# LLM MODES
# =============================================================================

class LLMMode(Enum):
    """Enumeration of LLM operation modes."""
    RAG = "retrieval_augmented_generation"
    MULTI = "multi_model_parallel"
    HYBRID = "hybrid_mode"


class ModelType(Enum):
    """Enumeration of supported model types."""
    GPT_3_5 = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    CLAUDE = "claude-3-opus"
    GEMINI = "gemini-pro"


# =============================================================================
# TIMEOUT AND RETRY SETTINGS
# =============================================================================

DEFAULT_REQUEST_TIMEOUT: Final[int] = 30  # seconds
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_RETRY_DELAY: Final[float] = 1.0  # seconds

# =============================================================================
# CACHE SETTINGS
# =============================================================================

DEFAULT_CACHE_TTL: Final[int] = 3600  # seconds (1 hour)
DEFAULT_MAX_CACHE_SIZE: Final[int] = 1000  # entries

# =============================================================================
# LOGGING SETTINGS
# =============================================================================

DEFAULT_LOG_LEVEL: Final[str] = "INFO"
DEFAULT_LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# =============================================================================
# FILE AND PATH SETTINGS
# =============================================================================

DEFAULT_DATA_DIR: Final[str] = "data"
DEFAULT_CACHE_DIR: Final[str] = "cache"
DEFAULT_LOGS_DIR: Final[str] = "logs"
DEFAULT_MODELS_DIR: Final[str] = "models"

# =============================================================================
# SUPPORTED FILE TYPES
# =============================================================================

SUPPORTED_DOCUMENT_TYPES: Final[tuple] = (
    ".txt", ".pdf", ".docx", ".md", ".html", ".json", ".csv"
)

# =============================================================================
# API RATE LIMITS
# =============================================================================

DEFAULT_RATE_LIMIT_PER_MINUTE: Final[int] = 60
DEFAULT_RATE_LIMIT_PER_HOUR: Final[int] = 3000

# =============================================================================
# VALIDATION MESSAGES
# =============================================================================

VALIDATION_ERRORS = {
    "temperature": f"Temperature must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE}",
    "top_p": f"Top-p must be between {MIN_TOP_P} and {MAX_TOP_P}",
    "chunk_size": f"Chunk size must be between {MIN_CHUNK_SIZE} and {MAX_CHUNK_SIZE}",
    "empty_input": "Input cannot be empty",
    "invalid_mode": "Invalid LLM mode specified",
}