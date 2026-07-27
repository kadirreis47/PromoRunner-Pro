from playwright.async_api import Page

from .base_handler import BaseHandler


class UnknownHandler(BaseHandler):

    async def handle(
        self,
        page: Page,
        promo_code: str,
    ) -> bool:

        print("[UNKNOWN] Desteklenmeyen site.")
        return False