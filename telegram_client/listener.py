import os

from dotenv import load_dotenv
from telethon import TelegramClient, events

from database.database import (
    initialize_database,
    message_exists,
    promo_code_exists,
    save_message,
)
from job_queue import job_queue
from models.job import PromoJob
from telegram_client.parser import parse_message


load_dotenv()


API_ID_RAW = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL", "").strip()


if not API_ID_RAW:
    raise RuntimeError(
        "TELEGRAM_API_ID .env dosyasında bulunamadı."
    )

if not API_HASH:
    raise RuntimeError(
        "TELEGRAM_API_HASH .env dosyasında bulunamadı."
    )

if not PHONE_NUMBER:
    raise RuntimeError(
        "TELEGRAM_PHONE .env dosyasında bulunamadı."
    )


API_ID = int(API_ID_RAW)


client = TelegramClient(
    session="data/promorunner_session",
    api_id=API_ID,
    api_hash=API_HASH,
)


async def process_message(
    event: events.NewMessage.Event,
) -> None:
    message = event.message
    text = message.raw_text or ""

    if not text.strip():
        return

    chat_id = event.chat_id

    if chat_id is None:
        print("Chat ID bulunamadığı için mesaj atlandı.")
        return

    if message_exists(chat_id, message.id):
        print(f"Tekrar mesaj atlandı: {message.id}")
        return

    parsed = parse_message(text)

    code_already_exists = promo_code_exists(
        parsed.promo_code
    )

    saved = save_message(
        telegram_chat_id=chat_id,
        telegram_message_id=message.id,
        message_date=message.date.isoformat(),
        parsed=parsed,
    )

    print("\n" + "=" * 70)
    print(f"Mesaj ID    : {message.id}")
    print(f"Chat ID     : {chat_id}")
    print(f"Tarih       : {message.date}")
    print(
        f"Site        : "
        f"{parsed.site_name or 'Bulunamadı'}"
    )
    print(
        f"Kod         : "
        f"{parsed.promo_code or 'Bulunamadı'}"
    )
    print(
        f"URL         : "
        f"{parsed.url or 'Bulunamadı'}"
    )
    print(
        f"Geçerli     : "
        f"{'Evet' if parsed.is_valid else 'Hayır'}"
    )
    print(
        f"Kod tekrar  : "
        f"{'Evet' if code_already_exists else 'Hayır'}"
    )
    print(
        f"Kaydedildi  : "
        f"{'Evet' if saved else 'Hayır'}"
    )

    if saved and parsed.is_valid:
        job = PromoJob(
            telegram_message_id=message.id,
            telegram_chat_id=chat_id,
            site_name=parsed.site_name,
            promo_code=parsed.promo_code,
            url=parsed.url,
            raw_text=parsed.raw_text,
        )

        await job_queue.put(job)

    print("-" * 70)
    print(f"Ham mesaj:\n{text}")
    print("=" * 70)


async def main() -> None:
    initialize_database()
    print("Veritabanı hazır.")

    await client.start(
        phone=PHONE_NUMBER
    )

    me = await client.get_me()

    print(
        f"Telegram bağlantısı başarılı: "
        f"{me.first_name}"
    )
    print(
        "Yeni kanal mesajları bekleniyor..."
    )

    if TARGET_CHANNEL:
        entity = await client.get_entity(
            TARGET_CHANNEL
        )

        @client.on(
            events.NewMessage(chats=entity)
        )
        async def target_channel_handler(
            event: events.NewMessage.Event,
        ) -> None:
            await process_message(event)

        print(
            f"Takip edilen kanal: "
            f"{TARGET_CHANNEL}"
        )

    else:

        @client.on(events.NewMessage())
        async def all_messages_handler(
            event: events.NewMessage.Event,
        ) -> None:
            if event.is_channel:
                await process_message(event)

        print(
            "TARGET_CHANNEL boş. "
            "Erişilebilen bütün kanal "
            "mesajları gösterilecek."
        )

    await client.run_until_disconnected()