#!/usr/bin/env python3
"""
🎯 Beginner-Friendly Qastra Test
Perfect for first-time users!
"""

from qastra import *

@qastra
def beginner_test():
    """
    Your first Qastra test - easy to understand!
    """
    print("🚀 Starting beginner test...")
    
    # 1. Open a simple website
    open_page("https://example.com")
    
    # 2. Wait a moment to see it load
    import time
    time.sleep(2)
    
    # 3. Look for a link and click it
    # Qastra is smart - it finds "More information" even without exact text
    click("More information")
    
    # 4. Wait to see the result
    time.sleep(2)
    
    # 5. Check that we're on the right page
    expect_page_title_contains("Example")
    
    print("✅ Test completed successfully!")
    print("🎉 Congratulations on your first Qastra test!")

if __name__ == "__main__":
    beginner_test()
