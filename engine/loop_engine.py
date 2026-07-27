from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.condition_engine import ConditionEngine
from engine.variable_engine import VariableEngine


class BreakLoop(Exception):
    """Internal signal used to stop the nearest active loop."""


class ContinueLoop(Exception):
    """Internal signal used to continue the nearest active loop."""


@dataclass(frozen=True)
class LoopSpec:
    loop_type: str
    steps: list[dict[str, Any]]
    index_as: str
    item_as: str
    times: int | None = None
    items: list[Any] | None = None
    condition: dict[str, Any] | None = None
    max_iterations: int = 1000


class LoopEngine:
    SUPPORTED_TYPES = {"repeat", "while", "for_each"}

    @classmethod
    def parse(
        cls,
        step: dict[str, Any],
        variables: dict[str, Any],
    ) -> LoopSpec:
        if not isinstance(step, dict):
            raise ValueError("Loop adımı geçerli bir nesne olmalı.")

        action = str(step.get("action", "loop")).strip().lower()
        loop_type = str(step.get("type", action)).strip().lower()

        if action == "loop" and not step.get("type"):
            raise ValueError("loop adımında type alanı gerekli.")

        if loop_type not in cls.SUPPORTED_TYPES:
            raise ValueError(f"Desteklenmeyen loop tipi: {loop_type}")

        steps = cls._validate_steps(step.get("steps", []))
        index_as = str(step.get("index_as", "loop_index")).strip()
        item_as = str(step.get("item_as", "loop_item")).strip()

        if not index_as:
            raise ValueError("index_as boş olamaz.")
        if not item_as:
            raise ValueError("item_as boş olamaz.")

        max_iterations = cls._resolve_integer(
            step.get("max_iterations", 1000),
            variables,
            "max_iterations",
            minimum=1,
        )

        if loop_type == "repeat":
            raw_times = step.get("times", step.get("count"))
            if raw_times is None:
                raise ValueError("repeat loop için times alanı gerekli.")

            times = cls._resolve_integer(
                raw_times,
                variables,
                "times",
                minimum=0,
            )
            if times > max_iterations:
                raise ValueError("repeat times max_iterations sınırını aşıyor.")
            return LoopSpec(
                loop_type=loop_type,
                steps=steps,
                index_as=index_as,
                item_as=item_as,
                times=times,
                max_iterations=max_iterations,
            )

        if loop_type == "for_each":
            raw_items = step.get("items")
            resolved_items = VariableEngine.resolve(raw_items, variables)

            if isinstance(resolved_items, tuple):
                resolved_items = list(resolved_items)

            if not isinstance(resolved_items, list):
                raise ValueError("for_each loop için items alanı liste olmalı.")

            return LoopSpec(
                loop_type=loop_type,
                steps=steps,
                index_as=index_as,
                item_as=item_as,
                items=resolved_items,
                max_iterations=max_iterations,
            )

        condition = step.get("condition", step.get("while"))
        if not isinstance(condition, dict):
            raise ValueError("while loop için condition alanı gerekli.")

        return LoopSpec(
            loop_type=loop_type,
            steps=steps,
            index_as=index_as,
            item_as=item_as,
            condition=condition,
            max_iterations=max_iterations,
        )

    @staticmethod
    def condition_matches(
        condition: dict[str, Any],
        variables: dict[str, Any],
    ) -> bool:
        return ConditionEngine.evaluate_condition(condition, variables)

    @staticmethod
    def _validate_steps(value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise ValueError("loop steps alanı liste olmalı.")

        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(
                    f"loop içindeki {index}. adım geçerli bir nesne değil."
                )
            validated.append(item)
        return validated

    @staticmethod
    def _resolve_integer(
        value: Any,
        variables: dict[str, Any],
        field_name: str,
        minimum: int,
    ) -> int:
        resolved = VariableEngine.resolve(value, variables)
        try:
            integer = int(resolved)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field_name} tam sayı olmalı.") from exc

        if integer < minimum:
            raise ValueError(f"{field_name} en az {minimum} olmalı.")
        return integer
