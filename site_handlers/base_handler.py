from abc import ABC, abstractmethod

from playwright.async_api import Page


class BaseHandler(ABC):

    @abstractmethod
    async def handle(
        self,
        page: Page,
        promo_code: str,
    ) -> bool:
        """
        Siteyi işler.

        True dönerse başarılı.
        False dönerse başarısız.
        """
        pass