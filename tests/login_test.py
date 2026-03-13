"""Example login test using Qastra DSL."""

from qastra import *

qastra("Login Flow Test")

print("Opening example.com...")
open_page("https://example.com")

print("Looking for 'More information' link...")
click("More information")

print("Test completed successfully!")
