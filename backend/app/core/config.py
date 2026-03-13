from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


_BASE_DIR = Path(__file__).resolve().parents[2]
_ENV_PATH = _BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_PATH), env_file_encoding="utf-8")

    app_name: str = "AI Radiology Triage & Decision Support Platform"
    environment: str = "dev"
    log_level: str = "INFO"

    # Supabase/PostgreSQL
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/medicathon"
    supabase_url: str | None = None
    supabase_key: str | None = None

    # Model settings
    hf_model_name: str = "distilbert-base-uncased"
    hf_zero_shot_model: str = "facebook/bart-large-mnli"
    hf_device: str = "cpu"  # "cpu" or "cuda"

    # Feature toggles
    enable_explainability: bool = True
    enable_inconsistency_checks: bool = True


class AppMeta(BaseModel):
    name: str
    environment: str
    version: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
