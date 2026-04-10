from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config" / "default.yaml"


class Settings(BaseSettings):
    app_env: str = Field(default="dev", alias="APP_ENV")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    model_name: str = Field(default="gpt-4o-mini", alias="MODEL_NAME")
    api_timeout_seconds: int = Field(default=30, alias="API_TIMEOUT_SECONDS")
    use_mock_data: bool = Field(default=True, alias="USE_MOCK_DATA")
    coingecko_base_url: str = Field(default="https://api.coingecko.com/api/v3", alias="COINGECKO_BASE_URL")
    defillama_base_url: str = Field(default="https://api.llama.fi", alias="DEFILLAMA_BASE_URL")
    rag_backend: str = Field(default="simple", alias="RAG_BACKEND")
    rag_top_k: int = Field(default=3, alias="RAG_TOP_K")
    rag_persist_directory: str = Field(default=".chroma", alias="RAG_PERSIST_DIRECTORY")
    rag_collection_name: str = Field(default="defi_research_docs", alias="RAG_COLLECTION_NAME")

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        extra="ignore",
        protected_namespaces=("settings_",),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_yaml_config() -> dict[str, Any]:
    fallback = {
        "app": {"name": "DeFi Research Agent", "version": "0.1.0", "env": "dev"},
        "llm": {"model": "gpt-4o-mini", "temperature": 0.2},
        "rag": {
            "top_k": 3,
            "max_context_chars": 2000,
            "backend": "simple",
            "collection_name": "defi_research_docs",
            "persist_directory": ".chroma",
        },
        "tools": {
            "use_mock_data": True,
            "coingecko_base_url": "https://api.coingecko.com/api/v3",
            "defillama_base_url": "https://api.llama.fi",
        },
    }

    if not CONFIG_PATH.exists():
        return fallback

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f) or {}

    merged = fallback.copy()
    for key, value in loaded.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value

    return merged
