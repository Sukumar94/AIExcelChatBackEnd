from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Application Settings
    Loaded from .env
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------
    # Application
    # -------------------------------------------------
    app_name: str = Field(default="AI Excel Analytics Platform")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)

    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # -------------------------------------------------
    # AI
    # -------------------------------------------------
    ollama_url: str = Field(default="http://localhost:11434")
    llm_model: str = Field(default="qwen2.5:1.5b")  # Changed from qwen2.5:7b
    embedding_model: str = Field(default="nomic-embed-text")

    # -------------------------------------------------
    # Storage
    # -------------------------------------------------
    upload_path: str = Field(default="data/uploads")
    parquet_path: str = Field(default="data/parquet")
    duckdb_path: str = Field(default="data/databases/analytics.db")
    faiss_path: str = Field(default="data/indexes")
    report_path: str = Field(default="data/reports")
    chart_path: str = Field(default="data/charts")
    temp_path: str = Field(default="data/temp")

    # -------------------------------------------------
    # CORS
    # -------------------------------------------------
    cors_origins: list[str] = Field(default=["*"])

    # -------------------------------------------------
    # Session Management
    # -------------------------------------------------
    session_ttl_minutes: int = Field(default=1440)  # 24 hours

    # -------------------------------------------------
    # Logging
    # -------------------------------------------------
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()