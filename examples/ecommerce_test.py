#!/usr/bin/env python3
"""
🛒 E-commerce Test Example
Test common online shopping scenarios
"""

from qastra import *

@qastra
def ecommerce_test():
    """
    Test a typical e-commerce workflow
    """
    print("🚀 Testing e-commerce flow...")
    
    # 1. Open shop homepage
    open_page("https://shop.example.com")
    
    # 2. Search for a product
    type_into("search", "laptop")
    click("search")
    
    # 3. Select first product
    click("product")
    
    # 4. Add to cart
    click("add to cart")
    
    # 5. View cart
    click("cart")
    
    # 6. Proceed to checkout
    click("checkout")
    
    # 7. Fill shipping info
    type_into("name", "John Doe")
    type_into("address", "123 Main St")
    type_into("city", "New York")
    
    # 8. Continue
    click("continue")
    
    # 9. Verify we're on payment page
    expect_page_title_contains("Payment")
    
    print("✅ E-commerce test passed!")
    print("🛒 Shopping workflow working correctly!")

if __name__ == "__main__":
    ecommerce_test()
