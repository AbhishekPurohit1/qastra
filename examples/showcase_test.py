"""Qastra Showcase - Best in Class E2E Testing Framework."""

from qastra import *
from vibetest.core.cross_browser import BrowserType, CrossBrowser
from vibetest.core.e2e import create_e2e_test

qastra("Qastra Showcase - Complete E2E Testing")

print("🌟 Qastra - Making E2E Testing Simple & Powerful")
print("=" * 60)

# 1. Smart Locators in Action
print("\n🧠 Smart Locators:")
open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
type_into("username", "admin")  # Found by name attribute
type_into("password", "admin123")  # Found by name attribute
click("Login")  # Found by text content
print("✅ No brittle selectors needed!")

# 2. Advanced Assertions
print("\n✨ Advanced Assertions:")
from vibetest.core.assertions import wait_for_element, expect_page_title
login_button = wait_for_element("Login")
expect_page_title("OrangeHRM")
print("✅ Robust assertions with timeouts!")

# 3. Cross-Browser Testing
print("\n🌐 Cross-Browser Testing:")
cb = CrossBrowser(BrowserType.FIREFOX, headless=True)
cb.start()
open_page("https://example.com")
expect_page_title("Example Domain")
cb.stop()
print("✅ Multi-browser support!")

# 4. E2E Test Framework
print("\n🚀 E2E Test Framework:")
test_suite = create_e2e_test("Complete User Journey")
test_suite.step("Navigate to login", lambda: open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"))
test_suite.step("Fill credentials", lambda: (type_into("username", "admin"), type_into("password", "admin123")))
test_suite.step("Submit form", lambda: click("Login"))
test_suite.run_all()
print("✅ Structured E2E testing!")

# 5. Performance & Reliability
print("\n⚡ Performance Features:")
import time
start = time.time()
open_page("https://example.com")
click("More information")
duration = time.time() - start
print(f"✅ Fast execution: {duration:.2f} seconds")

print("\n" + "=" * 60)
print("🎯 Qastra Features:")
print("   🧠 Smart Locators - Find by intent, not selectors")
print("   🔄 Self-Healing - Adapts to UI changes")
print("   🌐 Cross-Browser - Chrome, Firefox, Safari, Edge")
print("   ✨ Advanced Assertions - Wait, verify, validate")
print("   🚀 E2E Framework - Structured test flows")
print("   📱 Responsive Testing - Multiple viewports")
print("   ⚡ Performance - Fast and efficient")
print("   🎯 Production Ready - Real-world tested")

print("\n🌟 Qastra - Best in Class E2E Testing Framework!")
print("🚀 Making browser automation intelligent and accessible!")
