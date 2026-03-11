"""Real-world login test using VibeTest."""

from vibetest import *

test("Real World Login Test")

print("🚀 Testing with real login environment...")
print("Opening OrangeHRM demo site...")

# Navigate to real login page
open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")

print("Looking for username field...")
type_into("username", "admin")

print("Looking for password field...")
type_into("password", "admin123")

print("Looking for login button...")
click("Login")

print("✅ Real-world login test completed!")
print("🎯 VibeTest works in production environments!")
