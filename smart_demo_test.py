#!/usr/bin/env python3
"""
Smart Locator Demo Test - Shows the power of intent-based automation.
"""

from playwright.sync_api import sync_playwright
from qastra.engine.action_wrapper import click, fill, get_action_wrapper


def test_smart_locator_demo():
    """Demo test showing smart locator capabilities."""
    
    print("🚀 Smart Locator Demo Test")
    print("=" * 50)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to OrangeHRM login page
            page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
            page.wait_for_load_state("networkidle")
            
            print("📍 Navigated to OrangeHRM login page")
            
            # Use smart locator to fill username
            print("\n🔍 Trying to find username field...")
            result = fill(page, "username", "Admin")
            
            # Use smart locator to fill password
            print("\n🔍 Trying to find password field...")
            result = fill(page, "password", "admin123")
            
            # Use smart locator to click login button
            print("\n🔍 Trying to find login button...")
            result = click(page, "login")
            
            # Wait for dashboard to load
            page.wait_for_timeout(3000)
            
            # Try some dashboard interactions
            print("\n🔍 Trying to find menu items...")
            
            # Try to click on different menu items
            menu_items = ["admin", "user", "directory", "configuration"]
            
            for item in menu_items:
                result = click(page, item)
                if result['status'] == 'success':
                    print(f"✅ Successfully clicked {item}")
                    page.wait_for_timeout(1000)
                else:
                    print(f"❌ Could not find {item}")
            
            # Print action summary
            wrapper = get_action_wrapper()
            wrapper.print_action_summary()
            
            print("\n✅ Smart Locator Demo Completed!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            raise
        
        finally:
            browser.close()


def test_intent_explanation():
    """Test the intent explanation feature."""
    
    print("\n🧠 Intent Explanation Test")
    print("=" * 50)
    
    from qastra.engine.smart_locator import SmartLocator
    from qastra.engine.element_scanner import ElementScanner
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
            page.wait_for_load_state("networkidle")
            
            locator = SmartLocator()
            scanner = ElementScanner()
            
            # Test different intents
            test_intents = ["username", "password", "login", "signin", "submit"]
            
            for intent in test_intents:
                print(f"\n🔍 Testing intent: '{intent}'")
                
                element, match_info = locator.find_element(page, intent)
                
                if element:
                    features = scanner.get_element_features(element)
                    explanation = locator.explain_match(intent, features)
                    print(f"✅ Found element with confidence {match_info.get('confidence', 'unknown')}")
                    print(f"Explanation:\n{explanation}")
                else:
                    print(f"❌ No element found for '{intent}'")
        
        finally:
            browser.close()


if __name__ == "__main__":
    # Run the demo
    test_smart_locator_demo()
    test_intent_explanation()
