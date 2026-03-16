"""High‑level browser actions.

These wrap the core action helpers so test execution code can import from
`qastra.browser.actions` while we keep the implementation in one place.
"""

from __future__ import annotations

from qastra.core.actions import open_page, click, type_into

__all__ = ["open_page", "click", "type_into"]

