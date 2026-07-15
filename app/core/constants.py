"""
Application-wide constants.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# File system paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

UPLOAD_DIR = DATA_DIR / "uploads"
PARQUET_DIR = DATA_DIR / "parquet"
DUCKDB_DIR = DATA_DIR / "databases"
FAISS_DIR = DATA_DIR / "indexes"
REPORT_DIR = DATA_DIR / "reports"
CHART_DIR = DATA_DIR / "charts"
TEMP_DIR = DATA_DIR / "temp"

# Ensure all directories exist
for d in [UPLOAD_DIR, PARQUET_DIR, DUCKDB_DIR, FAISS_DIR, REPORT_DIR, CHART_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Upload limits
# ---------------------------------------------------------------------------
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".xlsm", ".csv"}

# ---------------------------------------------------------------------------
# LLM / AI
# ---------------------------------------------------------------------------
DEFAULT_LLM_MODEL = "qwen2.5:7b"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MAX_TOKENS = 4096
TEMPERATURE = 0.1

# ---------------------------------------------------------------------------
# Vector search
# ---------------------------------------------------------------------------
FAISS_INDEX_DIMENSION = 768  # nomic-embed-text produces 768-dim vectors
FAISS_INDEX_TYPE = "Flat"     # Exact search (L2)

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
CHART_THEME = "plotly_white"
DEFAULT_CHART_WIDTH = 800
DEFAULT_CHART_HEIGHT = 500

# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------
SESSION_TTL_SECONDS = 3600 * 2  # 2 hours
MAX_SHEETS_PER_WORKBOOK = 100
MAX_ROWS_PER_SHEET = 2_000_000

# ---------------------------------------------------------------------------
# DuckDB
# ---------------------------------------------------------------------------
DUCKDB_DEFAULT_PATH = str(DUCKDB_DIR / "analytics.db")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
DEFAULT_LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"