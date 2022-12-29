import asyncio
import logging
from typing import List

from aiogram.types import BotCommand

from src import error_reporting
from src.config import config, dispatcher, redis_client
from src.filters.admin import AdminFilter
from src.handlers.admin import register_admin
from src.handlers.echo import register_echo
from src.vk_api_client.services import vk_service


def register_all_filters():
    dispatcher.filters_factory.bind(AdminFilter)


def register_all_handlers() -> List[BotCommand]:
    all_commands: List = []
    handlers = [register_admin, register_echo]
    for handler in handlers:
        commands = handler(dispatcher)
        all_commands.extend(commands)
    return all_commands


async def set_my_commands(commands: List[BotCommand]):
    await dispatcher.bot.set_my_commands(commands)


async def on_startup_notify():
    for admin in config.ADMIN_IDS:
        await dispatcher.bot.send_message(admin, "Бот Запущен")


async def start_services():
    await vk_service.start()


async def stop_services():
    await vk_service.stop()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    session = await dispatcher.bot.get_session()
    await session.close()  # type: ignore
    await redis_client.redis.close()


async def init_bot():
    register_all_filters()
    commands = register_all_handlers()
    await set_my_commands(commands)
    await on_startup_notify()


async def main():
    logging.basicConfig(
        level=logging.ERROR,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logging.info("Starting bot")

    # setup
    error_reporting.init(config.SENTRY_DSN, config.ENVIRONMENT)
    await start_services()
    await init_bot()

    # start bot
    try:
        await dispatcher.start_polling()
    finally:
        await stop_services()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Bot stopped!")
