import os
from pathlib import Path
from dotenv import load_dotenv

# core/config.py

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with all environment variables and settings"""
    
    # API Keys
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    MONGO_URI = os.getenv("MONGO_URI")
    HF_API_KEY = os.getenv("HF_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Model Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    
    # File Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    UPLOAD_DIR = DATA_DIR / "uploads"
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", str(DATA_DIR / "vector_store"))
    LOG_PATH = os.getenv("LOG_PATH", str(BASE_DIR / "logs" / "app.log"))
    
    # Create directories if they don't exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    Path(VECTOR_STORE_PATH).mkdir(parents=True, exist_ok=True)
    Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    # Application Settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB default
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,txt,docx,csv").split(",")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    
    # Database Settings
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
    DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", 30))


class DevConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")


class ProdConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class TestConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = "DEBUG"
    VECTOR_STORE_PATH = str(Config.BASE_DIR / "data" / "test_vector_store")


# Factory function to get appropriate config
def get_config():
    """Returns configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    configs = {
        "development": DevConfig,
        "production": ProdConfig,
        "testing": TestConfig
    }
    
    return configs.get(env, DevConfig)


# Export the active configuration
config = get_config()