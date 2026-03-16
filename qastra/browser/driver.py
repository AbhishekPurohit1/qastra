"""Browser driver abstraction for Qastra.

Today this is a thin wrapper around the existing Playwright‑based browser,
but higher layers should depend on this module rather than Playwright
directly so we can swap the underlying engine in the future.
"""

from __future__ import annotations

from typing import Any, Optional

from .browser import browser as _playwright_browser


class BrowserDriver:
    """High‑level browser driver interface used by the action engine."""

    def __init__(self) -> None:
        # For now we delegate to the existing global Browser instance.
        self._impl = _playwright_browser

    @property
    def page(self):
        return self._impl.page

    def start(self, options: Optional[dict[str, Any]] = None) -> None:
        self._impl.start(options)

    def stop(self) -> None:
        self._impl.stop()

    def open(self, url: str) -> None:
        self._impl.open(url)

    def click_element(self, element: Any) -> None:
        self._impl.click(element)

    def type_into(self, element: Any, value: str) -> None:
        self._impl.type(element, value)

    def screenshot(self, name: str = "failure.png") -> None:
        self._impl.screenshot(name)


# Single shared driver instance for now.
driver = BrowserDriver()


__all__ = ["BrowserDriver", "driver"]

