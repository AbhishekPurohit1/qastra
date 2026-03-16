#!/usr/bin/env python3
"""
📄 Multi-Page Navigation Testing
Complex site navigation and workflow testing
"""

from qastra import *

@qastra
def multi_page_navigation():
    """
    Test navigation across multiple pages with state preservation
    """
    print("🚀 Testing multi-page navigation...")
    
    try:
        # 1. Start at homepage
        open_page("https://example.com")
        expect_page_title_contains("Home")
        print("🏠 Homepage loaded")
        
        # 2. Navigate to products
        click("products")
        wait_for_element("product-list", timeout=5000)
        expect_page_title_contains("Products")
        print("📦 Products page loaded")
        
        # 3. Filter products
        type_into("search", "laptop")
        click("search-button")
        wait_for_element("search-results", timeout=3000)
        print("🔍 Product search working")
        
        # 4. Select first product
        click("product-item")
        wait_for_element("product-details", timeout=5000)
        expect_page_title_contains("Product Details")
        print("📋 Product details loaded")
        
        # 5. Add to cart
        click("add-to-cart")
        wait_for_element("cart-notification", timeout=3000)
        print("🛒 Item added to cart")
        
        # 6. Navigate to cart
        click("cart-icon")
        wait_for_element("cart-items", timeout=5000)
        expect_page_title_contains("Shopping Cart")
        print("🛍️ Cart page loaded")
        
        # 7. Verify cart contents
        expect_page_contains("laptop")
        print("✅ Cart contents verified")
        
        # 8. Navigate to checkout
        click("checkout")
        wait_for_element("checkout-form", timeout=5000)
        expect_page_title_contains("Checkout")
        print("💳 Checkout page loaded")
        
        # 9. Fill shipping info
        type_into("first-name", "John")
        type_into("last-name", "Doe")
        type_into("address", "123 Main St")
        type_into("city", "New York")
        type_into("zip-code", "10001")
        click("continue-to-payment")
        print("📝 Shipping information entered")
        
        # 10. Verify payment page
        wait_for_element("payment-form", timeout=5000)
        expect_page_title_contains("Payment")
        print("💰 Payment page loaded")
        
        print("🎉 Multi-page navigation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Multi-page navigation test failed: {e}")
        raise

@qastra
def breadcrumb_navigation():
    """
    Test breadcrumb navigation and back/forward functionality
    """
    print("🚀 Testing breadcrumb navigation...")
    
    try:
        open_page("https://example.com")
        
        # Navigate deep into site
        click("products")
        click("electronics")
        click("laptops")
        click("gaming-laptops")
        
        # Verify breadcrumbs
        expect_page_contains("Home > Products > Electronics > Laptops > Gaming Laptops")
        print("🧭 Breadcrumbs working correctly")
        
        # Test breadcrumb navigation
        click("breadcrumb-electronics")
        expect_page_title_contains("Electronics")
        print("🔙 Breadcrumb navigation working")
        
        # Test browser back/forward
        browser_go_back()
        expect_page_title_contains("Gaming Laptops")
        print("⏮️ Browser back working")
        
        browser_go_forward()
        expect_page_title_contains("Electronics")
        print("⏭️ Browser forward working")
        
    except Exception as e:
        print(f"❌ Breadcrumb navigation test failed: {e}")
        raise

if __name__ == "__main__":
    multi_page_navigation()
    print("\n" + "="*50 + "\n")
    breadcrumb_navigation()
