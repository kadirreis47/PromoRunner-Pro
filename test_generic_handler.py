import asyncio

from browser.browser_manager import BrowserManager
from site_handlers.router import router


async def main() -> None:
    browser = BrowserManager()

    try:
        await browser.start()

        if browser.context is None:
            raise RuntimeError("Tarayıcı context oluşturulamadı.")

        # Kalıcı profildeki eski sekmeyi kullanmak yerine temiz sekme aç.
        page = await browser.context.new_page()

        handler = router.get_handler("CASIBOM")

        result = await handler.handle(
            page=page,
            promo_code="TEST123",
        )

        print(f"Test sonucu: {result}")

    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())