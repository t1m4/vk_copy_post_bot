import dataclasses
import re

from src.redis_client.client import AsyncRedisClient
from src.services.exceptions import UserDoesNotExist
from src.vk_api_client import services as vk_api_services
from src.vk_api_client.api_client import VKClientAPI
from src.vk_api_client.models import User


class UserService:
    def __init__(self, message: str, api_client: VKClientAPI, redis_client: AsyncRedisClient) -> None:
        self.message = message
        self.api_client = api_client
        self.redis_client = redis_client

    def _get_user_id_from_message(self) -> str:
        user_id = re.search(r"\d*$", self.message).group(0)  # type: ignore
        if not user_id:
            raise UserDoesNotExist("There is no user_id in this message {}".format(self.message))
        return user_id

    async def validate_user(self) -> User:
        """Validate user using VK API"""
        user_id = self._get_user_id_from_message()
        user = await vk_api_services.get_user(self.api_client, user_id)
        if not (user and user.can_see_all_posts and user.can_access_closed):
            raise UserDoesNotExist("This user is not allowed")
        return user

    async def add_telegram_channel(self, user_id: str, channel_id: int):
        """Add telegram channel to existing VK user"""
        post = await vk_api_services.get_user_last_post(self.api_client, user_id)
        post_as_dict = dataclasses.asdict(post)
        result = {"post": post_as_dict, "channel_id": channel_id}
        await self.redis_client.set_mapping(user_id, result)
