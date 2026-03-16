"""Failing test to demonstrate error reporting.

This test is intentionally marked xfail so it demonstrates a failure scenario
without breaking test collection for the rest of the suite.
"""

import pytest

from qastra import click, qastra


@pytest.mark.xfail(reason="Deliberate failure for demonstration")
def test_deliberate_failure_demo():
    qastra("Failing Test Example")
    print("🚀 Running a test that will fail...")
    click("nonexistent_button_that_cannot_be_found")
