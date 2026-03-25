#!/usr/bin/env python3
"""
Debug Demo Test - Shows new debug logging features
"""

from qastra import *

@qastra
def debug_demo():
    print("🚀 Debug Demo Test")
    
    # Test 1: Open page with timing
    open_page("https://example.com")
    
    # Test 2: Click with debug info
    click("More information")
    
    # Test 3: Type with debug info  
    type_into("search", "test query")
    
    print("✅ Debug demo completed!")

if __name__ == "__main__":
    debug_demo()
