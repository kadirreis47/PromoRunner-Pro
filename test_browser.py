import asyncio

from browser.browser_manager import BrowserManager


async def main() -> None:
    browser = BrowserManager()

    try:
        await browser.start()
        await browser.open_url("https://www.google.com")

        print()
        print("Tarayıcı başarıyla açıldı.")
        print("Testi bitirmek için PowerShell'de Enter'a bas.")

        await asyncio.to_thread(input)

    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())