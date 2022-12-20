import json
import re
from typing import Dict, Union

from src import error_reporting
from src.vk_api_client.api_client import VKClientAPI
from src.vk_api_client.exceptions import VKAPIException
from src.vk_api_client.models import Post, PostAttachment, User


async def get_user(api_client: VKClientAPI, user_id: str) -> Union[User, None]:
    try:
        users_dict = await api_client.get_user_by_id(user_id, "can_see_all_posts")
    except VKAPIException as error:
        with error_reporting.configure_scope():
            error_reporting.set_attachment("get_user.json", json.dumps(error.error_message).encode())
            error_reporting.capture_exception(error)
        raise error
    if not users_dict["response"]:
        raise VKAPIException("User does not exist")
    user: Dict = users_dict["response"][0]
    return User(
        id=user["id"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        can_access_closed=user["can_access_closed"],
        can_see_all_posts=user["can_see_all_posts"],
        is_closed=user["is_closed"],
    )


async def get_user_last_post(api_client: VKClientAPI, user_id: str) -> Union[Post, None]:
    try:
        user_posts_dict = await api_client.get_user_posts(user_id)
    except VKAPIException as error:
        with error_reporting.configure_scope():
            error_reporting.set_attachment("get_last_post.json", json.dumps(error.error_message).encode())
            error_reporting.capture_exception(error)
        raise error

    user_post_response = user_posts_dict["response"]
    if not user_post_response:
        raise VKAPIException("User does not exist")
    user_last_post: Dict = user_posts_dict["response"]["items"][0]
    user_last_post["text"] = re.sub(" +", " ", user_last_post["text"])
    attachments = []
    for post_attachment in user_last_post["attachments"]:
        attachment_type = post_attachment["type"]
        attachment = PostAttachment(type=attachment_type, url=post_attachment[attachment_type]["sizes"][-1]["url"])
        attachments.append(attachment)
    return Post(id=user_last_post["id"], text=user_last_post["text"], attachments=attachments)
