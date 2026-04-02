from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # OpenAI / OpenRouter Settings
    OPENAI_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Qdrant Settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "documents"

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # SQL DB Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
