#!/usr/bin/env python3
"""
Test Page AI Demo - Test the AI Page Understanding with a local HTML file.
"""

from playwright.sync_api import sync_playwright
from qastra.ai.page_ai import analyze_page, extract_products, ActionPlanner, DecisionEngine, GoalType

def test_page_ai():
    """Test the AI Page Understanding system."""
    print("🤖 Testing AI Page Understanding")
    print("=" * 40)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Load local test page
            page.goto('file:///Users/apple/Desktop/All%20Data/Qastra/test_page_ai.html')
            page.wait_for_timeout(2000)
            
            # Analyze page
            print("🔍 Analyzing page structure...")
            analysis = analyze_page(page)
            
            print(f"📄 Page Type: {analysis['page_type']}")
            print(f"📦 Products: {analysis['product_count']}")
            print(f"📝 Forms: {analysis['form_count']}")
            print(f"🔗 Navigation: {analysis['navigation_count']}")
            
            # Extract products
            print("\n🛍️  Extracting products...")
            products = extract_products(page)
            
            print(f"Found {len(products)} products:")
            for i, product in enumerate(products, 1):
                print(f"  {i}. {product.name}")
                print(f"     Brand: {product.brand}")
                print(f"     Price: ${product.price}")
                print(f"     Rating: {product.rating}")
                print()
            
            # Test action planning
            print("🧠 Testing action planning...")
            planner = ActionPlanner()
            
            test_instructions = [
                "find cheapest laptop",
                "find best rated laptop", 
                "find dell laptop",
                "add to cart"
            ]
            
            for instruction in test_instructions:
                print(f"\n📝 Instruction: {instruction}")
                action_plan = planner.parse_instruction(instruction)
                
                print(f"🎯 Goal: {action_plan.goal.goal_type.value}")
                print(f"📊 Confidence: {action_plan.goal.confidence:.2f}")
                print(f"⚙️  Parameters: {action_plan.goal.parameters}")
                
                # Execute goal
                engine = DecisionEngine()
                decisions = engine.execute_goal(page, action_plan.goal)
                
                for decision in decisions:
                    print(f"⚡ Decision: {decision.action}")
                    print(f"📈 Confidence: {decision.confidence:.2f}")
                    print(f"💭 Reasoning: {decision.reasoning}")
                    
                    # Execute if confident
                    if decision.element and decision.confidence > 0.5:
                        try:
                            if decision.action == 'click_product':
                                decision.element.click()
                                print("✅ Clicked product")
                                page.wait_for_timeout(1000)
                            elif decision.action == 'add_to_cart':
                                decision.element.click()
                                print("✅ Added to cart")
                                page.wait_for_timeout(1000)
                        except Exception as e:
                            print(f"❌ Execution failed: {e}")
            
            print("\n🎉 AI Page Understanding test completed!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_page_ai()
