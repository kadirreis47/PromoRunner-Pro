from playwright.async_api import Page

from .base_handler import BaseHandler


class RobinHandler(BaseHandler):

    async def handle(
        self,
        page: Page,
        promo_code: str,
    ) -> bool:

        print("[ROBIN] Handler çalıştı.")
        return True