from datetime import datetime, timezone

import aiosqlite

from .config import DB_PATH

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tg_user_id INTEGER NOT NULL,
    tg_username TEXT,
    full_name TEXT,
    category TEXT NOT NULL,
    subcategory TEXT,
    description TEXT NOT NULL,
    contact_phone TEXT,
    address TEXT,
    format TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT NOT NULL
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()


async def save_order(order: dict) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            INSERT INTO orders
                (tg_user_id, tg_username, full_name, category, subcategory,
                 description, contact_phone, address, format, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order["tg_user_id"],
                order.get("tg_username"),
                order.get("full_name"),
                order["category"],
                order.get("subcategory"),
                order["description"],
                order.get("contact_phone"),
                order.get("address"),
                order.get("format"),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await db.commit()
        return cursor.lastrowid


async def get_orders(limit: int = 50) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def update_status(order_id: int, status: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        await db.commit()


async def cancel_order(order_id: int, tg_user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            UPDATE orders
            SET status = 'cancelled'
            WHERE id = ?
              AND tg_user_id = ?
              AND status = 'new'
            """,
            (order_id, tg_user_id),
        )
        await db.commit()
        return cursor.rowcount > 0
    