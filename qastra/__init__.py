"""Qastra - AI-first browser automation framework."""

from qastra.core.actions import open_page, click, type_into
from qastra.core.assertions import expect, expect_page_title, expect_url, wait_for_element
from qastra.core.testcase import qastra
from qastra.core.e2e import create_e2e_test, UserJourney
from qastra.core.cross_browser import CrossBrowser, BrowserType, cross_browser_test
from qastra.recorder.recorder import start_recorder, record_interactive
from qastra.cli.cli import cli

__all__ = [
    "open_page", "click", "type_into", "expect", "qastra", "cli",
    "expect_page_title", "expect_url", "wait_for_element",
    "create_e2e_test", "UserJourney", "CrossBrowser", "BrowserType", "cross_browser_test",
    "start_recorder", "record_interactive"
]
