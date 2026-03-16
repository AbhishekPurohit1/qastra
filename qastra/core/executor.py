"""Execution engine for `.qa` test files.

This layer maps parsed QACommands to high‑level browser actions and assertions.
It intentionally depends only on the Qastra browser/action abstractions so
we can swap out the underlying automation engine later.
"""

from __future__ import annotations

from typing import Iterable, List

from qastra.browser.actions import open_page, click, type_text, verify_text, close_driver
from qastra.core.parser import CommandTuple
from qastra.utils.logger import get_logger


logger = get_logger("core.executor")


def _log_step(message: str) -> None:
    print(f"[STEP] {message}")
    logger.info(message)


def execute_commands(commands: Iterable[CommandTuple]) -> None:
    """Execute a sequence of parsed command tuples sequentially.

    Each command is a tuple of:
        ("open", url: str)
        ("click", element_name: str)
        ("type", (text: str, element_name: str))
        ("verify", text: str)
        ("raw", text: str)   # best-effort verification
    """
    commands_list: List[CommandTuple] = list(commands)
    if not commands_list:
        logger.warning("No commands to execute.")
        return

    all_passed = True

    try:
        for action, payload in commands_list:
            try:
                if action == "open":
                    url = str(payload)
                    _log_step(f"open {url}")
                    open_page(url)

                elif action == "click":
                    target = str(payload)
                    _log_step(f"click {target}")
                    click(target)

                elif action == "type":
                    text, element_name = payload  # type: ignore[misc]
                    _log_step(f"type '{text}' into {element_name}")
                    type_text(text, element_name)

                elif action == "verify":
                    text = str(payload)
                    _log_step(f"verify '{text}'")
                    if not verify_text(text):
                        print("[FAIL]")
                        logger.error("Verification failed for text: %s", text)
                        all_passed = False
                        break
                    print("[PASS]")

                elif action == "raw":
                    text = str(payload)
                    _log_step(f"raw '{text}'")
                    if not verify_text(text):
                        print("[FAIL]")
                        logger.error("Raw step failed to verify text: %s", text)
                        all_passed = False
                        break
                    print("[PASS]")

                else:
                    logger.warning("Unsupported command action: %s", action)

            except Exception as exc:  # noqa: BLE001
                all_passed = False
                print("[FAIL]")
                logger.error("Error executing command (%s, %s): %s", action, payload, exc)
                break

    finally:
        close_driver()

    if all_passed:
        print("[PASS]")


__all__ = ["execute_commands"]

