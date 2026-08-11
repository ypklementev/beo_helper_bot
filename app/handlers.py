from aiogram import F, Router
from .db import cancel_order
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from .db import cancel_order, get_order
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from .config import ADMIN_CHAT_ID, WEBAPP_URL

router = Router()

MENU_TEXT = (
    "⚡️ <b>IT-помощь в Белграде: техника, сеть, сайты!</b>\n\n"
    "Быстрый выезд или удалённое подключение, точная диагностика, "
    "понятное объяснение проблемы.\n\n"
    "🖥 <b>Настройка и ремонт техники</b>\n"
    "Ноутбук тормозит или зависает — диагностика, чистка, удаление вирусов, "
    "переустановка системы, замена компонентов. Настройка Wi-Fi роутеров, "
    "принтеров, устройств умного дома, перенос данных, настройка аккаунтов.\n\n"
    "🚀 <b>Сайты и Telegram-боты под ключ</b>\n"
    "Лендинг, интернет-магазин, сайт-визитка. Боты для записи клиентов, "
    "приёма заказов, рассылок. Автоматизация, оплата, мобильная адаптация, "
    "помощь со стартовым продвижением.\n\n"
    "✅ Разберусь в задаче, дам понятную оценку по срокам и стоимости.\n\n"
    "Нажми кнопку ниже, чтобы оформить заявку 👇"
)


def order_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Оформить заказ",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(MENU_TEXT, reply_markup=order_keyboard())


@router.message()
async def fallback(message: Message) -> None:
    try:
        await message.delete()
    except Exception:
        pass

    await message.answer(
        "Чтобы оформить заявку, нажми кнопку ниже 👇",
        reply_markup=order_keyboard(),
    )


@router.callback_query(F.data.startswith("cancel_order:"))
async def cancel_order_handler(callback: CallbackQuery) -> None:
    if callback.from_user is None:
        return

    order_id = int(callback.data.split(":")[1])

    order = await get_order(order_id)

    if not order:
        await callback.answer(
            "Заявка не найдена.",
            show_alert=True,
        )
        return

    if order["tg_user_id"] != callback.from_user.id:
        await callback.answer(
            "Эта заявка принадлежит другому пользователю.",
            show_alert=True,
        )
        return

    if order["status"] != "new":
        await callback.answer(
            "Эту заявку уже нельзя отменить.",
            show_alert=True,
        )
        return

    cancelled = await cancel_order(
        order_id=order_id,
        tg_user_id=callback.from_user.id,
    )

    if not cancelled:
        await callback.answer(
            "Не удалось отменить заявку.",
            show_alert=True,
        )
        return

    # Уведомляем пользователя
    await callback.message.edit_text(
        f"❌ <b>Заявка #{order_id} отменена.</b>\n\n"
        "Заявка больше не будет обрабатываться.",
    )

    await callback.answer("Заявка отменена")

    # Редактируем сообщение в чате администратора
    if order["admin_message_id"]:
        try:
            await callback.bot.edit_message_text(
                chat_id=ADMIN_CHAT_ID,
                message_id=order["admin_message_id"],
                text=(
                    f"❌ <b>Заявка #{order_id} ОТМЕНЕНА</b>\n\n"
                    f"👤 {order['full_name'] or '—'} "
                    f"(@{order['tg_username'] or '—'})\n"
                    f"📂 {order['category']}"
                    + (
                        f" / {order['subcategory']}"
                        if order["subcategory"]
                        else ""
                    )
                    + f"\n📝 {order['description']}"
                ),
                parse_mode="HTML",
            )
        except TelegramBadRequest:
            pass