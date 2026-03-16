"""Execution engine for `.qa` test files.

This layer maps parsed QACommands to high‑level browser actions and assertions.
It intentionally depends only on the Qastra browser/action abstractions so
we can swap out the underlying automation engine later.
"""

from __future__ import annotations

from typing import List

from qastra.browser.actions import open_page, click, type_into
from qastra.browser.driver import driver
from qastra.core.parser import QACommand
from qastra.core.assertions import expect
from qastra.utils.logger import get_logger


logger = get_logger("core.executor")


def execute_commands(commands: List[QACommand]) -> None:
    """Execute a list of QACommand objects sequentially."""
    if not commands:
        logger.warning("No commands to execute.")
        return

    driver.start()
    try:
        for cmd in commands:
            logger.info("Executing command: %s", cmd)

            if cmd.action == "open" and cmd.target:
                print(f"➡️  open {cmd.target}")
                open_page(cmd.target)

            elif cmd.action == "click" and cmd.target:
                print(f"🖱️  click \"{cmd.target}\"")
                click(cmd.target)

            elif cmd.action == "type" and cmd.target and cmd.value is not None:
                print(f"⌨️  type \"{cmd.value}\" into \"{cmd.target}\"")
                type_into(cmd.target, cmd.value)

            elif cmd.action == "verify" and cmd.target:
                print(f"🔍 verify \"{cmd.target}\"")
                expect(cmd.target)  # string mode checks presence in page content

            elif cmd.action == "raw" and cmd.target:
                # For now, treat unknown lines as a simple verification.
                print(f"🔹 raw step: {cmd.target}")
                expect(cmd.target)

            else:
                logger.warning("Unsupported command: %s", cmd)

    finally:
        driver.stop()


__all__ = ["execute_commands"]

