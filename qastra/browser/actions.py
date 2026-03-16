"""Selenium-based browser engine for Qastra.

This module defines the primary browser actions used by higher layers:

    open_page(url)
    click(element_name)
    type_text(text, element_name)
    verify_text(text)

It also provides thin compatibility wrappers (`type_into`) so existing
callers continue to work while the underlying engine can be swapped later.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass
class SeleniumConfig:
    headless: bool = True


_driver: Optional[WebDriver] = None


def _build_driver(config: SeleniumConfig) -> WebDriver:
    """Create a Selenium WebDriver instance (Chrome by default)."""
    from selenium.webdriver.chrome.options import Options

    options = Options()
    if config.headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    return webdriver.Chrome(options=options)


def get_driver() -> WebDriver:
    """Return a shared WebDriver instance (created on first use)."""
    if get_driver._driver is None:  # type: ignore[attr-defined]
        get_driver._driver = _build_driver(SeleniumConfig(headless=True))  # type: ignore[attr-defined]
    return get_driver._driver  # type: ignore[attr-defined]


# attach storage attribute to the function
get_driver._driver = _driver  # type: ignore[attr-defined]


def close_driver() -> None:
    """Close and dispose of the shared WebDriver instance."""
    driver = get_driver._driver  # type: ignore[attr-defined]
    if driver is not None:
        with contextlib.suppress(Exception):
            driver.quit()
    get_driver._driver = None  # type: ignore[attr-defined]


def _find_element_smart(name: str):
    """Best-effort smart locator using multiple strategies."""
    driver = get_driver()
    # 1) Visible text (buttons, links, generic elements)
    xpath_candidates = [
        f"//*[normalize-space(text())='{name}']",
        f"//button[normalize-space(text())='{name}']",
        f"//a[normalize-space(text())='{name}']",
    ]
    for xp in xpath_candidates:
        with contextlib.suppress(Exception):
            elem = driver.find_element(By.XPATH, xp)
            if elem:
                return elem

    # 2) aria-label
    with contextlib.suppress(Exception):
        elem = driver.find_element(By.CSS_SELECTOR, f"[aria-label='{name}']")
        if elem:
            return elem

    # 3) placeholder
    with contextlib.suppress(Exception):
        elem = driver.find_element(By.CSS_SELECTOR, f"[placeholder='{name}']")
        if elem:
            return elem

    # 4) button text (partial match)
    with contextlib.suppress(Exception):
        elem = driver.find_element(
            By.XPATH,
            f"//button[contains(normalize-space(text()), '{name}')]",
        )
        if elem:
            return elem

    raise ValueError(f"Element not found for description: {name}")


def open_page(url: str) -> None:
    """Open a URL in the browser."""
    driver = get_driver()
    driver.get(url)


def click(element_name: str) -> None:
    """Click an element identified by a human-friendly name."""
    elem = _find_element_smart(element_name)
    elem.click()


def type_text(text: str, element_name: str) -> None:
    """Type text into an element identified by a human-friendly name."""
    elem = _find_element_smart(element_name)
    elem.clear()
    elem.send_keys(text)


def verify_text(text: str) -> bool:
    """Verify that the given text is present somewhere in the page."""
    driver = get_driver()
    return text in driver.page_source


# Backwards-compatible alias used by some internal code paths
def type_into(label: str, value: str) -> None:
    """Compatibility wrapper: type_into(label, value) -> type_text(value, label)."""
    type_text(value, label)


__all__ = [
    "open_page",
    "click",
    "type_text",
    "verify_text",
    "type_into",
    "get_driver",
    "close_driver",
]

