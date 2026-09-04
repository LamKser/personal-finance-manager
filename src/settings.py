from os import getenv
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=getenv("ENV", ".env"), env_file_encoding="utf-8")

    # Log
    log_file: str
    log_level: str

    # Telegram
    telegram_token: str

    # Agent
    llm_provider: str
    api_key: str
    llm_model: str
    llm_reasoning: bool
    max_tool_retry: int

    # Router
    router_type: str
    router_provider: str
    router_model: str
    router_reasoning: bool
    top_tool: int
    tool_threshold: float
    tool_kb: str

    # Embedding
    embedding_provider: str
    embedding_model: str
    dimension: int | str | None = None

    # GG sheet
    credential: str
    sheet_key: str

settings = Settings()