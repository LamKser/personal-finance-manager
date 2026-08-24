from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Log
    log_file: str
    log_level: str

    # Telegram
    telegram_token: str

    # Agent
    provider: str
    api_key: str
    model: str
    reasoning: str
    max_tool_retry: int

    # GG sheet
    credential: str
    sheet_key: str

settings = Settings()