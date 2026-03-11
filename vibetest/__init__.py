"""VibeTest - AI-first browser automation framework."""

from vibetest.core.actions import open_page, click, type_into
from vibetest.core.assertions import expect, expect_page_title, expect_url, wait_for_element
from vibetest.core.testcase import test
from vibetest.core.e2e import create_e2e_test, UserJourney
from vibetest.core.cross_browser import CrossBrowser, BrowserType, cross_browser_test
from vibetest.cli.cli import cli

__all__ = [
    "open_page", "click", "type_into", "expect", "test", "cli",
    "expect_page_title", "expect_url", "wait_for_element",
    "create_e2e_test", "UserJourney", "CrossBrowser", "BrowserType", "cross_browser_test"
]
