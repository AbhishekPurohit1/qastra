"""Qastra Demo Example - Perfect for presentations."""

from qastra import *

qastra("Qastra Demo")

print("🚀 Starting Qastra Demo...")
print("This will open a browser and navigate to example.com")

# Navigate to a simple website
open_page("https://example.com")

print("✅ Page loaded successfully!")

# Look for and click the "More information" link
click("More information")

print("✅ Successfully clicked 'More information' link!")
print("🎉 Demo completed - Qastra works!")

# You can add more steps like:
# type_into("search", "Qastra")
# click("search button")
# expect("search results")
