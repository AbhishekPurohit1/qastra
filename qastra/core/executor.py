"""Execution engine for `.qa` test files.

This layer maps parsed QACommands to high‑level browser actions and assertions.
It intentionally depends only on the Qastra browser/action abstractions so
we can swap out the underlying automation engine later.
"""

from __future__ import annotations

from typing import Iterable, List

import os
import time
from typing import Iterable

from qastra.browser.actions import open_page, click, type_text, verify_text, close_driver
from qastra.core.parser import CommandTuple
from qastra.utils.logger import get_logger


logger = get_logger("core.executor")


def _log_step(message: str, duration: float = None) -> None:
    """Log a step with optional timing information."""
    is_debug = os.environ.get("QASTRA_DEBUG", "0") == "1"
    
    if duration:
        print(f"[STEP] {message} ({duration:.2f}s)")
        logger.info(f"Step: {message} (took {duration:.2f}s)")
    else:
        print(f"[STEP] {message}")
        logger.info(f"Step: {message}")
    
    if is_debug:
        print(f"[DEBUG] Executing: {message}")


def _log_result(status: str, details: str = None) -> None:
    """Log a result with optional details."""
    print(f"[{status.upper()}]")
    logger.info(f"Result: {status}")
    
    if details:
        is_debug = os.environ.get("QASTRA_DEBUG", "0") == "1"
        if is_debug:
            print(f"[DEBUG] Details: {details}")
        logger.debug(f"Details: {details}")


def _log_locator_attempts(attempts: list) -> None:
    """Log locator attempts in debug mode."""
    is_debug = os.environ.get("QASTRA_DEBUG", "0") == "1"
    
    if is_debug and attempts:
        print("[DEBUG] Locator attempts:")
        for i, attempt in enumerate(attempts):
            score = attempt.get('score', 0)
            element = attempt.get('element', 'unknown')
            print(f"   {i+1}. {element} (score: {score:.2f})")
        print()


def execute_commands(commands: Iterable[CommandTuple]) -> None:
    """Execute a sequence of parsed command tuples sequentially.

    Args:
        commands: Iterable of CommandTuple objects
            Each command is a tuple of:
            ("open", url: str)
            ("click", element_name: str)
            ("type", (text: str, element_name: str))
            ("verify", text: str)
            ("raw", python_code: str)

    Side Effects:
        - Opens browser if not already open
        - Executes actions in order
        - Logs each step and result
        - Closes browser on completion
    """
    commands_list: List[CommandTuple] = list(commands)
    if not commands_list:
        logger.warning("No commands to execute.")
        return

    all_passed = True
    is_debug = os.environ.get("QASTRA_DEBUG", "0") == "1"

    try:
        for i, command in enumerate(commands_list, 1):
            action, payload = command
            start_time = time.time()

            if action == "open":
                url = str(payload)
                _log_step(f"open {url}")
                open_page(url)
                duration = time.time() - start_time
                _log_step(f"Page loaded", duration)

            elif action == "click":
                element_name = str(payload)
                _log_step(f"click {element_name}")
                
                # Show locator attempts in debug mode
                if is_debug:
                    from qastra.engine.smart_locator import SmartLocator
                    locator = SmartLocator()
                    attempts = locator.debug_find_attempts(element_name)
                    _log_locator_attempts(attempts)
                
                click(element_name)
                duration = time.time() - start_time
                _log_step(f"Element clicked", duration)

            elif action == "type":
                text, element_name = payload
                _log_step(f"type '{text}' into {element_name}")
                
                # Show locator attempts in debug mode
                if is_debug:
                    from qastra.engine.smart_locator import SmartLocator
                    locator = SmartLocator()
                    attempts = locator.debug_find_attempts(element_name)
                    _log_locator_attempts(attempts)
                
                type_text(text, element_name)
                duration = time.time() - start_time
                _log_step(f"Text typed", duration)

            elif action == "verify":
                text = str(payload)
                _log_step(f"verify '{text}'")
                if not verify_text(text):
                    _log_result("FAIL", f"Text not found: {text}")
                    logger.error("Verification failed for text: %s", text)
                    all_passed = False
                    break
                else:
                    duration = time.time() - start_time
                    _log_result("PASS")
                    _log_step(f"Text verified", duration)

            elif action == "raw":
                text = str(payload)
                _log_step(f"raw '{text}'")
                if not verify_text(text):
                    _log_result("FAIL", f"Raw step failed: {text}")
                    logger.error("Raw step failed to verify text: %s", text)
                    all_passed = False
                    break
                else:
                    duration = time.time() - start_time
                    _log_result("PASS")
                    _log_step(f"Raw step completed", duration)

            else:
                logger.warning("Unsupported command action: %s", action)

    except Exception as exc:  # noqa: BLE001
        all_passed = False
        _log_result("FAIL", f"Exception: {exc}")
        logger.error("Error executing command (%s, %s): %s", action, payload, exc)

    finally:
        close_driver()

    if all_passed:
        _log_result("PASS", "All commands executed successfully")
        logger.info("All QA commands passed")
    else:
        _log_result("FAIL", "Some commands failed")
        logger.error("Some QA commands failed")


__all__ = ["execute_commands"]
