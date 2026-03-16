"""Lightweight configuration loader for Qastra.

This provides a single place for reading environment / default settings
so higher‑level components (CLI, executors, browser engine) can remain
decoupled from concrete values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class QastraConfig:
    headless: bool = True
    default_timeout_ms: int = 10_000


def load_config() -> QastraConfig:
    """Load configuration from environment with sensible defaults."""
    headless_env = os.getenv("QASTRA_HEADLESS", "true").lower()
    headless = headless_env not in ("0", "false", "no")

    timeout_env = os.getenv("QASTRA_DEFAULT_TIMEOUT_MS")
    try:
        timeout_ms = int(timeout_env) if timeout_env is not None else 10_000
    except ValueError:
        timeout_ms = 10_000

    return QastraConfig(headless=headless, default_timeout_ms=timeout_ms)


__all__ = ["QastraConfig", "load_config"]

