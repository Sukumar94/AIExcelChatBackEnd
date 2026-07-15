"""FastAPI dependency injection with service caching.

Services are cached (singleton pattern) to avoid repeated instantiation
and connection setup overhead. This improves performance and resource usage.
"""

from __future__ import annotations

from functools import lru_cache

from app.database.connection import DatabaseManager
from app.database.metadata_store import MetadataStore
from app.database.schema_manager import SchemaManager
from app.services.analytics_service import AnalyticsService
from app.services.chart_service import ChartService
from app.services.chat_service import ChatService
from app.services.dashboard_service import DashboardService
from app.services.report_service import ReportService
from app.services.session_service import SessionService
from app.services.upload_service import UploadService
from app.services.voice_service import VoiceService


@lru_cache(maxsize=1)
def get_upload_service() -> UploadService:
    """Get or create singleton UploadService instance."""
    return UploadService()


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    """Get or create singleton ChatService instance."""
    return ChatService()


@lru_cache(maxsize=1)
def get_chart_service() -> ChartService:
    """Get or create singleton ChartService instance."""
    return ChartService()


@lru_cache(maxsize=1)
def get_analytics_service() -> AnalyticsService:
    """Get or create singleton AnalyticsService instance."""
    return AnalyticsService()


@lru_cache(maxsize=1)
def get_dashboard_service() -> DashboardService:
    """Get or create singleton DashboardService instance."""
    return DashboardService()


@lru_cache(maxsize=1)
def get_report_service() -> ReportService:
    """Get or create singleton ReportService instance."""
    return ReportService()


@lru_cache(maxsize=1)
def get_voice_service() -> VoiceService:
    """Get or create singleton VoiceService instance."""
    return VoiceService()


@lru_cache(maxsize=1)
def get_schema_manager() -> SchemaManager:
    """Get or create singleton SchemaManager instance."""
    return SchemaManager()


@lru_cache(maxsize=1)
def get_metadata_store() -> MetadataStore:
    """Get or create singleton MetadataStore instance."""
    return MetadataStore()