#!/usr/bin/env python3
"""
Intelligent Test Demo - Demonstrates AI Page Understanding capabilities.

This demo shows how Qastra can understand web pages and perform
intelligent actions based on natural language instructions.
"""

import asyncio
from playwright.sync_api import sync_playwright
from qastra.ai.page_ai import (
    PageAnalyzer, ActionPlanner, DecisionEngine,
    parse_instruction, execute_goal, analyze_page
)


class IntelligentTestRunner:
    """Runs intelligent tests using AI page understanding."""
    
    def __init__(self):
        self.page_analyzer = PageAnalyzer()
        self.action_planner = ActionPlanner()
        self.decision_engine = DecisionEngine()
        self.decisions = []
    
    def run_intelligent_test(self, instruction: str, url: str = None):
        """Run an intelligent test based on natural language instruction."""
        print(f"🤖 Running Intelligent Test")
        print(f"📝 Instruction: {instruction}")
        print(f"🌐 URL: {url or 'Current page'}")
        print("=" * 50)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            
            try:
                # Navigate to URL if provided
                if url:
                    page.goto(url, wait_until="networkidle")
                    page.wait_for_timeout(2000)
                
                # Parse instruction into goal
                print("🧠 Parsing instruction...")
                action_plan = self.action_planner.parse_instruction(instruction)
                
                print(f"🎯 Goal: {action_plan.goal.goal_type.value}")
                print(f"📋 Confidence: {action_plan.goal.confidence:.2f}")
                print(f"⚙️  Parameters: {action_plan.goal.parameters}")
                
                # Analyze current page
                print("🔍 Analyzing page structure...")
                page_analysis = analyze_page(page)
                
                print(f"📄 Page Type: {page_analysis['page_type']}")
                print(f"📦 Products: {page_analysis['product_count']}")
                print(f"📝 Forms: {page_analysis['form_count']}")
                print(f"🔗 Navigation: {page_analysis['navigation_count']}")
                
                # Execute goal
                print("⚡ Executing goal...")
                decisions = self.decision_engine.execute_goal(page, action_plan.goal)
                
                # Execute decisions
                for i, decision in enumerate(decisions, 1):
                    print(f"\n--- Decision {i} ---")
                    print(f"Action: {decision.action}")
                    print(f"Confidence: {decision.confidence:.2f}")
                    print(f"Reasoning: {decision.reasoning}")
                    
                    if decision.element and decision.confidence > 0.5:
                        try:
                            # Execute the action
                            self._execute_decision(page, decision)
                            print(f"✅ Executed: {decision.action}")
                            page.wait_for_timeout(1000)
                        except Exception as e:
                            print(f"❌ Failed to execute: {e}")
                    else:
                        print(f"⏭️  Skipped (low confidence or no element)")
                
                # Store decisions
                self.decisions.extend(decisions)
                
                print(f"\n🎉 Test completed!")
                print(f"📊 Total decisions: {len(decisions)}")
                
                # Get decision summary
                summary = self.decision_engine.get_decision_summary()
                print(f"📈 Average confidence: {summary['average_confidence']:.2f}")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
            
            finally:
                browser.close()
    
    def _execute_decision(self, page, decision):
        """Execute a decision on the page."""
        action = decision.action
        element = decision.element
        params = decision.parameters
        
        if action == 'click_product' and element:
            element.click()
        
        elif action == 'fill_search' and element:
            query = params.get('query', '')
            element.fill(query)
        
        elif action == 'click_search' and element:
            element.click()
        
        elif action == 'press_enter' and element:
            element.press('Enter')
        
        elif action == 'add_to_cart' and element:
            element.click()
        
        elif action == 'checkout' and element:
            element.click()
        
        elif action == 'fill_username' and element:
            value = params.get('value', 'test@example.com')
            element.fill(value)
        
        elif action == 'fill_password' and element:
            value = params.get('value', 'password123')
            element.fill(value)
        
        elif action == 'submit_login' and element:
            element.click()
        
        elif action == 'select_for_comparison' and element:
            element.click()
        
        else:
            print(f"⚠️  Unknown action: {action}")
    
    def run_demo_sequence(self):
        """Run a sequence of demo tests."""
        demo_instructions = [
            ("Search for laptop", "https://www.amazon.com"),
            ("Find cheapest laptop", None),
            ("Find best rated laptop", None),
            ("Find Dell laptop", None),
            ("Add to cart", None),
        ]
        
        print("🚀 Starting Intelligent Test Demo Sequence")
        print("=" * 60)
        
        for i, (instruction, url) in enumerate(demo_instructions, 1):
            print(f"\n📋 Test {i}/{len(demo_instructions)}")
            self.run_intelligent_test(instruction, url)
            
            if i < len(demo_instructions):
                input("\n⏸️  Press Enter to continue to next test...")
        
        print(f"\n🎊 Demo sequence completed!")
        self.print_summary()
    
    def print_summary(self):
        """Print summary of all decisions made."""
        summary = self.decision_engine.get_decision_summary()
        
        print("\n📊 Final Summary")
        print("=" * 30)
        print(f"Total decisions: {summary['total_decisions']}")
        print(f"Average confidence: {summary['average_confidence']:.2f}")
        
        if summary['action_counts']:
            print("\n🔧 Actions performed:")
            for action, count in summary['action_counts'].items():
                print(f"  {action}: {count}")
        
        if summary['recent_decisions']:
            print("\n📝 Recent decisions:")
            for decision in summary['recent_decisions']:
                print(f"  • {decision.action} (confidence: {decision.confidence:.2f})")


def main():
    """Main function to run the demo."""
    runner = IntelligentTestRunner()
    
    print("🤖 Qastra AI Page Understanding Demo")
    print("=" * 40)
    print("This demo shows how Qastra can understand web pages")
    print("and perform intelligent actions based on natural language.")
    print()
    
    # Run demo sequence
    runner.run_demo_sequence()


if __name__ == "__main__":
    main()
