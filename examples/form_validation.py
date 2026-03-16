#!/usr/bin/env python3
"""
📋 Form Validation Testing
Comprehensive form submission and validation testing
"""

from qastra import *

@qastra
def contact_form_validation():
    """
    Test contact form with various validation scenarios
    """
    print("🚀 Testing contact form validation...")
    
    try:
        # 1. Open contact page
        open_page("https://example.com/contact")
        expect_page_title_contains("Contact")
        print("📄 Contact page opened")
        
        # 2. Test empty form submission
        click("submit")
        wait_for_element("error-message", timeout=3000)
        print("✅ Empty form validation works")
        
        # 3. Test invalid email
        type_into("name", "John Doe")
        type_into("email", "invalid-email")
        type_into("message", "Test message")
        click("submit")
        wait_for_element("email-error", timeout=3000)
        print("✅ Email validation works")
        
        # 4. Test valid submission
        type_into("email", "john.doe@example.com")
        click("submit")
        
        # 5. Verify success
        wait_for_element("success-message", timeout=5000)
        expect_page_title_contains("Thank You")
        print("✅ Valid form submission successful")
        
    except Exception as e:
        print(f"❌ Form validation test failed: {e}")
        raise

@qastra
def registration_form_validation():
    """
    Test user registration form with comprehensive validation
    """
    print("🚀 Testing registration form validation...")
    
    try:
        open_page("https://example.com/register")
        expect_page_title_contains("Register")
        
        # Test password mismatch
        type_into("username", "newuser")
        type_into("email", "user@example.com")
        type_into("password", "Password123!")
        type_into("confirm-password", "DifferentPassword!")
        click("register")
        
        wait_for_element("password-mismatch-error", timeout=3000)
        print("✅ Password mismatch validation works")
        
        # Test successful registration
        type_into("confirm-password", "Password123!")
        click("register")
        
        wait_for_element("registration-success", timeout=5000)
        expect_page_title_contains("Registration Complete")
        print("✅ Registration successful")
        
    except Exception as e:
        print(f"❌ Registration validation test failed: {e}")
        raise

if __name__ == "__main__":
    contact_form_validation()
    print("\n" + "="*50 + "\n")
    registration_form_validation()
