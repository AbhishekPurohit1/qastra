"""Auto-generated test by Qastra Recorder
Generated on: 2026-03-13 09:41:32
URL: https://example.com
"""

from qastra import *

qastra("Recorded Test")

# Navigate to starting page
open_page("https://example.com")

click("login")
type_into("username", "admin")
type_into("password", "your_password")
click("submit")

# Test completed successfully!
print("✅ Recorded test executed successfully!")
