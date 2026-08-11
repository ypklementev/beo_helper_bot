from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from .config import WEBAPP_URL

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
    await message.answer(
        "Чтобы оформить заявку, нажми кнопку ниже 👇", reply_markup=order_keyboard()
    )
