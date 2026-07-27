import re
from typing import Any


class VariableEngine:
    _pattern = re.compile(r"\$\{([^}]+)\}")

    @classmethod
    def resolve(
        cls,
        value: Any,
        variables: dict[str, Any],
    ) -> Any:

        if not isinstance(value, str):
            return value

        def replace(match):
            key = match.group(1)
            return str(variables.get(key, match.group(0)))

        return cls._pattern.sub(replace, value)