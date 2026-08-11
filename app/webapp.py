from pathlib import Path

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.session.aiohttp import AiohttpSession
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from .config import ADMIN_CHAT_ID, BOT_TOKEN, PROXY_URL
from .db import init_db, save_order
from .telegram_auth import validate_init_data
from .db import init_db, save_order, set_admin_message_id

app = FastAPI(title="IT Services Order API")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_session = AiohttpSession(proxy=PROXY_URL) if PROXY_URL else None
notify_bot = Bot(token=BOT_TOKEN, session=_session)


class OrderPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    init_data: str = Field(..., alias="initData")
    category: str
    subcategory: str | None = None
    description: str
    contact_phone: str | None = None
    address: str | None = None
    format: str | None = None


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/order")
async def create_order(payload: OrderPayload) -> dict:
    parsed = validate_init_data(payload.init_data)
    if parsed is None:
        raise HTTPException(
            status_code=401, detail="Invalid Telegram init data")

    if not payload.description.strip():
        raise HTTPException(status_code=422, detail="Description is required")

    user = parsed.get("user", {})
    order = {
        "tg_user_id": user.get("id"),
        "tg_username": user.get("username"),
        "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        "category": payload.category,
        "subcategory": payload.subcategory,
        "description": payload.description.strip(),
        "contact_phone": payload.contact_phone,
        "address": payload.address,
        "format": payload.format,
    }
    order_id = await save_order(order)

    lines = [
        f"🆕 <b>Новая заявка #{order_id}</b>",
        "",
        f"👤 {order['full_name'] or '—'} (@{order['tg_username'] or '—'})",
        f"📂 {order['category']}"
        + (f" / {order['subcategory']}" if order["subcategory"] else ""),
        f"📝 {order['description']}",
    ]
    if order["contact_phone"]:
        lines.append(f"📞 {order['contact_phone']}")
    if order["address"]:
        lines.append(f"📍 {order['address']}")
    if order["format"]:
        lines.append(f"🔧 Формат: {order['format']}")

    admin_message = None

    if ADMIN_CHAT_ID:
        admin_message = await notify_bot.send_message(ADMIN_CHAT_ID, "\n".join(lines), parse_mode="HTML")
        await set_admin_message_id(
            order_id,
            admin_message.message_id,
        )
    user_id = order["tg_user_id"]
    if user_id:
        user_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="❌ Отменить заявку",
                        callback_data=f"cancel_order:{order_id}",
                    )
                ]
            ]
        )

        await notify_bot.send_message(
            user_id,
            (
                f"✅ Заявка отправлена!\n\n"
                "Мы получили вашу заявку и скоро свяжемся с вами.\n\n"
                "Если вы передумали, заявку можно отменить кнопкой ниже."
            ),
            reply_markup=user_keyboard,
        )

    return {"ok": True, "order_id": order_id}
