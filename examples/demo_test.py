"""VibeTest Demo Example - Perfect for presentations."""

from vibetest import *

test("VibeTest Demo")

print("🚀 Starting VibeTest Demo...")
print("This will open a browser and navigate to example.com")

# Navigate to a simple website
open_page("https://example.com")

print("✅ Page loaded successfully!")

# Look for and click the "More information" link
click("More information")

print("✅ Successfully clicked 'More information' link!")
print("🎉 Demo completed - VibeTest works!")

# You can add more steps like:
# type_into("search", "VibeTest")
# click("search button")
# expect("search results")
