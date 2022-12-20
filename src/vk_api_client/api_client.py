import asyncio
from json import JSONDecodeError
from typing import Dict, Union

import aiohttp
from aiohttp.client_exceptions import ClientError

from src.vk_api_client.exceptions import VKAPIException


class VKClientAPI:
    VK_API_URL = "https://api.vk.com/method/"
    USER_GET_URL = VK_API_URL + "users.get/"
    WALL_GET_URL = VK_API_URL + "wall.get/"

    DEFAULT_TIMEOUT = 10
    DEFAULT_FILTER = "owner"
    DEFAULT_POSTS_COUNT = 1

    def __init__(self, session: aiohttp.ClientSession, access_token: str, api_version: str) -> None:
        self.session = session
        self.access_token = access_token
        self.api_version = api_version
        self.auth_params = {"access_token": access_token, "v": api_version}

    async def __get_json(self, url: str, params: Dict = {}, timeout: Union[int, None] = None) -> Dict:
        """Get json content from url"""
        timeout = timeout or self.DEFAULT_TIMEOUT
        params.update(self.auth_params)
        try:
            response = await self.session.get(url, params=params, timeout=timeout)
        except (asyncio.TimeoutError, ClientError) as error:
            raise VKAPIException(str(error), 500)
        if response.status == 200:
            return await self.__make_json(response)
        else:
            raise VKAPIException("Invalid status code", response.status)

    async def __make_json(self, response: aiohttp.ClientResponse) -> Dict:
        try:
            return await response.json()
        except JSONDecodeError as error:
            raise VKAPIException(error.args[0])

    async def check_error(self, response: Dict):
        error = response.get("error")
        if error:
            raise VKAPIException(error, 400)

    async def get_user_by_id(self, id: str, fields: Union[str, None] = None) -> Dict:
        params = {"user_ids": id, "fields": fields}
        if fields:
            params["fields"] = fields
        response = await self.__get_json(self.USER_GET_URL, params=params)
        await self.check_error(response)
        return response

    async def get_user_posts(
        self, user_id: str, count: Union[int, None] = None, filter: Union[str, None] = None
    ) -> Dict:
        if not filter:
            filter = self.DEFAULT_FILTER
        if not count:
            count = self.DEFAULT_POSTS_COUNT
        params = {"owner_id": user_id, "filter": filter, "count": count}
        response = await self.__get_json(self.WALL_GET_URL, params=params)
        await self.check_error(response)
        return response
