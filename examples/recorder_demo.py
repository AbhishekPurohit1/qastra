"""Qastra Recorder Demo - Show how to turn manual actions into automated tests."""

from qastra import *

qastra("Recorder Demo")

print("🎬 Qastra Recorder Demo")
print("=" * 50)

print("\n📋 What the Recorder Does:")
print("   1. Opens a browser at specified URL")
print("   2. Captures your clicks and typing")
print("   3. Converts actions to Qastra code")
print("   4. Generates a complete test file")

print("\n🎯 Example Usage:")
print("   qastra record https://example.com")
print("   qastra record https://example.com --duration 120")
print("   qastra record https://example.com --output my_test.py")

print("\n⌨️  Actions Captured:")
print("   ✅ Clicks on buttons, links, elements")
print("   ✅ Typing in input fields, textareas")
print("   ✅ Form submissions")
print("   ✅ Page navigation")

print("\n🧠 Smart Features:")
print("   🔄 Text normalization (sign in → login)")
print("   🔒 Password masking for security")
print("   📝 Clean intent-based identifiers")
print("   🎯 Element deduplication")

print("\n📝 Generated Test Example:")
print("""
from qastra import *

qastra("Recorded Test")

open_page("https://example.com")

click("login")
type_into("username", "admin")
type_into("password", "your_password")
click("submit")

print("✅ Recorded test executed successfully!")
""")

print("\n🚀 Interactive Workflow:")
print("   1. Run: vibetest record https://example.com")
print("   2. Browser opens automatically")
print("   3. Click around, type in forms")
print("   4. Browser closes after timeout")
print("   5. Test file appears: recorded_test.py")
print("   6. Run: python recorded_test.py")

print("\n🎯 Real-World Benefits:")
print("   📚 Rapid test creation")
print("   🔄 No manual test writing")
print("   🧠 AI-powered element identification")
print("   ⚡ Instant test generation")
print("   🎪 Perfect for demos and prototypes")

print("\n🌟 Recorder + Smart Locators:")
print("   📝 Recorder: click('Sign In Button')")
print("   🧠 Smart Locator: finds element by intent")
print("   ✅ Result: Robust, maintainable tests")

print("\n📋 CLI Options:")
print("   --duration 60    # Recording time in seconds")
print("   --output test.py # Output filename")
print("   --help          # Show all options")

print("\n🎪 Demo Scenario:")
print("   1. vibetest record https://opensource-demo.orangehrmlive.com")
print("   2. Click login button")
print("   3. Type username and password")
print("   4. Click submit")
print("   5. Navigate to dashboard")
print("   6. Browser closes")
print("   7. Open recorded_test.py")
print("   8. Run: python recorded_test.py")

print("\n🎉 Result: Complete automated test from manual actions!")

print("\n" + "=" * 50)
print("🚀 Ready to try the recorder?")
print("💡 Run: vibetest record https://example.com")
print("🎯 Watch your manual actions become automated tests!")
