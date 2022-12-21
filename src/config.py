from typing import List

from pydantic import BaseSettings, Field, RedisDsn


class Config(BaseSettings):
    BOT_TOKEN: str = Field(...)
    ADMIN_IDS: List = Field(...)
    ENVIRONMENT: str = Field(...)
    REDIS_HOST: str = Field(...)
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = Field(...)
    VK_ACCESS_TOKEN: str = Field(...)
    VK_API_VERSION: str = Field(...)
    SENTRY_DSN: str | None = Field(None)

    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

config = Config(_env_file=".env", _env_file_encoding="utf-8")  # type: ignore
