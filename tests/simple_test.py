"""
Simple test file to demonstrate the test runner.
"""

from qastra.api.test_api import test, navigate, verify


def test_basic_navigation():
    """Test basic navigation functionality."""
    test("open https://example.com")
    verify("Example Domain")


def test_search_functionality():
    """Test search functionality."""
    test("open https://github.com")
    test("fill search input with qastra")
    test("click search button")
    verify("qastra")


if __name__ == "__main__":
    test_basic_navigation()
    test_search_functionality()
    print("✅ All tests passed!")
