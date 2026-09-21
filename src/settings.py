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

    llm_provider: str
    # ollama
    ollama_model: str
    ollama_reasoning: bool

    # vllm
    vllm_url: str
    vllm_api_key: str
    vllm_model: str

    # nvidia
    nvidia_api_key: str
    nvidia_model: str

    max_tool_retry: int

    # Router
    router_type: str
    router_provider: str
    router_model: str
    router_reasoning: bool
    top_tool: int
    tool_threshold: float
    tool_kb: str
    update_kb: bool

    # Embedding
    embedding_provider: str
    embedding_model: str
    dimension: int | str | None = None

    # GG sheet
    credential: str
    sheet_key: str

    # Langfuse
    tracing: bool
    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_base_url: str

settings = Settings()