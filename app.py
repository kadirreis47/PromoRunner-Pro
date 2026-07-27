import asyncio

from telegram_client.listener import main as telegram_main
from worker import worker


async def run() -> None:
    try:
        await asyncio.gather(
            telegram_main(),
            worker.run(),
        )

    finally:
        await worker.browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(run())

    except KeyboardInterrupt:
        print()
        print("PromoRunner kullanıcı tarafından durduruldu.")