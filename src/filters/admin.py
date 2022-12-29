import typing

from aiogram.dispatcher.filters import BoundFilter

from src.config import config


class AdminFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin: typing.Optional[bool] = None):
        self.is_admin = is_admin

    async def check(self, message):
        if self.is_admin is None:
            return False
        return (message.from_user.id in config.ADMIN_IDS) == self.is_admin
