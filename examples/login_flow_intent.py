#!/usr/bin/env python3
"""
🔐 Login Flow with Intent-Based Testing
Demonstrates complete authentication workflow with error handling
"""

from qastra import *

@qastra
def login_flow_intent():
    """
    Complete login flow demonstrating intent-based automation
    with comprehensive assertions and error handling
    """
    print("🚀 Starting login flow test...")
    
    try:
        # 1. Navigate to login page
        open_page("https://example.com/login")
        print("📄 Login page opened")
        
        # 2. Verify we're on login page
        expect_page_title_contains("Login")
        wait_for_element("login-form", timeout=5000)
        print("✅ Login page verified")
        
        # 3. Fill credentials using intent
        type_into("username", "testuser@example.com")
        type_into("password", "SecurePassword123!")
        print("🔑 Credentials entered")
        
        # 4. Click login button (understands "login", "sign in", "submit")
        click("login")
        print("🔐 Login attempt made")
        
        # 5. Wait for successful login
        wait_for_element("dashboard", timeout=10000)
        expect_page_title_contains("Dashboard")
        print("✅ Login successful")
        
        # 6. Verify user is logged in
        wait_for_element("user-profile", timeout=5000)
        expect_page_url_contains("dashboard")
        print("👤 User session verified")
        
        # 7. Test user menu functionality
        click("user-profile")
        wait_for_element("logout", timeout=3000)
        print("📋 User menu accessible")
        
        # 8. Logout and verify
        click("logout")
        wait_for_element("login", timeout=5000)
        expect_page_title_contains("Login")
        print("🚪 Logout successful")
        
        print("🎉 Complete login flow test passed!")
        
    except Exception as e:
        print(f"❌ Login flow failed: {e}")
        
        # Take screenshot on failure for debugging
        try:
            take_screenshot("login_failure.png")
            print("📸 Screenshot saved: login_failure.png")
        except:
            pass
            
        raise

@qastra  
def login_with_invalid_credentials():
    """
    Test login failure scenarios with proper error handling
    """
    print("🚀 Testing invalid credentials...")
    
    try:
        open_page("https://example.com/login")
        
        # Enter invalid credentials
        type_into("username", "invalid@example.com")
        type_into("password", "WrongPassword123!")
        click("login")
        
        # Verify error message appears
        wait_for_element("error-message", timeout=5000)
        expect_page_title_contains("Login")  # Should stay on login page
        
        print("✅ Invalid credentials properly rejected")
        
    except Exception as e:
        print(f"❌ Invalid credentials test failed: {e}")
        raise

if __name__ == "__main__":
    # Run successful login flow
    login_flow_intent()
    
    print("\n" + "="*50 + "\n")
    
    # Run failure scenario
    login_with_invalid_credentials()
