"""Configuração do bot carregada exclusivamente por variáveis de ambiente."""

from __future__ import annotations

import os
from pathlib import Path


def _load_env() -> None:
    env_paths = (
        Path(__file__).resolve().parent / ".env",
        Path.home() / ".config" / "estudos-bot" / ".env",
    )
    for env_path in env_paths:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and key not in os.environ:
                os.environ[key] = value


_load_env()


def _get(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _get_int(name: str, default: int, minimum: int = 1) -> int:
    try:
        value = int(_get(name, str(default)))
    except ValueError:
        return default
    return max(minimum, value)


TELEGRAM_TOKEN = _get("TELEGRAM_TOKEN")
GROQ_API_KEY = _get("GROQ_API_KEY")
GROQ_MODEL = _get("GROQ_MODEL", "llama-3.1-70b-versatile")
GEMINI_API_KEY = _get("GEMINI_API_KEY")
GEMINI_MODEL = _get("GEMINI_MODEL", "gemini-3.5-flash")
GEMINI_FALLBACK_MODEL = _get("GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")
AI_PROVIDER = _get("AI_PROVIDER", "auto").lower()
ALLOWED_CHAT_IDS_RAW = _get("ALLOWED_CHAT_IDS")
MAX_PDF_MB = _get_int("MAX_PDF_MB", 20)
MAX_DOCUMENT_CHARS = _get_int("MAX_DOCUMENT_CHARS", 60000, minimum=12000)
MAX_HISTORY_MESSAGES = _get_int("MAX_HISTORY_MESSAGES", 20, minimum=2)


def active_ai_provider() -> str:
    if AI_PROVIDER == "gemini":
        return "gemini" if GEMINI_API_KEY else "indisponivel"
    if AI_PROVIDER == "groq":
        return "groq" if GROQ_API_KEY else "indisponivel"
    if GEMINI_API_KEY:
        return "gemini"
    if GROQ_API_KEY:
        return "groq"
    return "indisponivel"


def fallback_ai_provider(primary: str) -> str | None:
    if primary == "gemini" and GROQ_API_KEY:
        return "groq"
    if primary == "groq" and GEMINI_API_KEY:
        return "gemini"
    return None


def allowed_chat_ids() -> set[int] | None:
    values = {
        int(item.strip())
        for item in ALLOWED_CHAT_IDS_RAW.split(",")
        if item.strip().lstrip("-").isdigit()
    }
    return values or None
