"""
Configuration loading and validation.
Uses pydantic-settings for type-safe config from .env files.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Application-level settings.
    Values are loaded from .env (or environment variables) at runtime.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = Field(default="AI Excel Analytics Platform")
    app_version: str = Field(default="2.0.0")
    debug: bool = Field(default=False)
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    cors_origins: list[str] = Field(default=["http://localhost:5173"])

    # ---- AI / LLM ----
    ollama_url: str = Field(default="http://localhost:11434")
    llm_model: str = Field(default="qwen2.5:7b")
    embedding_model: str = Field(default="nomic-embed-text")
    llm_temperature: float = Field(default=0.1)
    llm_max_tokens: int = Field(default=4096)

    # ---- Data paths ----
    upload_path: str = Field(default="data/uploads")
    parquet_path: str = Field(default="data/parquet")
    duckdb_path: str = Field(default="data/databases/analytics.db")
    faiss_path: str = Field(default="data/indexes")
    report_path: str = Field(default="data/reports")
    chart_path: str = Field(default="data/charts")
    temp_path: str = Field(default="data/temp")

    # ---- Limits ----
    max_file_size_mb: int = Field(default=500)
    max_sheets: int = Field(default=100)
    max_rows_per_sheet: int = Field(default=2_000_000)
    session_ttl_minutes: int = Field(default=120)

    # ---- Logging ----
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    """Returns a cached Settings singleton."""
    return Settings()


settings = get_settings()