from playwright.async_api import Page

from .base_handler import BaseHandler


class ChatbetHandler(BaseHandler):

    async def handle(
        self,
        page: Page,
        promo_code: str,
    ) -> bool:

        print("[CHATBET] Handler çalıştı.")
        print(f"[CHATBET] Promo Kod : {promo_code}")

        # Şimdilik sadece hazır olduğunu gösteriyoruz.
        return True