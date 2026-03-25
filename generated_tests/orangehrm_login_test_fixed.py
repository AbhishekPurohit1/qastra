#!/usr/bin/env python3
"""
Auto-generated form test for OrangeHRM
Generated on: 2026-03-25 09:52:12
"""

from playwright.sync_api import sync_playwright

def test_orangehrm_login_test_fixed():
    """Auto-generated form test for OrangeHRM."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to page
            page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
            page.wait_for_load_state("networkidle")
            
            # Fill form
            # Fill text input (username) - Username
            page.fill(".oxd-input", "testuser")
            # Fill password input (password) - Password
            page.fill(".oxd-input", "TestPassword123")
            # Submit form
            page.wait_for_selector(".oxd-button", state="visible")
            page.click(".oxd-button")
            page.wait_for_load_state("networkidle")

            # Submit button (Login)
            page.wait_for_selector(".oxd-button", state="visible")
            page.click(".oxd-button")
            page.wait_for_load_state("networkidle")
            # Click link (OrangeHRM, Inc) - http://www.orangehrm.com
            page.wait_for_selector("a", state="visible")
            page.click("a")
            page.wait_for_load_state("networkidle")
            
            print("✅ Form test completed successfully!")
            
        except Exception as e:
            print(f"❌ Form test failed: {e}")
            raise
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_orangehrm_login_test_fixed()
