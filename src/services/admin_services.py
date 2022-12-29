import dataclasses
import re

from src.config import redis_client
from src.services.exceptions import UserDoesNotExist
from src.vk_api_client.models import User
from src.vk_api_client.services import vk_service


class UserService:
    def __init__(self, message: str) -> None:
        self.message = message

    def _get_user_id_from_message(self) -> str:
        user_id = re.search(r"\d*$", self.message).group(0)  # type: ignore
        if not user_id:
            raise UserDoesNotExist
        return user_id

    async def validate_user(self) -> User:
        """Validate user using VK API"""
        user_id = self._get_user_id_from_message()
        user = await vk_service.get_user(user_id)
        if not user or not (user and user.can_see_all_posts and user.can_access_closed):
            raise UserDoesNotExist
        return user

    async def add_telegram_channel(self, user_id: str, channel_id: int):
        """Add telegram channel to existing VK user"""
        post = await vk_service.get_user_last_post(user_id)
        if not post:
            raise UserDoesNotExist
        post_as_dict = dataclasses.asdict(post)
        result = {"post": post_as_dict, "channel_id": channel_id}
        await redis_client.set_mapping(user_id, result)
