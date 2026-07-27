from pathlib import Path
from typing import Optional

from playwright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)


BROWSER_PROFILE_PATH = Path("data/browser_profile")


class BrowserManager:
    def __init__(self) -> None:
        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start(self) -> Page:
        BROWSER_PROFILE_PATH.mkdir(parents=True, exist_ok=True)

        self.playwright = await async_playwright().start()

        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE_PATH),
            headless=False,
            viewport={
                "width": 1400,
                "height": 900,
            },
            locale="tr-TR",
            args=[
                "--start-maximized",
                "--disable-notifications",
            ],
        )

        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()

        print("Tarayıcı motoru hazır.")
        return self.page

    async def open_url(self, url: str) -> Page:
        if not self.page:
            await self.start()

        if not self.page:
            raise RuntimeError("Tarayıcı sayfası oluşturulamadı.")

        print(f"Bağlantı açılıyor: {url}")

        await self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60_000,
        )

        print(f"Açılan adres: {self.page.url}")
        return self.page

    async def close(self) -> None:
        if self.context:
            await self.context.close()

        if self.playwright:
            await self.playwright.stop()

        self.page = None
        self.context = None
        self.playwright = None