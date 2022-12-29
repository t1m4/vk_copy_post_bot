import json
import re
from typing import Dict, Union

import aiohttp

from src import error_reporting
from src.config import config
from src.vk_api_client.api_client import VKClient
from src.vk_api_client.exceptions import VKAPIException
from src.vk_api_client.models import Post, PostAttachment, User


class VKService:
    DEFAULT_TIMEOUT = 30

    def __init__(self) -> None:
        self._client: VKClient | None = None
        self._session: aiohttp.ClientSession | None = None

    async def start(self):
        session_timeout = aiohttp.ClientTimeout(total=self.DEFAULT_TIMEOUT)
        self._session = aiohttp.ClientSession(timeout=session_timeout)
        self._client = VKClient(self._session, config.VK_ACCESS_TOKEN, config.VK_API_VERSION)

    async def stop(self):
        if self._session is None:
            return
        await self._session.close()

    @property
    def client(self) -> VKClient:
        if client := self._client:
            return client
        raise ValueError("VK service is not started")

    async def get_user(self, user_id: str) -> Union[User, None]:
        """Get user by id"""
        try:
            users_dict = await self.client.get_user_by_id(user_id, "can_see_all_posts")
        except VKAPIException as error:
            with error_reporting.configure_scope():
                error_reporting.set_attachment("get_user.json", json.dumps(error.error_message).encode())
                error_reporting.capture_exception(error)
            return
        if not users_dict["response"]:
            return
        user: Dict = users_dict["response"][0]
        return User(
            id=user["id"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            can_access_closed=user["can_access_closed"],
            can_see_all_posts=user["can_see_all_posts"],
            is_closed=user["is_closed"],
        )

    async def get_user_last_post(self, user_id: str) -> Union[Post, None]:
        """Get user last post by id"""
        try:
            user_posts_dict = await self.client.get_user_posts(user_id)
        except VKAPIException as error:
            with error_reporting.configure_scope():
                error_reporting.set_attachment("get_last_post.json", json.dumps(error.error_message).encode())
                error_reporting.capture_exception(error)
            return

        user_post_response = user_posts_dict["response"]
        if not user_post_response:
            return
        user_last_post: Dict = user_posts_dict["response"]["items"][0]
        user_last_post["text"] = re.sub(" +", " ", user_last_post["text"])
        attachments = []
        for post_attachment in user_last_post["attachments"]:
            attachment_type = post_attachment["type"]
            attachment = PostAttachment(type=attachment_type, url=post_attachment[attachment_type]["sizes"][-1]["url"])
            attachments.append(attachment)
        return Post(id=user_last_post["id"], text=user_last_post["text"], attachments=attachments)


vk_service = VKService()
