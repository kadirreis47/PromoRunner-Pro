from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from playwright.async_api import (
    Page,
    TimeoutError as PlaywrightTimeoutError,
)

from engine.context import ExecutionContext
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
            for index, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    raise ValueError(f"{index}. adım geçerli bir nesne değil.")

                action = str(step.get("action", "")).strip().lower()
                print(f"[GENERIC] Adım {index}/{len(steps)}: {action}")

                await self._execute_step(
                    page=page,
                    step=step,
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

    async def _execute_step(
        self,
        page: Page,
        step: dict[str, Any],
        context: ExecutionContext,
        timeout: int,
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
        else:
            raise ValueError(f"Desteklenmeyen action: {action}")

    async def _goto(self, page: Page, step: dict[str, Any], context: ExecutionContext, timeout: int) -> None:
        url = VariableEngine.resolve(step.get("url"), context.all())
        if not url:
            raise ValueError("goto adımında url eksik.")
        await page.goto(
            str(url),
            wait_until=str(step.get("wait_until", "domcontentloaded")),
            timeout=int(step.get("timeout_ms", timeout)),
        )
        print(f"[GENERIC] Açılan adres: {page.url}")

    async def _wait(self, page: Page, step: dict[str, Any], context: ExecutionContext, timeout: int) -> None:
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

    async def _screenshot(self, page: Page, step: dict[str, Any], context: ExecutionContext) -> None:
        resolved_path = VariableEngine.resolve(step.get("path", "logs/screenshots/page.png"), context.all())
        screenshot_path = Path(str(resolved_path))
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(screenshot_path), full_page=bool(step.get("full_page", True)))
        print(f"[GENERIC] Ekran görüntüsü: {screenshot_path}")

    def _assert_url(self, page: Page, step: dict[str, Any], context: ExecutionContext) -> None:
        expected = str(VariableEngine.resolve(step.get("contains", ""), context.all())).strip()
        if not expected:
            raise ValueError("assert_url adımında contains eksik.")
        if expected.lower() not in page.url.lower():
            raise AssertionError(f"URL doğrulanamadı. Beklenen: {expected}, gerçek: {page.url}")

    async def _assert_text(self, page: Page, step: dict[str, Any], context: ExecutionContext, timeout: int) -> None:
        text = str(VariableEngine.resolve(step.get("text", ""), context.all())).strip()
        if not text:
            raise ValueError("assert_text adımında text eksik.")
        locator = page.get_by_text(text, exact=bool(step.get("exact", False)))
        await locator.first.wait_for(state="visible", timeout=int(step.get("timeout_ms", timeout)))

    async def _extract_text(self, page: Page, step: dict[str, Any], context: ExecutionContext, timeout: int) -> None:
        selector = VariableEngine.resolve(step.get("selector"), context.all())
        if not selector:
            raise ValueError("extract_text adımında selector eksik.")
        locator = page.locator(str(selector)).first
        await locator.wait_for(state="visible", timeout=int(step.get("timeout_ms", timeout)))
        text = (await locator.inner_text()).strip()
        label = str(VariableEngine.resolve(step.get("label", selector), context.all()))
        save_as = step.get("save_as")
        if save_as:
            context.set(str(save_as), text)
        print(f"[GENERIC] {label}: {text}")

    def _log(self, step: dict[str, Any], context: ExecutionContext) -> None:
        message = VariableEngine.resolve(str(step.get("message", "")), context.all())
        print(f"[GENERIC] {message}")
