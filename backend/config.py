from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    API_TITLE: str = "Task Manager Agent API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # LLM Configuration
    GOOGLE_GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b"
    LLM_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b"
    LLM_TEMPERATURE: float = 0.7
    LLM_PROVIDER: str = "nvidia"  # Primary provider: nvidia, gemini, openai, anthropic
    
    # Database Configuration
    SUPABASE_URL: str = ""
    SUPABASE_API_KEY: str = ""
    SUPABASE_DB_NAME: str = "task_manager"
    
    # ChromaDB Configuration
    CHROMADB_PERSIST_DIR: str = "./chroma_data"
    CHROMADB_COLLECTION_NAME: str = "task_embeddings"
    
    # External APIs
    GOOGLE_CALENDAR_API_KEY: str = ""
    NOTION_API_KEY: str = ""
    
    # Scheduler Configuration
    SCHEDULER_ENABLED: bool = True
    REMINDER_CHECK_INTERVAL_MINUTES: int = 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Frontend Configuration (optional, used by frontend)
    API_URL: str = "http://localhost:8000/api/v1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()