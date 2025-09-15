from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    app_name: str = "IUI2026-HelpBI API"
    version: str = "0.1.0"
    environment: str = "dev"
    log_level: str = "info"
    cors_allow_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
