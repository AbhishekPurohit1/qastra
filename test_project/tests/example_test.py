#!/usr/bin/env python3
"""
Example Qastra test
"""

from playwright.sync_api import sync_playwright

def test_example():
    """Example test using Qastra self-healing locators."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to a website
            page.goto("https://example.com")
            page.wait_for_load_state("networkidle")
            
            # Click a link (Qastra will heal if locator fails)
            page.click("text=More information")
            
            # Wait for navigation
            page.wait_for_load_state("networkidle")
            
            print("✅ Test completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_example()
