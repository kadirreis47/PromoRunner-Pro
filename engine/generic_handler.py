from __future__ import annotations

from typing import Any

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from site_handlers.base_handler import BaseHandler


class GenericHandler(BaseHandler):
    def __init__(self, profile: dict[str, Any]) -> None:
        self.profile = profile

    async def handle(
        self,
        page: Page,
        promo_code: str,
    ) -> bool:
        start_url = self.profile.get("start_url")
        ready_selector = self.profile.get("ready_selector")
        timeout = int(self.profile.get("timeout_ms", 15000))

        if not start_url:
            print("[GENERIC] Profilde start_url eksik.")
            return False

        try:
            print(
                f"[GENERIC] Site açılıyor: "
                f"{self.profile.get('site_name', 'UNKNOWN')}"
            )

            await page.goto(
                start_url,
                wait_until="domcontentloaded",
                timeout=timeout,
            )

            if ready_selector:
                await page.wait_for_selector(
                    ready_selector,
                    timeout=timeout,
                )

            print(f"[GENERIC] Sayfa hazır: {page.url}")
            print(f"[GENERIC] Promo kodu algılandı: {promo_code}")

            return True

        except PlaywrightTimeoutError:
            print("[GENERIC] Sayfa zaman aşımına uğradı.")
            return False

        except Exception as exc:
            print(f"[GENERIC] Beklenmeyen hata: {exc}")
            return False