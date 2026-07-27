from .chatbet import ChatbetHandler
from .robin import RobinHandler
from .unknown import UnknownHandler


class SiteRouter:

    def __init__(self):

        self.handlers = {
            "CHATBET": ChatbetHandler(),
            "ROBIN": RobinHandler(),
        }

        self.unknown = UnknownHandler()

    def get_handler(
        self,
        site_name: str | None,
    ):

        if not site_name:
            return self.unknown

        return self.handlers.get(
            site_name.upper(),
            self.unknown,
        )


router = SiteRouter()