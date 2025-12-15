# app/prompts.py

from pathlib import Path
from typing import Optional

from app.config import PROMPTS_DIR

DEFAULT_SYSTEM_PROMPT_FALLBACK = (
    "Ты AI-ассистент студии AINOVA. Отвечай по делу, простым языком."
)

DEFAULT_DEVELOPER_PROMPT_FALLBACK = (
    "Отвечай структурно и кратко. Если не хватает данных — уточняй."
)


def _read_text(path: Path) -> Optional[str]:
    try:
        if path.exists() and path.is_file():
            text = path.read_text(encoding="utf-8").strip()
            return text or None
    except Exception:
        return None
    return None


def load_system_prompt() -> str:
    path = Path(PROMPTS_DIR) / "system.txt"
    return _read_text(path) or DEFAULT_SYSTEM_PROMPT_FALLBACK


def load_developer_prompt() -> str:
    path = Path(PROMPTS_DIR) / "developer.txt"
    return _read_text(path) or DEFAULT_DEVELOPER_PROMPT_FALLBACK
