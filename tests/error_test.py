"""Test error handling in VibeTest."""

from vibetest import *

test("Error Handling Test")

try:
    # This should fail gracefully
    click("nonexistent-element")
    print("❌ Should have failed!")
except Exception as e:
    print(f"✅ Error caught correctly: {e}")

try:
    # This should also fail gracefully
    type_into("nonexistent-input", "test")
    print("❌ Should have failed!")
except Exception as e:
    print(f"✅ Type error caught correctly: {e}")

print("Error handling test completed!")
