from typing import List

from pydantic import BaseSettings, Field, RedisDsn


class Config(BaseSettings):
    BOT_TOKEN: str = Field(...)
    ADMIN_IDS: List = Field(...)
    ENVIRONMENT: str = Field(...)
    REDIS_URL: RedisDsn = Field(...)
    VK_ACCESS_TOKEN: str = Field(...)
    VK_API_VERSION: str = Field(...)
    SENTRY_DSN: str | None = Field(None)


config = Config(_env_file=".env", _env_file_encoding="utf-8")  # type: ignore
