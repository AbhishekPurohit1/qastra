"""Comprehensive E2E test suite - Best in class testing framework."""

from vibetest import *
from vibetest.core.e2e import create_e2e_test, UserJourney
from vibetest.core.cross_browser import cross_browser_test, BrowserType
from vibetest.core.assertions import expect, expect_page_title, expect_url, wait_for_element

# Test 1: Complete Login Journey (Multi-browser)
@cross_browser_test("Login Journey", [BrowserType.CHROME, BrowserType.FIREFOX])
def test_login_journey():
    """Complete login flow across browsers."""
    UserJourney.login_flow("admin", "admin123")
    expect_page_title("OrangeHRM")
    expect_url("dashboard")

# Test 2: E2E User Registration Flow
def test_registration_flow():
    """Complete user registration flow."""
    test = create_e2e_test("User Registration Flow")
    
    test.step("Navigate to registration page", lambda: open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"))
    test.step("Click on registration link", lambda: click("register"))
    test.step("Fill registration form", lambda: UserJourney.form_flow({
        "first_name": "John",
        "last_name": "Doe", 
        "email": "john.doe@example.com",
        "password": "SecurePass123!"
    }))
    test.step("Submit registration", lambda: click("submit"))
    test.step("Verify success message", lambda: expect("Registration successful"))
    
    test.run_all()

# Test 3: Search and Navigation Flow
def test_search_navigation():
    """Complete search and navigation flow."""
    test = create_e2e_test("Search and Navigation")
    
    test.step("Navigate to homepage", lambda: open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"))
    test.step("Login to system", lambda: UserJourney.login_flow())
    test.step("Navigate to search", lambda: UserJourney.navigation_flow())
    test.step("Perform search", lambda: UserJourney.search_flow("employee"))
    test.step("Verify search results", lambda: expect("Search Results"))
    
    test.run_all()

# Test 4: Form Validation and Error Handling
def test_form_validation():
    """Test form validation and error handling."""
    test = create_e2e_test("Form Validation")
    
    test.step("Navigate to login", lambda: open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"))
    test.step("Submit empty form", lambda: click("Login"))
    test.step("Verify error message", lambda: expect("Username cannot be empty"))
    test.step("Fill username only", lambda: type_into("username", "admin"))
    test.step("Submit incomplete form", lambda: click("Login"))
    test.step("Verify password error", lambda: expect("Password cannot be empty"))
    test.step("Fill both fields", lambda: type_into("password", "admin123"))
    test.step("Submit valid form", lambda: click("Login"))
    test.step("Verify successful login", lambda: expect_page_title("OrangeHRM"))
    
    test.run_all()

# Test 5: Advanced Element Interactions
def test_advanced_interactions():
    """Test advanced element interactions."""
    test = create_e2e_test("Advanced Interactions")
    
    test.step("Navigate to login page", lambda: open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"))
    test.step("Wait for username field", lambda: wait_for_element("username"))
    test.step("Type username with assertion", lambda: (
        type_into("username", "admin"),
        expect(wait_for_element("username")).to_have_attribute("value", "admin")
    ))
    test.step("Type password", lambda: type_into("password", "admin123"))
    test.step("Verify login button enabled", lambda: expect(wait_for_element("Login")).to_be_enabled())
    test.step("Click login button", lambda: click("Login"))
    test.step("Verify dashboard loaded", lambda: expect_url("dashboard"))
    
    test.run_all()

# Test 6: Performance and Responsiveness
def test_performance():
    """Test performance and responsiveness."""
    import time
    start_time = time.time()
    
    test = create_e2e_test("Performance Test")
    
    test.step("Load login page", lambda: open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"))
    test.step("Complete login", lambda: UserJourney.login_flow())
    test.step("Navigate to dashboard", lambda: UserJourney.navigation_flow())
    
    test.run_all()
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"\n⚡ Test completed in {duration:.2f} seconds")
    
    if duration < 10:
        print("🚀 Excellent performance!")
    elif duration < 20:
        print("✅ Good performance!")
    else:
        print("⚠️  Performance needs improvement")

# Test 7: Cross-device Simulation
def test_responsive_design():
    """Test responsive design across viewports."""
    from vibetest.browser.browser import browser
    
    test = create_e2e_test("Responsive Design Test")
    
    # Desktop view
    test.step("Set desktop viewport", lambda: browser.page.set_viewport_size({"width": 1920, "height": 1080}))
    test.step("Test desktop login", lambda: UserJourney.login_flow())
    
    # Tablet view  
    test.step("Set tablet viewport", lambda: browser.page.set_viewport_size({"width": 768, "height": 1024}))
    test.step("Test tablet navigation", lambda: UserJourney.navigation_flow())
    
    # Mobile view
    test.step("Set mobile viewport", lambda: browser.page.set_viewport_size({"width": 375, "height": 667}))
    test.step("Test mobile interactions", lambda: click("menu"))
    
    test.run_all()

if __name__ == "__main__":
    print("🌟 VibeTest - Best in Class E2E Testing Framework")
    print("=" * 70)
    
    # Run all test suites
    test_login_journey()
    test_registration_flow()
    test_search_navigation()
    test_form_validation()
    test_advanced_interactions()
    test_performance()
    test_responsive_design()
    
    print("\n" + "=" * 70)
    print("🎉 ALL E2E TESTS COMPLETED!")
    print("🚀 VibeTest - Production Ready Framework")
    print("🌐 Cross-browser | 📱 Responsive | ⚡ Performance | ✨ Advanced")
