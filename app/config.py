# app/config.py

import os
from pathlib import Path

from dotenv import load_dotenv

# Подхватываем .env из корня проекта (где запускается uvicorn)
load_dotenv()

# --- API keys / providers ---
PROXYAPI_API_KEY = os.getenv("PROXYAPI_API_KEY", "").strip()
PROXYAPI_BASE_URL = os.getenv("PROXYAPI_BASE_URL", "https://openai.api.proxyapi.ru/v1").strip()

# --- LLM settings ---
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini").strip()
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# --- Memory / history ---
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "12"))

# --- RAG settings ---
ENABLE_RAG = os.getenv("ENABLE_RAG", "true").lower() in ("1", "true", "yes", "y")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "2"))
RAG_MAX_CHARS = int(os.getenv("RAG_MAX_CHARS", "4000"))  # ограничение на размер контекста

# --- Paths ---
# Структура: data/prompts/*.txt
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path(__file__).resolve().parents[1]))
DATA_DIR = Path(os.getenv("DATA_DIR", str(PROJECT_ROOT / "data")))
PROMPTS_DIR = Path(os.getenv("PROMPTS_DIR", str(DATA_DIR / "prompts")))

# --- Database ---
DEFAULT_DB_PATH = PROJECT_ROOT / "ainova_assistant.db"
DB_URL = os.getenv("DB_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")
