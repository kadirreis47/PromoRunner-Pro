import re
from typing import Any


class VariableEngine:
    _pattern = re.compile(r"\$\{([^}]+)\}")
    _exact_pattern = re.compile(r"^\$\{([^}]+)\}$")

    @classmethod
    def resolve(
        cls,
        value: Any,
        variables: dict[str, Any],
    ) -> Any:
        if isinstance(value, list):
            return [cls.resolve(item, variables) for item in value]

        if isinstance(value, dict):
            return {
                key: cls.resolve(item, variables)
                for key, item in value.items()
            }

        if not isinstance(value, str):
            return value

        exact_match = cls._exact_pattern.match(value)
        if exact_match:
            key = exact_match.group(1)
            return variables.get(key, value)

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            return str(variables.get(key, match.group(0)))

        return cls._pattern.sub(replace, value)
