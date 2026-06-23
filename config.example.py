"""Exemplo de configuração; copie para config.py ou use um arquivo .env."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-70b-versatile")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
AI_PROVIDER = os.environ.get("AI_PROVIDER", "auto").lower()
ALLOWED_CHAT_IDS_RAW = os.environ.get("ALLOWED_CHAT_IDS", "")


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


def allowed_chat_ids() -> set[int] | None:
    values = {
        int(item.strip())
        for item in ALLOWED_CHAT_IDS_RAW.split(",")
        if item.strip().lstrip("-").isdigit()
    }
    return values or None
