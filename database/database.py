import sqlite3
from pathlib import Path
from typing import Optional

from telegram_client.parser import ParsedPromoMessage


DATABASE_PATH = Path("data/promorunner.db")


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS promo_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_message_id INTEGER NOT NULL,
                telegram_chat_id INTEGER NOT NULL,
                message_date TEXT,
                site_name TEXT,
                promo_code TEXT,
                url TEXT,
                raw_text TEXT NOT NULL,
                is_valid INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'pending',
                result_message TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(
                    telegram_chat_id,
                    telegram_message_id
                )
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_promo_code
            ON promo_messages(promo_code)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_status
            ON promo_messages(status)
            """
        )

        connection.commit()


def message_exists(
    telegram_chat_id: int,
    telegram_message_id: int,
) -> bool:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM promo_messages
            WHERE telegram_chat_id = ?
              AND telegram_message_id = ?
            LIMIT 1
            """,
            (
                telegram_chat_id,
                telegram_message_id,
            ),
        ).fetchone()

        return row is not None


def promo_code_exists(
    promo_code: Optional[str],
) -> bool:
    if not promo_code:
        return False

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM promo_messages
            WHERE UPPER(promo_code) = UPPER(?)
            LIMIT 1
            """,
            (promo_code,),
        ).fetchone()

        return row is not None


def save_message(
    telegram_chat_id: int,
    telegram_message_id: int,
    message_date: str,
    parsed: ParsedPromoMessage,
) -> bool:
    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO promo_messages (
                    telegram_message_id,
                    telegram_chat_id,
                    message_date,
                    site_name,
                    promo_code,
                    url,
                    raw_text,
                    is_valid
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    telegram_message_id,
                    telegram_chat_id,
                    message_date,
                    parsed.site_name,
                    parsed.promo_code,
                    parsed.url,
                    parsed.raw_text,
                    int(parsed.is_valid),
                ),
            )

            connection.commit()
            return True

    except sqlite3.IntegrityError:
        return False


def update_message_status(
    telegram_chat_id: int,
    telegram_message_id: int,
    status: str,
    result_message: Optional[str] = None,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE promo_messages
            SET
                status = ?,
                result_message = ?
            WHERE telegram_chat_id = ?
              AND telegram_message_id = ?
            """,
            (
                status,
                result_message,
                telegram_chat_id,
                telegram_message_id,
            ),
        )

        connection.commit()