from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import BotCommand, Chat, Message

from src.config import bot
from src.services.admin_services import UserService
from src.services.exceptions import UserServiceException
from src.states.user_post import UserPost
from src.vk_api_client.models import User


async def start(message: Message):
    await message.reply("Hello, admin!")


async def start_add_new_post(message: Message):
    await UserPost.AddPostUrlState.set()
    await message.answer("Please, send vk user link or just VK user id!")


async def add_new_user(message: Message, state: FSMContext):
    service = UserService(message.text)
    try:
        user: User = await service.validate_user()
    except UserServiceException:
        await message.answer("There is not valid VK user id. Try again")
        return
    await state.update_data(user_id=user.id)
    await UserPost.next()
    await message.answer("Added {}! Please send telegram channel in format @username".format(user.first_name))


async def admin_add_telegram_channel(message: Message, state: FSMContext):
    state_data = await state.get_data()
    text = message.text
    if text[0] != "@":
        await message.answer("There is not valid Telegram channel id. Try again")
        return
    channel: Chat = await bot.get_chat(text)
    service = UserService(text)
    try:
        await service.add_telegram_channel(state_data["user_id"], channel.id)
    except UserServiceException:
        await message.answer("There is not valid VK user id")
        return
    await state.finish()
    await message.answer("Added!")


def register_admin(dp: Dispatcher):
    start_command_name = "start"
    add_post_command_name = "add_post"
    dp.register_message_handler(start, commands=[start_command_name], state="*", is_admin=True)
    dp.register_message_handler(start_add_new_post, commands=[add_post_command_name], state="*", is_admin=True)
    dp.register_message_handler(add_new_user, state=UserPost.AddPostUrlState, is_admin=True)
    dp.register_message_handler(admin_add_telegram_channel, state=UserPost.AddTelegramChannel, is_admin=True)
    return [BotCommand(start_command_name, "Start bot"), BotCommand(add_post_command_name, "Add Vk post url")]
