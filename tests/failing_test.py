"""Failing test to demonstrate error reporting."""

from qastra import *

qastra("Failing Test Example")

print("🚀 Running a test that will fail...")

# This will fail because the element doesn't exist
try:
    click("nonexistent_button_that_cannot_be_found")
    print("❌ This should have failed!")
except Exception as e:
    print(f"✅ Expected failure: {e}")
    raise Exception("This is a deliberate test failure for demonstration")
