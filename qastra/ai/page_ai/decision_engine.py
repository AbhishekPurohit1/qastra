"""
Decision Engine - Makes intelligent decisions based on page analysis and goals.
"""

import re
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from playwright.sync_api import Page, ElementHandle

from .page_analyzer import Product, Form, NavigationItem, extract_products, analyze_page
from .action_planner import ActionPlan, Goal, GoalType, ActionType


@dataclass
class Decision:
    """Represents a decision made by the engine."""
    action: str
    element: Optional[ElementHandle]
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str


class DecisionEngine:
    """Makes intelligent decisions about page interactions."""
    
    def __init__(self):
        self.decision_history = []
        
        # Decision weights for different factors
        self.weights = {
            'price': 0.4,
            'rating': 0.3,
            'brand': 0.2,
            'availability': 0.1
        }
    
    def execute_goal(self, page: Page, goal: Goal) -> List[Decision]:
        """
        Execute a goal and return the decisions made.
        
        Args:
            page: Playwright page object
            goal: Goal to achieve
            
        Returns:
            List of decisions made
        """
        decisions = []
        
        try:
            if goal.goal_type == GoalType.FIND_CHEAPEST:
                decisions = self._find_cheapest_product(page, goal)
            
            elif goal.goal_type == GoalType.FIND_MOST_EXPENSIVE:
                decisions = self._find_most_expensive_product(page, goal)
            
            elif goal.goal_type == GoalType.FIND_BEST_RATED:
                decisions = self._find_best_rated_product(page, goal)
            
            elif goal.goal_type == GoalType.FIND_SPECIFIC_BRAND:
                decisions = self._find_specific_brand_product(page, goal)
            
            elif goal.goal_type == GoalType.SEARCH_FOR_ITEM:
                decisions = self._search_for_item(page, goal)
            
            elif goal.goal_type == GoalType.ADD_TO_CART:
                decisions = self._add_to_cart(page, goal)
            
            elif goal.goal_type == GoalType.CHECKOUT:
                decisions = self._checkout(page, goal)
            
            elif goal.goal_type == GoalType.LOGIN:
                decisions = self._login(page, goal)
            
            elif goal.goal_type == GoalType.SIGNUP:
                decisions = self._signup(page, goal)
            
            elif goal.goal_type == GoalType.COMPARE_PRODUCTS:
                decisions = self._compare_products(page, goal)
            
            else:
                # Default: try to find relevant product
                decisions = self._find_relevant_product(page, goal)
        
        except Exception as e:
            # Create error decision
            error_decision = Decision(
                action='error',
                element=None,
                parameters={'error': str(e)},
                confidence=0.0,
                reasoning=f'Failed to execute goal: {e}'
            )
            decisions.append(error_decision)
        
        # Store decision history
        self.decision_history.extend(decisions)
        
        return decisions
    
    def _find_cheapest_product(self, page: Page, goal: Goal) -> List[Decision]:
        """Find the cheapest product on the page."""
        products = extract_products(page)
        
        if not products:
            return [Decision(
                action='no_products_found',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products found on the page'
            )]
        
        # Filter by parameters
        filtered_products = self._filter_products(products, goal.parameters)
        
        if not filtered_products:
            return [Decision(
                action='no_matching_products',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products match the specified criteria'
            )]
        
        # Find cheapest
        cheapest_product = min(filtered_products, key=lambda p: p.price or float('inf'))
        
        if cheapest_product.price is None:
            return [Decision(
                action='no_priced_products',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products with valid prices found'
            )]
        
        # Create decision
        decision = Decision(
            action='click_product',
            element=cheapest_product.element,
            parameters={
                'product_name': cheapest_product.name,
                'price': cheapest_product.price,
                'brand': cheapest_product.brand
            },
            confidence=0.9,
            reasoning=f'Selected cheapest product: {cheapest_product.name} at ${cheapest_product.price}'
        )
        
        return [decision]
    
    def _find_most_expensive_product(self, page: Page, goal: Goal) -> List[Decision]:
        """Find the most expensive product on the page."""
        products = extract_products(page)
        
        if not products:
            return [Decision(
                action='no_products_found',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products found on the page'
            )]
        
        # Filter by parameters
        filtered_products = self._filter_products(products, goal.parameters)
        
        if not filtered_products:
            return [Decision(
                action='no_matching_products',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products match the specified criteria'
            )]
        
        # Find most expensive
        most_expensive = max(filtered_products, key=lambda p: p.price or 0)
        
        if most_expensive.price is None:
            return [Decision(
                action='no_priced_products',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products with valid prices found'
            )]
        
        # Create decision
        decision = Decision(
            action='click_product',
            element=most_expensive.element,
            parameters={
                'product_name': most_expensive.name,
                'price': most_expensive.price,
                'brand': most_expensive.brand
            },
            confidence=0.9,
            reasoning=f'Selected most expensive product: {most_expensive.name} at ${most_expensive.price}'
        )
        
        return [decision]
    
    def _find_best_rated_product(self, page: Page, goal: Goal) -> List[Decision]:
        """Find the best rated product on the page."""
        products = extract_products(page)
        
        if not products:
            return [Decision(
                action='no_products_found',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products found on the page'
            )]
        
        # Filter by parameters
        filtered_products = self._filter_products(products, goal.parameters)
        
        if not filtered_products:
            return [Decision(
                action='no_matching_products',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products match the specified criteria'
            )]
        
        # Find best rated (with rating fallback to price)
        rated_products = [p for p in filtered_products if p.rating is not None]
        
        if rated_products:
            best_rated = max(rated_products, key=lambda p: p.rating or 0)
            reasoning = f'Selected best rated product: {best_rated.name} with {best_rated.rating} stars'
        else:
            # Fallback to cheapest if no ratings
            best_rated = min(filtered_products, key=lambda p: p.price or float('inf'))
            reasoning = f'No ratings found, selected cheapest: {best_rated.name} at ${best_rated.price}'
        
        # Create decision
        decision = Decision(
            action='click_product',
            element=best_rated.element,
            parameters={
                'product_name': best_rated.name,
                'price': best_rated.price,
                'rating': best_rated.rating,
                'brand': best_rated.brand
            },
            confidence=0.8,
            reasoning=reasoning
        )
        
        return [decision]
    
    def _find_specific_brand_product(self, page: Page, goal: Goal) -> List[Decision]:
        """Find a product from a specific brand."""
        products = extract_products(page)
        target_brand = goal.parameters.get('brand', '').lower()
        
        if not target_brand:
            return [Decision(
                action='no_brand_specified',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No brand specified in goal'
            )]
        
        if not products:
            return [Decision(
                action='no_products_found',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products found on the page'
            )]
        
        # Filter by brand
        brand_products = []
        for product in products:
            if product.brand and product.brand.lower() == target_brand:
                brand_products.append(product)
        
        if not brand_products:
            return [Decision(
                action='no_brand_products',
                element=None,
                parameters={'target_brand': target_brand},
                confidence=0.0,
                reasoning=f'No products found for brand: {target_brand}'
            )]
        
        # Select best from brand (cheapest or highest rated)
        best_product = self._select_best_from_list(brand_products, goal)
        
        # Create decision
        decision = Decision(
            action='click_product',
            element=best_product.element,
            parameters={
                'product_name': best_product.name,
                'price': best_product.price,
                'brand': best_product.brand,
                'rating': best_product.rating
            },
            confidence=0.9,
            reasoning=f'Selected {target_brand} product: {best_product.name}'
        )
        
        return [decision]
    
    def _search_for_item(self, page: Page, goal: Goal) -> List[Decision]:
        """Search for an item on the page."""
        decisions = []
        
        # Look for search box
        search_selectors = [
            'input[type="search"]',
            'input[placeholder*="search" i]',
            'input[name*="search" i]',
            '#search',
            '.search-input',
            '[data-testid*="search"]'
        ]
        
        search_box = None
        for selector in search_selectors:
            try:
                search_box = page.query_selector(selector)
                if search_box:
                    break
            except:
                continue
        
        if not search_box:
            return [Decision(
                action='no_search_box',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No search box found on the page'
            )]
        
        # Extract search query from goal parameters
        search_query = goal.parameters.get('product_type', goal.parameters.get('brand', ''))
        
        if not search_query:
            search_query = 'product'  # Default query
        
        # Create fill decision
        fill_decision = Decision(
            action='fill_search',
            element=search_box,
            parameters={'query': search_query},
            confidence=0.8,
            reasoning=f'Fill search box with: {search_query}'
        )
        decisions.append(fill_decision)
        
        # Look for search button
        search_button_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Search")',
            'button:has-text("search")',
            '.search-button',
            '[data-testid*="search-button"]'
        ]
        
        search_button = None
        for selector in search_button_selectors:
            try:
                search_button = page.query_selector(selector)
                if search_button:
                    break
            except:
                continue
        
        if search_button:
            click_decision = Decision(
                action='click_search',
                element=search_button,
                parameters={'query': search_query},
                confidence=0.8,
                reasoning='Click search button to submit query'
            )
            decisions.append(click_decision)
        else:
            # Try pressing Enter
            enter_decision = Decision(
                action='press_enter',
                element=search_box,
                parameters={'query': search_query},
                confidence=0.7,
                reasoning='Press Enter to submit search'
            )
            decisions.append(enter_decision)
        
        return decisions
    
    def _add_to_cart(self, page: Page, goal: Goal) -> List[Decision]:
        """Add product to cart."""
        # Look for add to cart buttons
        cart_selectors = [
            'button:has-text("Add to Cart")',
            'button:has-text("Add to cart")',
            'button:has-text("Buy Now")',
            'button:has-text("Shop")',
            '.add-to-cart',
            '.add-to-cart-button',
            '[data-testid*="add-to-cart"]',
            'button[class*="cart"]'
        ]
        
        for selector in cart_selectors:
            try:
                cart_button = page.query_selector(selector)
                if cart_button:
                    return [Decision(
                        action='add_to_cart',
                        element=cart_button,
                        parameters={},
                        confidence=0.9,
                        reasoning=f'Found add to cart button: {selector}'
                    )]
            except:
                continue
        
        return [Decision(
            action='no_cart_button',
            element=None,
            parameters={},
            confidence=0.0,
            reasoning='No add to cart button found'
        )]
    
    def _checkout(self, page: Page, goal: Goal) -> List[Decision]:
        """Initiate checkout process."""
        # Look for checkout buttons or cart icon
        checkout_selectors = [
            'button:has-text("Checkout")',
            'button:has-text("checkout")',
            'a:has-text("Cart")',
            'a:has-text("cart")',
            '.checkout-button',
            '.cart-icon',
            '[data-testid*="checkout"]',
            '[data-testid*="cart"]'
        ]
        
        for selector in checkout_selectors:
            try:
                checkout_element = page.query_selector(selector)
                if checkout_element:
                    return [Decision(
                        action='checkout',
                        element=checkout_element,
                        parameters={},
                        confidence=0.9,
                        reasoning=f'Found checkout element: {selector}'
                    )]
            except:
                continue
        
        return [Decision(
            action='no_checkout',
            element=None,
            parameters={},
            confidence=0.0,
            reasoning='No checkout button or cart found'
        )]
    
    def _login(self, page: Page, goal: Goal) -> List[Decision]:
        """Handle login process."""
        page_analysis = analyze_page(page)
        forms = page_analysis.get('forms', [])
        
        if not forms:
            return [Decision(
                action='no_login_form',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No login form found'
            )]
        
        # Find login form (look for password field)
        login_form = None
        for form in forms:
            has_password = any(field.get('type') == 'password' for field in form.fields)
            if has_password:
                login_form = form
                break
        
        if not login_form:
            return [Decision(
                action='no_login_form',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No login form with password field found'
            )]
        
        decisions = []
        
        # Fill username/email field
        username_field = None
        for field in login_form.fields:
            if field.get('type') in ['email', 'text'] and any(keyword in field.get('name', '').lower() + field.get('label', '').lower() for keyword in ['email', 'user', 'login']):
                username_field = field
                break
        
        if username_field:
            decisions.append(Decision(
                action='fill_username',
                element=login_form.element.query_selector(f'input[name="{username_field["name"]}"]'),
                parameters={'value': 'test@example.com'},  # Should come from goal parameters
                confidence=0.8,
                reasoning='Fill username/email field'
            ))
        
        # Fill password field
        password_field = None
        for field in login_form.fields:
            if field.get('type') == 'password':
                password_field = field
                break
        
        if password_field:
            decisions.append(Decision(
                action='fill_password',
                element=login_form.element.query_selector(f'input[name="{password_field["name"]}"]'),
                parameters={'value': 'password123'},  # Should come from goal parameters
                confidence=0.8,
                reasoning='Fill password field'
            ))
        
        # Submit form
        if login_form.submit_button:
            decisions.append(Decision(
                action='submit_login',
                element=login_form.submit_button,
                parameters={},
                confidence=0.9,
                reasoning='Click submit button'
            ))
        
        return decisions
    
    def _signup(self, page: Page, goal: Goal) -> List[Decision]:
        """Handle signup process."""
        # Similar to login but for registration
        page_analysis = analyze_page(page)
        forms = page_analysis.get('forms', [])
        
        if not forms:
            return [Decision(
                action='no_signup_form',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No signup form found'
            )]
        
        # Find signup form
        signup_form = None
        for form in forms:
            form_text = form.element.inner_text().lower()
            if any(keyword in form_text for keyword in ['register', 'signup', 'sign up', 'create account']):
                signup_form = form
                break
        
        if not signup_form:
            return [Decision(
                action='no_signup_form',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No signup form found'
            )]
        
        return [Decision(
            action='fill_signup_form',
            element=signup_form.element,
            parameters={},
            confidence=0.7,
            reasoning='Found signup form - requires manual filling'
        )]
    
    def _compare_products(self, page: Page, goal: Goal) -> List[Decision]:
        """Compare products on the page."""
        products = extract_products(page)
        
        if len(products) < 2:
            return [Decision(
                action='not_enough_products',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='Need at least 2 products to compare'
            )]
        
        # Select top products for comparison
        top_products = sorted(products, key=lambda p: (p.rating or 0, -(p.price or 0)))[:2]
        
        decisions = []
        for i, product in enumerate(top_products):
            decisions.append(Decision(
                action='select_for_comparison',
                element=product.element,
                parameters={
                    'product_name': product.name,
                    'price': product.price,
                    'rating': product.rating,
                    'selection_order': i + 1
                },
                confidence=0.8,
                reasoning=f'Select product {i+1} for comparison: {product.name}'
            ))
        
        return decisions
    
    def _find_relevant_product(self, page: Page, goal: Goal) -> List[Decision]:
        """Find a relevant product based on goal parameters."""
        products = extract_products(page)
        
        if not products:
            return [Decision(
                action='no_products_found',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products found on the page'
            )]
        
        # Filter by parameters
        filtered_products = self._filter_products(products, goal.parameters)
        
        if not filtered_products:
            return [Decision(
                action='no_matching_products',
                element=None,
                parameters={},
                confidence=0.0,
                reasoning='No products match the specified criteria'
            )]
        
        # Select best product
        best_product = self._select_best_from_list(filtered_products, goal)
        
        return [Decision(
            action='click_product',
            element=best_product.element,
            parameters={
                'product_name': best_product.name,
                'price': best_product.price,
                'brand': best_product.brand
            },
            confidence=0.7,
            reasoning=f'Selected relevant product: {best_product.name}'
        )]
    
    def _filter_products(self, products: List[Product], parameters: Dict[str, Any]) -> List[Product]:
        """Filter products based on parameters."""
        filtered = products.copy()
        
        # Filter by brand
        if 'brand' in parameters:
            target_brand = parameters['brand'].lower()
            filtered = [p for p in filtered if p.brand and p.brand.lower() == target_brand]
        
        # Filter by product type
        if 'product_type' in parameters:
            target_type = parameters['product_type'].lower()
            filtered = [p for p in filtered if target_type in p.name.lower()]
        
        # Filter by price range
        if 'price_limit' in parameters:
            max_price = parameters['price_limit']
            filtered = [p for p in filtered if p.price and p.price <= max_price]
        
        # Filter by minimum rating
        if 'min_rating' in parameters:
            min_rating = parameters['min_rating']
            filtered = [p for p in filtered if p.rating and p.rating >= min_rating]
        
        # Filter by availability
        filtered = [p for p in filtered if not p.availability or 'out of stock' not in p.availability.lower()]
        
        return filtered
    
    def _select_best_from_list(self, products: List[Product], goal: Goal) -> Product:
        """Select the best product from a list based on goal type."""
        if not products:
            return None
        
        if goal.goal_type == GoalType.FIND_CHEAPEST:
            return min(products, key=lambda p: p.price or float('inf'))
        
        elif goal.goal_type == GoalType.FIND_MOST_EXPENSIVE:
            return max(products, key=lambda p: p.price or 0)
        
        elif goal.goal_type == GoalType.FIND_BEST_RATED:
            rated_products = [p for p in products if p.rating is not None]
            if rated_products:
                return max(rated_products, key=lambda p: p.rating or 0)
            else:
                return min(products, key=lambda p: p.price or float('inf'))
        
        else:
            # Default: balance price and rating
            def score_product(p):
                score = 0
                if p.price:
                    score += (1000 - p.price) * self.weights['price']  # Lower price = higher score
                if p.rating:
                    score += p.rating * 100 * self.weights['rating']
                if p.brand:
                    score += 50 * self.weights['brand']
                return score
            
            return max(products, key=score_product)
    
    def get_decision_summary(self) -> Dict[str, Any]:
        """Get summary of all decisions made."""
        if not self.decision_history:
            return {'total_decisions': 0, 'decisions': []}
        
        # Group decisions by action type
        action_counts = {}
        for decision in self.decision_history:
            action = decision.action
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Calculate average confidence
        avg_confidence = sum(d.confidence for d in self.decision_history) / len(self.decision_history)
        
        return {
            'total_decisions': len(self.decision_history),
            'action_counts': action_counts,
            'average_confidence': avg_confidence,
            'recent_decisions': self.decision_history[-5:]  # Last 5 decisions
        }


# Convenience functions
def execute_goal(page: Page, goal: Goal) -> List[Decision]:
    """Quick function to execute a goal."""
    engine = DecisionEngine()
    return engine.execute_goal(page, goal)


def find_cheapest_product(page: Page) -> Optional[Decision]:
    """Quick function to find cheapest product."""
    engine = DecisionEngine()
    goal = Goal(GoalType.FIND_CHEAPEST, {}, 0.9, "Find cheapest product")
    decisions = engine.execute_goal(page, goal)
    return decisions[0] if decisions else None
