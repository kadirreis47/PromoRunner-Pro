from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine.condition_engine import ConditionEngine


@dataclass(frozen=True)
class BranchResult:
    matched: bool
    branch_index: int | None
    branch_name: str
    steps: list[dict[str, Any]]


class BranchEngine:
    """Selects the first matching branch and returns its executable steps."""

    @classmethod
    def select(
        cls,
        step: dict[str, Any],
        variables: dict[str, Any],
    ) -> BranchResult:
        if not isinstance(step, dict):
            raise ValueError("Branch adımı geçerli bir nesne olmalı.")

        branches = step.get("branches", step.get("cases"))

        if not isinstance(branches, list) or not branches:
            raise ValueError("branch adımında boş olmayan branches listesi gerekli.")

        for index, branch in enumerate(branches):
            if not isinstance(branch, dict):
                raise ValueError(f"{index + 1}. branch geçerli bir nesne değil.")

            condition = branch.get("if", branch.get("condition"))
            if condition is None:
                raise ValueError(f"{index + 1}. branch koşulu eksik.")

            if ConditionEngine.evaluate_condition(condition, variables):
                return BranchResult(
                    matched=True,
                    branch_index=index,
                    branch_name=str(branch.get("name", f"branch_{index + 1}")),
                    steps=cls._validate_steps(
                        branch.get("steps", []),
                        f"{index + 1}. branch",
                    ),
                )

        default_value = step.get("default")
        if default_value is None:
            default_value = step.get("else")

        if default_value is None:
            return BranchResult(
                matched=False,
                branch_index=None,
                branch_name="none",
                steps=[],
            )

        if isinstance(default_value, list):
            default_name = "default"
            default_steps = default_value
        elif isinstance(default_value, dict):
            default_name = str(default_value.get("name", "default"))
            default_steps = default_value.get("steps", [])
        else:
            raise ValueError("branch default alanı liste veya nesne olmalı.")

        return BranchResult(
            matched=False,
            branch_index=None,
            branch_name=default_name,
            steps=cls._validate_steps(default_steps, "default branch"),
        )

    @staticmethod
    def _validate_steps(value: Any, source: str) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            raise ValueError(f"{source} steps alanı liste olmalı.")

        validated: list[dict[str, Any]] = []
        for index, item in enumerate(value, start=1):
            if not isinstance(item, dict):
                raise ValueError(
                    f"{source} içindeki {index}. adım geçerli bir nesne değil."
                )
            validated.append(item)

        return validated
