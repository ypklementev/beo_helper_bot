from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from .config import ADMIN_USER_ID

router = Router()


def is_admin(message: Message) -> bool:
    return message.from_user is not None and message.from_user.id == ADMIN_USER_ID


@router.message(Command("admin"))
async def admin_panel(message: Message) -> None:
    if not is_admin(message):
        return

    await message.answer(
        "🔧 <b>Админ-панель</b>\n\n"
        "/chat_id — ID текущего чата\n"
        "/chat_info — подробная информация о чате\n"
        "/bot_info — информация о боте\n"
        "/ping — проверка работы бота"
    )


@router.message(Command("chat_id"))
async def chat_id(message: Message) -> None:
    if not is_admin(message):
        return

    chat = message.chat

    title = chat.title or "—"
    username = f"@{chat.username}" if chat.username else "—"

    await message.answer(
        "💬 <b>Информация о чате</b>\n\n"
        f"<b>ID:</b> <code>{chat.id}</code>\n"
        f"<b>Название:</b> {title}\n"
        f"<b>Тип:</b> {chat.type}\n"
        f"<b>Username:</b> {username}"
    )


@router.message(Command("chat_info"))
async def chat_info(message: Message) -> None:
    if not is_admin(message):
        return

    chat = message.chat

    await message.answer(
        "🔎 <b>Chat info</b>\n\n"
        f"<b>ID:</b> <code>{chat.id}</code>\n"
        f"<b>Type:</b> {chat.type}\n"
        f"<b>Title:</b> {chat.title or '—'}\n"
        f"<b>Username:</b> @{chat.username if chat.username else '—'}\n"
        f"<b>Bot:</b> {'Да' if chat.type == 'private' else 'Нет'}"
    )


@router.message(Command("bot_info"))
async def bot_info(message: Message) -> None:
    if not is_admin(message):
        return

    bot = message.bot
    me = await bot.get_me()

    await message.answer(
        "🤖 <b>Bot info</b>\n\n"
        f"<b>ID:</b> <code>{me.id}</code>\n"
        f"<b>Username:</b> @{me.username}\n"
        f"<b>Name:</b> {me.full_name}"
    )


@router.message(Command("ping"))
async def ping(message: Message) -> None:
    if not is_admin(message):
        return

    await message.answer("🏓 Pong!")