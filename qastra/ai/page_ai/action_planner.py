"""
Action Planner - Converts natural language instructions into actionable goals.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ActionType(Enum):
    """Types of actions that can be performed."""
    NAVIGATE = "navigate"
    SEARCH = "search"
    FILTER = "filter"
    SELECT = "select"
    CLICK = "click"
    FILL = "fill"
    SUBMIT = "submit"
    WAIT = "wait"
    VERIFY = "verify"


class GoalType(Enum):
    """Types of goals that can be achieved."""
    FIND_PRODUCT = "find_product"
    FIND_CHEAPEST = "find_cheapest"
    FIND_MOST_EXPENSIVE = "find_most_expensive"
    FIND_BEST_RATED = "find_best_rated"
    FIND_SPECIFIC_BRAND = "find_specific_brand"
    SEARCH_FOR_ITEM = "search_for_item"
    FILL_FORM = "fill_form"
    NAVIGATE_TO_PAGE = "navigate_to_page"
    COMPARE_PRODUCTS = "compare_products"
    ADD_TO_CART = "add_to_cart"
    CHECKOUT = "checkout"
    LOGIN = "login"
    SIGNUP = "signup"


@dataclass
class Goal:
    """Represents a goal to be achieved."""
    goal_type: GoalType
    parameters: Dict[str, Any]
    confidence: float
    description: str


@dataclass
class ActionPlan:
    """Represents a sequence of actions to achieve a goal."""
    goal: Goal
    actions: List[Dict[str, Any]]
    description: str


class ActionPlanner:
    """Plans actions based on natural language instructions."""
    
    def __init__(self):
        # Action patterns
        self.action_patterns = {
            'navigate': [
                r'\b(go to|navigate|open|visit)\b',
                r'\b(click|follow|use)\s+(link|menu|button)\b',
            ],
            'search': [
                r'\b(search|find|look for|explore)\b',
                r'\b(type|enter)\s+(in|into)\s+(search|input|field)\b',
            ],
            'filter': [
                r'\b(filter|sort|refine|narrow)\b',
                r'\b(order by|sort by|arrange by)\b',
            ],
            'select': [
                r'\b(select|choose|pick|get)\b',
                r'\b(click|tap)\s+(on|)\b',
            ],
            'fill': [
                r'\b(fill|enter|type|input)\b',
                r'\b(write|put)\s+(in|into)\b',
            ],
            'submit': [
                r'\b(submit|send|confirm|apply)\b',
                r'\b(click|press)\s+(submit|send|confirm)\b',
            ],
            'wait': [
                r'\b(wait|pause|delay)\b',
                r'\b(until|till)\b',
            ],
            'verify': [
                r'\b(verify|check|confirm|ensure)\b',
                r'\b(make sure|assert)\b',
            ]
        }
        
        # Goal patterns
        self.goal_patterns = {
            'cheapest': [
                r'\b(cheapest|lowest|minimum|best price|most affordable)\b',
                r'\b(lowest price|best deal|best value)\b',
            ],
            'expensive': [
                r'\b(most expensive|highest|maximum|premium|top)\b',
                r'\b(highest price|most expensive|luxury)\b',
            ],
            'best_rated': [
                r'\b(best rated|highest rated|top rated|most popular)\b',
                r'\b(highest rating|best reviews|top reviews)\b',
            ],
            'brand_specific': [
                r'\b(apple|samsung|dell|hp|lenovo|asus|acer|microsoft|sony|lg|toshiba)\b',
                r'\b(iphone|macbook|ipad|galaxy|thinkpad|pavilion|inspiron|vivobook|surface)\b',
            ],
            'product_type': [
                r'\b(laptop|phone|tablet|desktop|monitor|keyboard|mouse|headphones|speaker|camera)\b',
                r'\b(computer|pc|notebook|smartphone|mobile|display)\b',
            ],
            'add_to_cart': [
                r'\b(add to cart|add to bag|buy|purchase|order|shop)\b',
                r'\b(get|buy|purchase|order)\s+(it|that|this)\b',
            ],
            'checkout': [
                r'\b(checkout|complete purchase|buy now|proceed to payment)\b',
                r'\b(finish purchase|complete order|pay)\b',
            ],
            'login': [
                r'\b(log in|sign in|login|signin)\b',
                r'\b(enter|access)\s+(account|my account)\b',
            ],
            'signup': [
                r'\b(sign up|register|create account|signup)\b',
                r'\b(join|new account|get started)\b',
            ],
            'compare': [
                r'\b(compare|vs|versus|difference)\b',
                r'\b(show me|tell me about)\b',
            ]
        }
        
        # Parameter patterns
        self.parameter_patterns = {
            'price_range': r'\b(between|under|over|above|below|less than|more than)\s*\$?(\d+(?:\.\d{2})?)',
            'brand': r'\b(apple|samsung|dell|hp|lenovo|asus|acer|microsoft|sony|lg|toshiba|msi|razer)\b',
            'product_type': r'\b(laptop|phone|tablet|desktop|monitor|keyboard|mouse|headphones|speaker|camera)\b',
            'rating': r'\b(\d+(?:\.\d+)?)\s*(stars?|rating|out of \d)',
            'quantity': r'\b(\d+)\s*(items?|products?|units?)',
        }
    
    def parse_instruction(self, instruction: str) -> ActionPlan:
        """
        Parse a natural language instruction into an action plan.
        
        Args:
            instruction: Natural language instruction
            
        Returns:
            ActionPlan with goal and sequence of actions
        """
        instruction_lower = instruction.lower().strip()
        
        # Extract goal
        goal = self._extract_goal(instruction_lower)
        
        # Extract actions
        actions = self._extract_actions(instruction_lower, goal)
        
        # Create action plan
        plan = ActionPlan(
            goal=goal,
            actions=actions,
            description=f"Execute: {instruction}"
        )
        
        return plan
    
    def _extract_goal(self, instruction: str) -> Goal:
        """Extract the primary goal from instruction."""
        goal_type = GoalType.FIND_PRODUCT
        parameters = {}
        confidence = 0.5
        
        # Check for specific goal types
        for goal_name, patterns in self.goal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, instruction):
                    if goal_name == 'cheapest':
                        goal_type = GoalType.FIND_CHEAPEST
                        confidence = 0.9
                    elif goal_name == 'expensive':
                        goal_type = GoalType.FIND_MOST_EXPENSIVE
                        confidence = 0.9
                    elif goal_name == 'best_rated':
                        goal_type = GoalType.FIND_BEST_RATED
                        confidence = 0.8
                    elif goal_name == 'brand_specific':
                        goal_type = GoalType.FIND_SPECIFIC_BRAND
                        confidence = 0.8
                        # Extract brand parameter
                        brand_match = re.search(pattern, instruction)
                        if brand_match:
                            parameters['brand'] = brand_match.group(1)
                    elif goal_name == 'product_type':
                        # Extract product type parameter
                        product_match = re.search(pattern, instruction)
                        if product_match:
                            parameters['product_type'] = product_match.group(1)
                    elif goal_name == 'add_to_cart':
                        goal_type = GoalType.ADD_TO_CART
                        confidence = 0.9
                    elif goal_name == 'checkout':
                        goal_type = GoalType.CHECKOUT
                        confidence = 0.9
                    elif goal_name == 'login':
                        goal_type = GoalType.LOGIN
                        confidence = 0.9
                    elif goal_name == 'signup':
                        goal_type = GoalType.SIGNUP
                        confidence = 0.9
                    elif goal_name == 'compare':
                        goal_type = GoalType.COMPARE_PRODUCTS
                        confidence = 0.8
                    break
        
        # Extract additional parameters
        for param_name, pattern in self.parameter_patterns.items():
            match = re.search(pattern, instruction)
            if match:
                if param_name == 'price_range':
                    parameters['price_limit'] = float(match.group(1))
                elif param_name == 'brand':
                    parameters['brand'] = match.group(1)
                elif param_name == 'product_type':
                    parameters['product_type'] = match.group(1)
                elif param_name == 'rating':
                    parameters['min_rating'] = float(match.group(1))
                elif param_name == 'quantity':
                    parameters['quantity'] = int(match.group(1))
        
        # Create description
        description = f"Goal: {goal_type.value}"
        if parameters:
            description += f" with parameters: {parameters}"
        
        return Goal(
            goal_type=goal_type,
            parameters=parameters,
            confidence=confidence,
            description=description
        )
    
    def _extract_actions(self, instruction: str, goal: Goal) -> List[Dict[str, Any]]:
        """Extract sequence of actions to achieve the goal."""
        actions = []
        
        # Determine actions based on goal type
        if goal.goal_type == GoalType.FIND_CHEAPEST:
            actions = [
                {'type': ActionType.SEARCH, 'description': 'Search for products'},
                {'type': ActionType.SELECT, 'description': 'Select cheapest product'},
                {'type': ActionType.CLICK, 'description': 'Click on cheapest product'}
            ]
        
        elif goal.goal_type == GoalType.FIND_MOST_EXPENSIVE:
            actions = [
                {'type': ActionType.SEARCH, 'description': 'Search for products'},
                {'type': ActionType.SELECT, 'description': 'Select most expensive product'},
                {'type': ActionType.CLICK, 'description': 'Click on most expensive product'}
            ]
        
        elif goal.goal_type == GoalType.FIND_BEST_RATED:
            actions = [
                {'type': ActionType.SEARCH, 'description': 'Search for products'},
                {'type': ActionType.FILTER, 'description': 'Sort by rating'},
                {'type': ActionType.SELECT, 'description': 'Select best rated product'},
                {'type': ActionType.CLICK, 'description': 'Click on best rated product'}
            ]
        
        elif goal.goal_type == GoalType.FIND_SPECIFIC_BRAND:
            brand = goal.parameters.get('brand', '')
            actions = [
                {'type': ActionType.SEARCH, 'description': f'Search for {brand} products'},
                {'type': ActionType.FILTER, 'description': f'Filter by brand: {brand}'},
                {'type': ActionType.SELECT, 'description': f'Select {brand} product'},
                {'type': ActionType.CLICK, 'description': f'Click on {brand} product'}
            ]
        
        elif goal.goal_type == GoalType.SEARCH_FOR_ITEM:
            actions = [
                {'type': ActionType.NAVIGATE, 'description': 'Navigate to search page'},
                {'type': ActionType.FILL, 'description': 'Enter search query'},
                {'type': ActionType.SUBMIT, 'description': 'Submit search'},
                {'type': ActionType.WAIT, 'description': 'Wait for results'}
            ]
        
        elif goal.goal_type == GoalType.ADD_TO_CART:
            actions = [
                {'type': ActionType.SELECT, 'description': 'Select product'},
                {'type': ActionType.CLICK, 'description': 'Click add to cart'},
                {'type': ActionType.VERIFY, 'description': 'Verify item in cart'}
            ]
        
        elif goal.goal_type == GoalType.CHECKOUT:
            actions = [
                {'type': ActionType.NAVIGATE, 'description': 'Navigate to cart'},
                {'type': ActionType.CLICK, 'description': 'Click checkout'},
                {'type': ActionType.FILL, 'description': 'Fill checkout form'},
                {'type': ActionType.SUBMIT, 'description': 'Submit order'}
            ]
        
        elif goal.goal_type == GoalType.LOGIN:
            actions = [
                {'type': ActionType.NAVIGATE, 'description': 'Navigate to login page'},
                {'type': ActionType.FILL, 'description': 'Fill login credentials'},
                {'type': ActionType.SUBMIT, 'description': 'Submit login form'},
                {'type': ActionType.VERIFY, 'description': 'Verify successful login'}
            ]
        
        elif goal.goal_type == GoalType.SIGNUP:
            actions = [
                {'type': ActionType.NAVIGATE, 'description': 'Navigate to signup page'},
                {'type': ActionType.FILL, 'description': 'Fill registration form'},
                {'type': ActionType.SUBMIT, 'description': 'Submit registration'},
                {'type': ActionType.VERIFY, 'description': 'Verify successful signup'}
            ]
        
        elif goal.goal_type == GoalType.COMPARE_PRODUCTS:
            actions = [
                {'type': ActionType.SEARCH, 'description': 'Find products to compare'},
                {'type': ActionType.SELECT, 'description': 'Select first product'},
                {'type': ActionType.SELECT, 'description': 'Select second product'},
                {'type': ActionType.NAVIGATE, 'description': 'Navigate to comparison page'}
            ]
        
        else:
            # Default actions for general goals
            actions = [
                {'type': ActionType.SEARCH, 'description': 'Search for relevant items'},
                {'type': ActionType.SELECT, 'description': 'Select appropriate item'},
                {'type': ActionType.CLICK, 'description': 'Click on selected item'}
            ]
        
        # Add goal parameters to actions
        for action in actions:
            action['parameters'] = goal.parameters
        
        return actions
    
    def plan_search_query(self, instruction: str) -> str:
        """Extract search query from instruction."""
        # Look for product types and brands
        product_types = []
        brands = []
        
        for pattern in self.goal_patterns['product_type']:
            matches = re.findall(pattern, instruction, re.IGNORECASE)
            product_types.extend(matches)
        
        for pattern in self.goal_patterns['brand_specific']:
            matches = re.findall(pattern, instruction, re.IGNORECASE)
            brands.extend(matches)
        
        # Build search query
        query_parts = []
        
        if brands:
            query_parts.extend(brands)
        
        if product_types:
            query_parts.extend(product_types)
        
        # Add other keywords
        keywords = re.findall(r'\b(laptop|phone|tablet|computer|electronics|tech|gadget)\b', instruction, re.IGNORECASE)
        query_parts.extend(keywords)
        
        return ' '.join(query_parts) if query_parts else instruction
    
    def plan_form_filling(self, instruction: str, form_fields: List[Dict[str, Any]]) -> Dict[str, str]:
        """Plan how to fill a form based on instruction."""
        field_values = {}
        
        # Extract common form field values
        email_patterns = [
            r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
            r'\b(email|mail)\s*[:=]\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]
        
        password_patterns = [
            r'\b(password|pass)\s*[:=]\s*(\S+)',
            r'\b(use|enter)\s+(password|pass)\s*(\S+)'
        ]
        
        name_patterns = [
            r'\b(name|username|user)\s*[:=]\s*([A-Za-z\s]+)',
            r'\b(i am|my name is)\s+([A-Za-z\s]+)'
        ]
        
        # Extract values
        for pattern in email_patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                email = match.group(1) if match.lastindex == 1 else match.group(2)
                field_values['email'] = email
        
        for pattern in password_patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                password = match.group(1) if match.lastindex == 1 else match.group(2)
                field_values['password'] = password
        
        for pattern in name_patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                name = match.group(1) if match.lastindex == 1 else match.group(2)
                field_values['name'] = name.strip()
        
        # Map to form fields
        mapped_values = {}
        for field in form_fields:
            field_name = field.get('name', '').lower()
            field_label = field.get('label', '').lower()
            field_type = field.get('type', '').lower()
            
            # Map by field name
            if 'email' in field_name or 'mail' in field_name:
                if 'email' in field_values:
                    mapped_values[field_name] = field_values['email']
            elif 'password' in field_name or 'pass' in field_name:
                if 'password' in field_values:
                    mapped_values[field_name] = field_values['password']
            elif 'name' in field_name or 'user' in field_name:
                if 'name' in field_values:
                    mapped_values[field_name] = field_values['name']
            
            # Map by field type
            elif field_type == 'email':
                if 'email' in field_values:
                    mapped_values[field_name] = field_values['email']
            elif field_type == 'password':
                if 'password' in field_values:
                    mapped_values[field_name] = field_values['password']
            
            # Map by label
            elif 'email' in field_label:
                if 'email' in field_values:
                    mapped_values[field_name] = field_values['email']
            elif 'password' in field_label:
                if 'password' in field_values:
                    mapped_values[field_name] = field_values['password']
        
        return mapped_values
    
    def get_confidence_score(self, instruction: str) -> float:
        """Get confidence score for instruction understanding."""
        instruction_lower = instruction.lower()
        
        # Check for clear action words
        action_words = 0
        for action_type, patterns in self.action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, instruction_lower):
                    action_words += 1
                    break
        
        # Check for clear goal words
        goal_words = 0
        for goal_type, patterns in self.goal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, instruction_lower):
                    goal_words += 1
                    break
        
        # Calculate confidence
        total_words = len(instruction.split())
        if total_words == 0:
            return 0.0
        
        confidence = min(1.0, (action_words + goal_words) / max(1, total_words * 0.3))
        
        return confidence


# Convenience functions
def parse_instruction(instruction: str) -> ActionPlan:
    """Quick function to parse instruction into action plan."""
    planner = ActionPlanner()
    return planner.parse_instruction(instruction)


def plan_search_query(instruction: str) -> str:
    """Quick function to extract search query."""
    planner = ActionPlanner()
    return planner.plan_search_query(instruction)
