"""Pydantic-settings configuration loaded from env / .env file."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "Universal Data Connector"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATA_DIR: str = str(Path(__file__).resolve().parent.parent / "data")
    MAX_RESULTS: int = 10
    DEFAULT_PAGE_SIZE: int = 10
    DEFAULT_VOICE_MODE: bool = True
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
