#!/usr/bin/env python3
"""
Orange HRM Test - Testing Qastra with Orange HRM website
"""

from qastra import *

@qastra
def orange_hrm_test():
    print("🚀 Starting Orange HRM test...")

    # Open Orange HRM demo site
    open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")

    print("📄 Orange HRM login page opened")

    # Wait for page to load
    wait_for_element("username", timeout=5000)

    # Enter login credentials
    type_into("username", "Admin")
    type_into("password", "admin123")

    print("🔑 Credentials entered")

    # Click login button
    click("login")

    print("🔐 Login button clicked")

    # Wait for dashboard to load
    wait_for_element("dashboard", timeout=10000)

    print("📊 Dashboard loaded successfully")

    # Verify we're on the dashboard
    expect_page_title_contains("OrangeHRM")

    print("✅ Test completed successfully!")

    # Close browser after a short delay to see results
    import time
    time.sleep(2)

# Run the test
if __name__ == "__main__":
    orange_hrm_test()
