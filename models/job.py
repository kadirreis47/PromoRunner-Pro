from dataclasses import dataclass


@dataclass(slots=True)
class PromoJob:
    telegram_message_id: int
    telegram_chat_id: int

    site_name: str | None
    promo_code: str | None
    url: str | None

    raw_text: str