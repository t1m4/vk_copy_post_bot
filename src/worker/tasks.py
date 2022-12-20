import asyncio
import dataclasses
import logging

from aiogram import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError

from main import start_services, stop_services
from src import error_reporting
from src.config import config
from src.vk_api_client.models import Post
from src.vk_api_client.services import get_user_last_post
from src.worker.celery import celery_app as app

logger = logging.getLogger(__name__)


async def send_new_post(dispatcher: Dispatcher, channel_id: int, user_post: Post):
    """Push post to telegram channel"""
    is_photo = True if user_post.attachments else False
    is_text = True if user_post.text else False
    if not (is_text or is_photo):
        logger.error("There is no text/photo")
        return
    elif is_text and not is_photo:
        await dispatcher.bot.send_message(channel_id, user_post.text)
    else:
        try:
            await dispatcher.bot.send_photo(channel_id, user_post.attachments[0].url, caption=user_post.text)
        except TelegramAPIError as error:
            logger.error(error)
            if "Message caption is too long" in str(error):
                await dispatcher.bot.send_photo(channel_id, user_post.attachments[0].url)
                await dispatcher.bot.send_message(channel_id, user_post.text)


async def create_new_post():
    """Get new post from VK API and compare with existing one. Push to telegram channel"""
    vk_api_client, redis_client, dispatcher = await start_services()

    user_ids = await redis_client.get_all_user_ids()
    for redis_user_id in user_ids:
        vk_user_id = redis_user_id.split("_")[-1]
        saved_user_post = await redis_client.get_key(redis_user_id)
        post = Post(**saved_user_post["post"])
        new_user_post = await get_user_last_post(vk_api_client, vk_user_id)
        if not new_user_post:
            return
        if new_user_post.id != post.id:
            post_as_dict = dataclasses.asdict(new_user_post)
            result = {"post": post_as_dict, "channel_id": saved_user_post["channel_id"]}
            await redis_client.set_mapping(vk_user_id, result)
            await send_new_post(dispatcher, saved_user_post["channel_id"], new_user_post)

    await stop_services(dispatcher, vk_api_client, redis_client)


@app.task
def test_task(name: str = "World") -> None:
    error_reporting.init(config.SENTRY_DSN, config.ENVIRONMENT)
    asyncio.run(create_new_post())
