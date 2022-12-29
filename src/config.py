from typing import List

import aioredis
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pydantic import BaseSettings, Field

from src.redis_client.client import AsyncRedisClient


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
redis_instance = aioredis.Redis(
    host=config.REDIS_HOST, port=config.REDIS_PORT, password=config.REDIS_PASSWORD, decode_responses=True
)
redis_client = AsyncRedisClient(redis_instance)
storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dispatcher = Dispatcher(bot, storage=storage)
