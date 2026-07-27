from __future__ import annotations

from typing import Any


class ExecutionContext:
    def __init__(self) -> None:
        self.variables: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self.variables[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self.variables.get(key, default)

    def has(self, key: str) -> bool:
        return key in self.variables

    def delete(self, key: str) -> None:
        self.variables.pop(key, None)

    def all(self) -> dict[str, Any]:
        return dict(self.variables)
