#!/usr/bin/env python3
"""
Demo test file for testing the maintenance bot.
"""

from playwright.sync_api import sync_playwright

def test_login():
    """Test login functionality."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Navigate to a real test site
        page.goto("https://www.saucedemo.com/")
        
        # Fill login form with working selectors
        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        
        # Click login button
        page.click("#login-button")
        
        # Verify login successful
        page.wait_for_selector(".app_logo")
        
        browser.close()

def test_search():
    """Test search functionality."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Go to homepage first, then navigate to inventory
        page.goto("https://www.saucedemo.com/")
        page.fill("#user-name", "standard_user")
        page.fill("#password", "secret_sauce")
        page.click("#login-button")
        
        # Wait for inventory page to load
        page.wait_for_selector(".inventory_item")
        
        # Test sorting functionality
        page.select_option(".product_sort_container", "Name (A to Z)")
        
        # Verify products are still displayed
        page.wait_for_selector(".inventory_item")
        
        browser.close()

if __name__ == "__main__":
    test_login()
    test_search()
