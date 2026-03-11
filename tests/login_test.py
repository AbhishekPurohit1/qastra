"""Example login test using VibeTest DSL."""

from vibetest import *

test("Login Flow Test")

print("Opening example.com...")
open_page("https://example.com")

print("Looking for 'More information' link...")
click("More information")

print("Test completed successfully!")
