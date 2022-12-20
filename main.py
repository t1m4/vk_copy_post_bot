import asyncio
import logging
from typing import List, Tuple

import aiohttp
import aioredis
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand

from src import error_reporting
from src.config import Config, config
from src.filters.admin import AdminFilter
from src.handlers.admin import register_admin
from src.handlers.echo import register_echo
from src.middlewares.environment import Middleware
from src.redis_client.client import AsyncRedisClient
from src.vk_api_client.api_client import VKClientAPI

logger = logging.getLogger(__name__)


def register_all_middlewares(
    dp: Dispatcher, config: Config, vk_api_client: VKClientAPI, redis_client: AsyncRedisClient
):
    dp.setup_middleware(Middleware(dp, config, vk_api_client, redis_client))


def register_all_filters(dp: Dispatcher):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp: Dispatcher) -> List[BotCommand]:
    all_commands: List = []
    handlers = [register_admin, register_echo]
    for handler in handlers:
        commands = handler(dp)
        all_commands.extend(commands)
    return all_commands


async def set_my_commands(dispatcher: Dispatcher, commands: List[BotCommand]):
    await dispatcher.bot.set_my_commands(commands)


async def on_startup_notify(dp: Dispatcher):
    for admin in config.ADMIN_IDS:
        await dp.bot.send_message(admin, "Бот Запущен")


async def start_services() -> Tuple[VKClientAPI, AsyncRedisClient, Dispatcher]:
    # setup sentry
    error_reporting.init(config.SENTRY_DSN, config.ENVIRONMENT)

    # setup client api
    aiohttp_session = aiohttp.ClientSession()
    vk_api_client = VKClientAPI(aiohttp_session, config.VK_ACCESS_TOKEN, config.VK_API_VERSION)

    # setup redis api
    redis_instance = await aioredis.from_url(config.REDIS_URL, decode_responses=True)
    redis_client = AsyncRedisClient(redis_instance)

    # setup bot
    storage = MemoryStorage()
    bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
    dispatcher = Dispatcher(bot, storage=storage)
    bot["config"] = config
    return vk_api_client, redis_client, dispatcher


async def stop_services(dispatcher: Dispatcher, vk_api_client: VKClientAPI, redis_client: AsyncRedisClient):
    await vk_api_client.session.close()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    session = await dispatcher.bot.get_session()
    await session.close()  # type: ignore
    await redis_client.redis.close()


async def init_bot(dispatcher: Dispatcher, vk_api_client: VKClientAPI, redis_client: AsyncRedisClient):
    register_all_middlewares(dispatcher, config, vk_api_client, redis_client)
    register_all_filters(dispatcher)
    commands = register_all_handlers(dispatcher)
    await set_my_commands(dispatcher, commands)
    await on_startup_notify(dispatcher)


async def main():
    logging.basicConfig(
        # level=logging.ERROR,
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger.info("Starting bot")

    # set sentry
    error_reporting.init(config.SENTRY_DSN, config.ENVIRONMENT)

    vk_api_client, redis_client, dispatcher = await start_services()
    await init_bot(dispatcher, vk_api_client, redis_client)

    # start
    try:
        await dispatcher.start_polling()
    finally:
        await stop_services(dispatcher, vk_api_client, redis_client)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
