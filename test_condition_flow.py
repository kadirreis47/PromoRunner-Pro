import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright

from engine.generic_handler import GenericHandler


async def main():
    profile_path = Path("config/site_profiles/casibom.json")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        handler = GenericHandler(profile)
        result = await handler.handle(page, "TEST123")

        print(f"Test sonucu: {result}")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
