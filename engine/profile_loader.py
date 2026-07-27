from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ProfileLoader:
    def __init__(self, profiles_dir: str | Path = "config/site_profiles") -> None:
        self.profiles_dir = Path(profiles_dir)

    def load(self, site_name: str | None) -> dict[str, Any] | None:
        if not site_name:
            return None

        profile_path = self.profiles_dir / f"{site_name.lower()}.json"

        if not profile_path.exists():
            return None

        try:
            with profile_path.open("r", encoding="utf-8") as file:
                profile = json.load(file)
        except (OSError, json.JSONDecodeError):
            return None

        if not isinstance(profile, dict):
            return None

        if not profile.get("site_name"):
            return None

        return profile