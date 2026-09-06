from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "SearchSignal"
    API_V1_STR: str = "/api/v1"
    
    # Engine & Rule Versioning (Spec Section 72)
    CRAWLER_VERSION: str = "4.2.0"
    RULE_PACK_VERSION: str = "2026.09"
    SCORING_VERSION: str = "2026.09.1"
    GEO_MODEL_VERSION: str = "GEO-2026.1"
    AEO_MODEL_VERSION: str = "AEO-2026.2"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./searchsignal.db"
    
    # Storage
    STORAGE_DIR: Path = Path("./evidence_storage")
    
    # Security & SSRF
    ALLOW_LOCAL_TEST_HOSTS: bool = True  # Allows local test fixtures in development
    MAX_CRAWL_URLS: int = 1000
    DEFAULT_CONCURRENCY: int = 4
    DEFAULT_REQUEST_TIMEOUT_MS: int = 10000
    MAX_REDIRECT_HOPS: int = 5
    MAX_RESPONSE_BYTES: int = 10 * 1024 * 1024  # 10MB safety cap
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # JWT / Auth
    SECRET_KEY: str = "searchsignal-production-secret-key-change-in-production-2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
