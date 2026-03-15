#!/usr/bin/env python3
"""
Auto-generated test for Example Domain
Generated on: 2026-03-14 23:34:00
"""

from playwright.sync_api import sync_playwright

def test_example_com_Example_Domain():
    """Auto-generated test for Example Domain."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to page
            page.goto("https://example.com")
            page.wait_for_load_state("networkidle")
            
            # Click link (Learn more) - https://iana.org/domains/example
            page.wait_for_selector("a", state="visible")
            page.click("a")
            page.wait_for_load_state("networkidle")
            
            print("✅ Test completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_example_com_Example_Domain()
