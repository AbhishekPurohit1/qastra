#!/usr/bin/env python3
"""
Real-world demo tests for popular websites.

This file demonstrates Qastra working with real websites
to show practical usage of the framework.
"""

from qastra.api.test_api import test, navigate, click, fill, verify, wait


def test_github_search():
    """Test GitHub search functionality."""
    print("🧪 Testing GitHub Search")
    
    test("open https://github.com")
    wait(2000)  # Wait for page to load
    
    test("fill search input with qastra")
    test("click search button")
    wait(2000)
    
    test("verify qastra repository")
    test("click first result")
    wait(2000)
    
    test("verify repository page")
    print("✅ GitHub search test completed")


def test_amazon_search():
    """Test Amazon search functionality."""
    print("🧪 Testing Amazon Search")
    
    test("open https://amazon.com")
    wait(3000)  # Amazon takes time to load
    
    test("fill search box with laptop")
    test("click search button")
    wait(3000)
    
    test("verify search results")
    test("click first product")
    wait(2000)
    
    test("verify product details")
    print("✅ Amazon search test completed")


def test_stackoverflow_login():
    """Test Stack Overflow login flow."""
    print("🧪 Testing Stack Overflow Login")
    
    test("open https://stackoverflow.com")
    wait(2000)
    
    test("click login button")
    wait(2000)
    
    # Note: Don't use real credentials in demo
    test("fill email with demo@example.com")
    test("fill password with demopassword")
    
    # Just verify the form is filled, don't actually login
    verify("email")
    verify("password")
    
    print("✅ Stack Overflow login test completed")


def test_youtube_search():
    """Test YouTube search functionality."""
    print("🧪 Testing YouTube Search")
    
    test("open https://youtube.com")
    wait(2000)
    
    test("fill search box with python tutorial")
    test("click search button")
    wait(2000)
    
    test("verify search results")
    test("click first video")
    wait(3000)
    
    test("verify video player")
    print("✅ YouTube search test completed")


def test_reddit_browsing():
    """Test Reddit browsing."""
    print("🧪 Testing Reddit Browsing")
    
    test("open https://reddit.com")
    wait(2000)
    
    test("verify reddit homepage")
    test("click programming subreddit")
    wait(2000)
    
    test("verify programming posts")
    test("click first post")
    wait(2000)
    
    test("verify post details")
    print("✅ Reddit browsing test completed")


def test_linkedin_profile():
    """Test LinkedIn profile viewing."""
    print("🧪 Testing LinkedIn Profile")
    
    test("open https://linkedin.com")
    wait(3000)  # LinkedIn takes time to load
    
    # Just verify the page loads without login
    verify("LinkedIn")
    verify("Join now")
    
    print("✅ LinkedIn profile test completed")


def test_medium_article():
    """Test Medium article reading."""
    print("🧪 Testing Medium Article")
    
    test("open https://medium.com")
    wait(2000)
    
    test("verify medium homepage")
    test("click first article")
    wait(2000)
    
    test("verify article content")
    print("✅ Medium article test completed")


def run_all_real_world_tests():
    """Run all real-world demo tests."""
    print("🚀 Starting Real-World Demo Tests")
    print("=" * 50)
    
    tests = [
        test_github_search,
        test_amazon_search,
        test_stackoverflow_login,
        test_youtube_search,
        test_reddit_browsing,
        test_linkedin_profile,
        test_medium_article
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")
            failed += 1
            print()
    
    print("=" * 50)
    print("📊 Real-World Test Summary")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    print(f"Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    return passed, failed


if __name__ == "__main__":
    run_all_real_world_tests()
