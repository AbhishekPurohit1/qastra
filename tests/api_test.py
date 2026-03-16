"""
Test the Qastra API functionality.
"""

from qastra.api.test_api import test, navigate, verify


def test_api_functionality():
    """Test basic API functionality."""
    print("🧪 Testing Qastra API")
    
    # Test navigation
    result = test("open https://example.com")
    print(f"Navigation test: {result['status']}")
    
    # Test verification
    if result['status'] == 'PASS':
        verify_result = verify("Example Domain")
        print(f"Verification test: {'PASS' if verify_result else 'FAIL'}")
    
    print("✅ API test completed")


if __name__ == "__main__":
    test_api_functionality()
