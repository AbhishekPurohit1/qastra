"""Central logging utilities for Qastra.

All internal modules should use this logger instead of configuring logging
individually. This makes it easier to route logs to files / HTML reports later.
"""

from __future__ import annotations

import logging
from typing import Optional


_LOGGER_NAME = "qastra"


def _configure_root_logger(level: int = logging.INFO) -> None:
    """Configure the shared Qastra logger once."""
    logger = logging.getLogger(_LOGGER_NAME)

    if logger.handlers:
        return

    logger.setLevel(level)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module‑scoped logger under the shared Qastra root."""
    _configure_root_logger()
    if name is None:
        return logging.getLogger(_LOGGER_NAME)
    return logging.getLogger(f"{_LOGGER_NAME}.{name}")


__all__ = ["get_logger"]

