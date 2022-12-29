import dataclasses
import logging

from aiogram.utils.exceptions import TelegramAPIError

from src.config import dispatcher, redis_client
from src.vk_api_client.models import Post
from src.vk_api_client.services import vk_service
from src.worker.celery import celery_app as app
from src.worker.celery import celery_event_loop


async def send_new_post(channel_id: int, user_post: Post):
    """Push post to telegram channel"""
    is_photo = True if user_post.attachments else False
    is_text = True if user_post.text else False
    if not (is_text or is_photo):
        logging.error("There is no text/photo")
        return
    elif is_text and not is_photo:
        await dispatcher.bot.send_message(channel_id, user_post.text)
    else:
        try:
            await dispatcher.bot.send_photo(channel_id, user_post.attachments[0].url, caption=user_post.text)
        except TelegramAPIError as error:
            logging.error(error)
            if "Message caption is too long" in str(error):
                await dispatcher.bot.send_photo(channel_id, user_post.attachments[0].url)
                await dispatcher.bot.send_message(channel_id, user_post.text)


async def create_new_post():
    """Get new post from VK API and compare with existing one. Push to telegram channel"""
    user_ids = await redis_client.get_all_user_ids()
    for redis_user_id in user_ids:
        vk_user_id = redis_user_id.split("_")[-1]
        saved_user_post = await redis_client.get_key(redis_user_id)
        post = Post(**saved_user_post["post"])
        new_user_post = await vk_service.get_user_last_post(vk_user_id)
        if not new_user_post:
            continue
        if new_user_post.id != post.id:
            post_as_dict = dataclasses.asdict(new_user_post)
            result = {"post": post_as_dict, "channel_id": saved_user_post["channel_id"]}
            await redis_client.set_mapping(vk_user_id, result)
            await send_new_post(saved_user_post["channel_id"], new_user_post)


@app.task
def test_task() -> None:
    celery_event_loop.run_until_complete(create_new_post())
