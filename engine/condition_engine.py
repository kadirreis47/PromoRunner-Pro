from typing import Any

from engine.variable_engine import VariableEngine


class ConditionEngine:
    @staticmethod
    def _resolve(value: Any, variables: dict[str, Any]) -> Any:
        return VariableEngine.resolve(value, variables)

    @classmethod
    def evaluate(
        cls,
        operator: str,
        left: Any,
        right: Any,
        variables: dict[str, Any],
    ) -> bool:
        operator = str(operator).strip().lower()
        resolved_left = cls._resolve(left, variables)
        resolved_right = cls._resolve(right, variables)

        if operator == "contains":
            return str(resolved_right) in str(resolved_left)

        if operator == "not_contains":
            return str(resolved_right) not in str(resolved_left)

        if operator == "equals":
            return str(resolved_left) == str(resolved_right)

        if operator == "not_equals":
            return str(resolved_left) != str(resolved_right)

        if operator == "starts_with":
            return str(resolved_left).startswith(str(resolved_right))

        if operator == "ends_with":
            return str(resolved_left).endswith(str(resolved_right))

        if operator in {"greater_than", "gt"}:
            return cls._as_number(resolved_left) > cls._as_number(resolved_right)

        if operator in {"greater_or_equal", "gte"}:
            return cls._as_number(resolved_left) >= cls._as_number(resolved_right)

        if operator in {"less_than", "lt"}:
            return cls._as_number(resolved_left) < cls._as_number(resolved_right)

        if operator in {"less_or_equal", "lte"}:
            return cls._as_number(resolved_left) <= cls._as_number(resolved_right)

        if operator == "in":
            return resolved_left in resolved_right

        if operator == "not_in":
            return resolved_left not in resolved_right

        if operator == "exists":
            return resolved_left is not None and str(resolved_left).strip() != ""

        if operator == "not_exists":
            return resolved_left is None or str(resolved_left).strip() == ""

        raise ValueError(f"Desteklenmeyen koşul operatörü: {operator}")

    @staticmethod
    def _as_number(value: Any) -> float:
        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Sayısal değer bekleniyordu: {value}") from exc

    @classmethod
    def evaluate_condition(
        cls,
        condition: dict[str, Any],
        variables: dict[str, Any],
    ) -> bool:
        if not isinstance(condition, dict):
            raise ValueError("Koşul geçerli bir nesne olmalı.")

        if "all" in condition:
            conditions = condition["all"]

            if not isinstance(conditions, list) or not conditions:
                raise ValueError("all alanı boş olmayan bir liste olmalı.")

            return all(
                cls.evaluate_condition(item, variables)
                for item in conditions
            )

        if "any" in condition:
            conditions = condition["any"]

            if not isinstance(conditions, list) or not conditions:
                raise ValueError("any alanı boş olmayan bir liste olmalı.")

            return any(
                cls.evaluate_condition(item, variables)
                for item in conditions
            )

        if "not" in condition:
            return not cls.evaluate_condition(
                condition["not"],
                variables,
            )

        operator = condition.get("operator")

        if not operator:
            raise ValueError("Koşul operator alanı eksik.")

        return cls.evaluate(
            operator=operator,
            left=condition.get("left"),
            right=condition.get("right", ""),
            variables=variables,
        )

    @classmethod
    def contains(cls, left, right, variables):
        return cls.evaluate("contains", left, right, variables)

    @classmethod
    def equals(cls, left, right, variables):
        return cls.evaluate("equals", left, right, variables)
