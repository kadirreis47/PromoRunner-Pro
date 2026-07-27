from engine.generic_handler import GenericHandler
from engine.profile_loader import ProfileLoader

from .unknown import UnknownHandler


class SiteRouter:
    def __init__(self) -> None:
        self.profile_loader = ProfileLoader()
        self.unknown = UnknownHandler()

    def get_handler(
        self,
        site_name: str | None,
    ):
        profile = self.profile_loader.load(site_name)

        if not profile:
            return self.unknown

        return GenericHandler(profile)


router = SiteRouter()