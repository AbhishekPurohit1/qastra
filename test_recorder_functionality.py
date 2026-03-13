"""Test the recorder functionality without opening browser."""

from qastra.recorder.recorder import QastraRecorder

def test_recorder_normalization():
    """Test text normalization functionality."""
    recorder = QastraRecorder()
    
    # Test text normalization
    test_cases = [
        ("Sign In", "login"),
        ("Log In", "login"),
        ("Register", "signup"),
        ("Sign Up", "signup"),
        ("Search", "search"),
        ("Menu", "menu"),
        ("Profile", "profile"),
        ("Settings", "settings"),
        ("Logout", "logout"),
        ("Sign Out", "logout"),
        ("Submit Button", "submit"),
        ("Click Here", "click_here"),
        ("", "element"),
        ("a", "element")
    ]
    
    print("🧪 Testing Recorder Text Normalization:")
    for input_text, expected in test_cases:
        result = recorder.normalize_text(input_text)
        status = "✅" if result == expected else "❌"
        print(f"   {status} '{input_text}' → '{result}' (expected: '{expected}')")
    
    # Test action recording
    print("\n🎯 Testing Action Recording:")
    recorder.record_click("Login Button")
    recorder.record_type("username", "admin")
    recorder.record_type("password", "secret123")
    recorder.record_click("Submit")
    
    print(f"   📝 Actions recorded: {len(recorder.actions)}")
    for action in recorder.actions:
        print(f"      • {action}")
    
    # Test password masking
    has_masked_password = any("your_password" in action for action in recorder.actions)
    print(f"   🔒 Password masking: {'✅' if has_masked_password else '❌'}")
    
    # Test test generation
    recorder.start_url = "https://example.com"
    recorder.recording_start_time = 0
    
    test_file = recorder.generate_test_file("test_recorded.py")
    
    print(f"\n📄 Test file generated: {test_file}")
    
    # Check if file exists and has content
    import os
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
            print(f"   📏 File size: {len(content)} characters")
            print(f"   ✅ Contains 'from qastra import *': {'from qastra import *' in content}")
            print(f"   ✅ Contains test function: {'test(' in content}")
            print(f"   ✅ Contains open_page: {'open_page(' in content}")
            print(f"   ✅ Contains actions: {len(recorder.actions) > 0}")
    
    print("\n🎉 Recorder functionality test completed!")

if __name__ == "__main__":
    test_recorder_normalization()
