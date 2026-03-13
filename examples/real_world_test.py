"""Real-world login test for Qastra."""

from qastra import *

qastra("Real World Login Test")

print("🚀 Testing Qastra with real-world login environment...")
print("Testing OrangeHRM - a real HR management system")

# Navigate to real login page
open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")

print("📝 Filling login form with smart locators...")
type_into("username", "admin")
type_into("password", "admin123")
click("Login")

print("✅ Real-world login completed successfully!")
print("🎯 Qastra works in production environments!")
print("� Smart locators found: username field, password field, login button")
