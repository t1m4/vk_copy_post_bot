from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from src.config import Config
from src.vk_api_client.api_client import VKClientAPI

from ..redis_client.client import AsyncRedisClient


class Middleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(
        self, dispatcher: Dispatcher, config: Config, api_client: VKClientAPI, redis_client: AsyncRedisClient, **kwargs
    ):
        super().__init__()
        self.dispatcher = dispatcher
        self.config = config
        self.api_client = api_client
        self.redis_client = redis_client

    async def pre_process(self, obj, data, *args):
        data.update(
            dispatcher=self.dispatcher, config=self.config, api_client=self.api_client, redis_client=self.redis_client
        )
