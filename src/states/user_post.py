from aiogram.dispatcher.filters.state import State, StatesGroup


class UserPost(StatesGroup):
    AddPostUrlState = State()
    AddTelegramChannel = State()
