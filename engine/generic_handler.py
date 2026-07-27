from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from playwright.async_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
)

from engine.action_if import ActionIf
from engine.branch_engine import BranchEngine
from engine.context import ExecutionContext
from engine.loop_engine import BreakLoop, ContinueLoop, LoopEngine
from engine.variable_engine import VariableEngine
from site_handlers.base_handler import BaseHandler


class GenericHandler(BaseHandler):
    def __init__(self, profile: dict[str, Any]) -> None:
        self.profile = profile

    async def handle(
        self,
        page: Page,
        promo_code: str,
    ) -> bool:
        site_name = str(self.profile.get("site_name", "UNKNOWN"))
        timeout = int(self.profile.get("timeout_ms", 15_000))
        steps = self.profile.get("steps", [])

        context = ExecutionContext()
        context.set("promo_code", promo_code)
        context.set("site", site_name)

        profile_variables = self.profile.get("variables", {})

        if isinstance(profile_variables, dict):
            for key, value in profile_variables.items():
                context.set(
                    str(key),
                    VariableEngine.resolve(value, context.all()),
                )

        if not isinstance(steps, list) or not steps:
            print(f"[GENERIC] {site_name}: Çalıştırılabilir adım bulunamadı.")
            return False

        print(f"[GENERIC] Profil çalışıyor: {site_name}")

        try:
            await self._execute_steps(
                page=page,
                steps=steps,
                context=context,
                timeout=timeout,
            )

            print(f"[GENERIC] Profil başarıyla tamamlandı: {site_name}")
            return True

        except PlaywrightTimeoutError as exc:
            print(f"[GENERIC] Zaman aşımı: {exc}")
            return False

        except Exception as exc:
            print(f"[GENERIC] Profil hatası: {exc}")
            return False

    async def _execute_steps(
        self,
        page: Page,
        steps: list[dict[str, Any]],
        context: ExecutionContext,
        timeout: int,
        scope: str = "root",
        loop_depth: int = 0,
    ) -> None:
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                raise ValueError(
                    f"{scope} içindeki {index}. adım geçerli bir nesne değil."
                )

            action = str(step.get("action", "")).strip().lower()
            position = f"{scope}.{index}" if scope != "root" else str(index)

            if not ActionIf.should_execute(step, context):
                print(
                    f"[GENERIC] Adım {position} atlandı: "
                    f"koşul sağlanmadı ({action})"
                )
                continue

            print(f"[GENERIC] Adım {position}: {action}")

            await self._execute_step(
                page=page,
                step=step,
                context=context,
                timeout=timeout,
                loop_depth=loop_depth,
            )

    async def _execute_branch(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
        timeout: int,
        loop_depth: int,
    ) -> None:
        result = BranchEngine.select(step, context.all())

        if not result.steps:
            print("[GENERIC] Branch eşleşmedi; çalıştırılacak adım yok.")
            return

        print(f"[GENERIC] Branch seçildi: {result.branch_name}")

        await self._execute_steps(
            page=page,
            steps=result.steps,
            context=context,
            timeout=timeout,
            scope=f"branch:{result.branch_name}",
            loop_depth=loop_depth,
        )

    async def _execute_step(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
        timeout: int,
        loop_depth: int = 0,
    ) -> None:
        action = str(step.get("action", "")).strip().lower()

        if action == "goto":
            await self._goto(page, step, context, timeout)

        elif action == "wait":
            await self._wait(page, step, context, timeout)

        elif action == "sleep":
            await self._sleep(step)

        elif action == "screenshot":
            await self._screenshot(page, step, context)

        elif action == "assert_url":
            self._assert_url(page, step, context)

        elif action == "assert_text":
            await self._assert_text(page, step, context, timeout)

        elif action == "extract_text":
            await self._extract_text(page, step, context, timeout)

        elif action == "log":
            self._log(step, context)

        elif action == "branch":
            await self._execute_branch(
                page, step, context, timeout, loop_depth
            )

        elif action in {"loop", "repeat", "while", "for_each"}:
            await self._execute_loop(
                page, step, context, timeout, loop_depth
            )

        elif action == "break":
            if loop_depth < 1:
                raise ValueError("break yalnızca loop içinde kullanılabilir.")
            raise BreakLoop()

        elif action == "continue":
            if loop_depth < 1:
                raise ValueError("continue yalnızca loop içinde kullanılabilir.")
            raise ContinueLoop()

        elif action == "set":
            self._set_variable(step, context)

        elif action == "increment":
            self._increment_variable(step, context)

        else:
            raise ValueError(f"Desteklenmeyen action: {action}")

    async def _execute_loop(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
        timeout: int,
        loop_depth: int,
    ) -> None:
        spec = LoopEngine.parse(step, context.all())
        saved = self._save_loop_variables(
            context, spec.index_as, spec.item_as
        )

        try:
            if spec.loop_type == "repeat":
                assert spec.times is not None
                for index in range(spec.times):
                    context.set(spec.index_as, index)
                    context.set(spec.item_as, index)
                    if await self._run_loop_iteration(
                        page, spec.steps, context, timeout,
                        loop_depth, f"repeat:{index}"
                    ):
                        break

            elif spec.loop_type == "for_each":
                assert spec.items is not None
                for index, item in enumerate(spec.items):
                    if index >= spec.max_iterations:
                        raise RuntimeError(
                            "for_each max_iterations sınırını aştı."
                        )
                    context.set(spec.index_as, index)
                    context.set(spec.item_as, item)
                    if await self._run_loop_iteration(
                        page, spec.steps, context, timeout,
                        loop_depth, f"for_each:{index}"
                    ):
                        break

            else:
                assert spec.condition is not None
                index = 0
                while LoopEngine.condition_matches(
                    spec.condition, context.all()
                ):
                    if index >= spec.max_iterations:
                        raise RuntimeError(
                            "while max_iterations sınırını aştı."
                        )
                    context.set(spec.index_as, index)
                    context.set(spec.item_as, index)
                    should_break = await self._run_loop_iteration(
                        page, spec.steps, context, timeout,
                        loop_depth, f"while:{index}"
                    )
                    index += 1
                    if should_break:
                        break
        finally:
            self._restore_loop_variables(context, saved)

    async def _run_loop_iteration(
        self,
        page: Page,
        steps: list[dict[str, Any]],
        context: ExecutionContext,
        timeout: int,
        loop_depth: int,
        scope: str,
    ) -> bool:
        try:
            await self._execute_steps(
                page=page,
                steps=steps,
                context=context,
                timeout=timeout,
                scope=scope,
                loop_depth=loop_depth + 1,
            )
        except ContinueLoop:
            return False
        except BreakLoop:
            return True
        return False

    @staticmethod
    def _save_loop_variables(
        context: ExecutionContext,
        *names: str,
    ) -> dict[str, tuple[bool, Any]]:
        return {
            name: (context.has(name), context.get(name))
            for name in set(names)
        }

    @staticmethod
    def _restore_loop_variables(
        context: ExecutionContext,
        saved: dict[str, tuple[bool, Any]],
    ) -> None:
        for name, (existed, value) in saved.items():
            if existed:
                context.set(name, value)
            else:
                context.delete(name)

    @staticmethod
    def _set_variable(
        step: dict[str, Any],
        context: ExecutionContext,
    ) -> None:
        name = str(step.get("name", step.get("save_as", ""))).strip()
        if not name:
            raise ValueError("set adımında name alanı gerekli.")
        value = VariableEngine.resolve(step.get("value"), context.all())
        context.set(name, value)

    @staticmethod
    def _increment_variable(
        step: dict[str, Any],
        context: ExecutionContext,
    ) -> None:
        name = str(step.get("name", "")).strip()
        if not name:
            raise ValueError("increment adımında name alanı gerekli.")

        amount = VariableEngine.resolve(step.get("by", 1), context.all())
        current = context.get(name, 0)
        try:
            new_value = float(current) + float(amount)
        except (TypeError, ValueError) as exc:
            raise ValueError("increment yalnızca sayısal değerlerle çalışır.") from exc

        if new_value.is_integer():
            context.set(name, int(new_value))
        else:
            context.set(name, new_value)

    async def _goto(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
        timeout: int,
    ) -> None:
        url = VariableEngine.resolve(step.get("url"), context.all())

        if not url:
            raise ValueError("goto adımında url eksik.")

        await page.goto(
            str(url),
            wait_until=str(step.get("wait_until", "domcontentloaded")),
            timeout=int(step.get("timeout_ms", timeout)),
        )

        print(f"[GENERIC] Açılan adres: {page.url}")

    async def _wait(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
        timeout: int,
    ) -> None:
        selector = VariableEngine.resolve(step.get("selector"), context.all())

        if not selector:
            raise ValueError("wait adımında selector eksik.")

        await page.wait_for_selector(
            str(selector),
            state=str(step.get("state", "visible")),
            timeout=int(step.get("timeout_ms", timeout)),
        )

    async def _sleep(self, step: dict[str, Any]) -> None:
        milliseconds = int(step.get("milliseconds", 1000))

        if milliseconds < 0:
            raise ValueError("sleep süresi negatif olamaz.")

        await asyncio.sleep(milliseconds / 1000)

    async def _screenshot(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
    ) -> None:
        resolved_path = VariableEngine.resolve(
            step.get("path", "logs/screenshots/page.png"),
            context.all(),
        )
        screenshot_path = Path(str(resolved_path))
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)

        await page.screenshot(
            path=str(screenshot_path),
            full_page=bool(step.get("full_page", True)),
        )

        print(f"[GENERIC] Ekran görüntüsü: {screenshot_path}")

    def _assert_url(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
    ) -> None:
        expected = str(
            VariableEngine.resolve(step.get("contains", ""), context.all())
        ).strip()

        if not expected:
            raise ValueError("assert_url adımında contains eksik.")

        if expected.lower() not in page.url.lower():
            raise AssertionError(
                f"URL doğrulanamadı. Beklenen: {expected}, gerçek: {page.url}"
            )

    async def _assert_text(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
        timeout: int,
    ) -> None:
        text = str(
            VariableEngine.resolve(step.get("text", ""), context.all())
        ).strip()

        if not text:
            raise ValueError("assert_text adımında text eksik.")

        locator = page.get_by_text(text, exact=bool(step.get("exact", False)))

        await locator.first.wait_for(
            state="visible",
            timeout=int(step.get("timeout_ms", timeout)),
        )

    async def _extract_text(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
        timeout: int,
    ) -> None:
        selector = VariableEngine.resolve(step.get("selector"), context.all())

        if not selector:
            raise ValueError("extract_text adımında selector eksik.")

        locator = page.locator(str(selector)).first

        await locator.wait_for(
            state="visible",
            timeout=int(step.get("timeout_ms", timeout)),
        )

        text = (await locator.inner_text()).strip()
        label = str(
            VariableEngine.resolve(
                step.get("label", selector),
                context.all(),
            )
        )

        save_as = step.get("save_as")
        if save_as:
            context.set(str(save_as), text)

        print(f"[GENERIC] {label}: {text}")

    def _log(
        self,
        step: dict[str, Any],
        context: ExecutionContext,
    ) -> None:
        message = VariableEngine.resolve(
            str(step.get("message", "")),
            context.all(),
        )

        print(f"[GENERIC] {message}")
