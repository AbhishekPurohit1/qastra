#!/usr/bin/env python3
"""
🔐 Simple Login Test Example
Perfect for testing authentication flows
"""

from qastra import *

@qastra
def simple_login_test():
    """
    Test a typical login flow - easy to customize!
    """
    print("🚀 Testing login flow...")
    
    # 1. Open login page
    open_page("https://example.com/login")
    
    # 2. Enter credentials
    type_into("username", "testuser")
    type_into("password", "testpass")
    
    # 3. Click login button
    click("login")
    
    # 4. Wait for dashboard to load
    wait_for_element("dashboard", timeout=5000)
    
    # 5. Verify we're logged in
    expect_page_title_contains("Dashboard")
    
    print("✅ Login test passed!")
    print("🎯 User successfully logged in!")

if __name__ == "__main__":
    simple_login_test()
