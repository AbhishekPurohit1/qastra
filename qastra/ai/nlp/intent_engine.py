"""
Intent Engine - Maps parsed intents to browser actions.
"""

from typing import Dict, Any, List, Tuple, Optional
import re


class IntentEngine:
    """Maps parsed natural language intents to structured browser actions."""
    
    def __init__(self):
        # Action mappings for different intents
        self.action_mappings = {
            'login': self._map_login_actions,
            'search': self._map_search_actions,
            'click': self._map_click_actions,
            'fill': self._map_fill_actions,
            'navigate': self._map_navigate_actions,
            'select': self._map_select_actions,
            'wait': self._map_wait_actions,
            'scroll': self._map_scroll_actions,
            'assert': self._map_assert_actions,
        }
        
        # Common selector patterns
        self.selector_patterns = {
            'username': [
                'input[name*="username"]',
                'input[name*="user"]',
                'input[id*="username"]',
                'input[placeholder*="username"]',
                'input[type="text"]',
            ],
            'password': [
                'input[name*="password"]',
                'input[name*="pass"]',
                'input[id*="password"]',
                'input[placeholder*="password"]',
                'input[type="password"]',
            ],
            'email': [
                'input[name*="email"]',
                'input[name*="mail"]',
                'input[type="email"]',
                'input[placeholder*="email"]',
            ],
            'login': [
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'input[type="submit"]',
                'button[type="submit"]',
                'button:has-text("Submit")',
            ],
            'search': [
                'input[name*="search"]',
                'input[placeholder*="search"]',
                'input[type="search"]',
                'input[id*="search"]',
            ],
            'search_button': [
                'button:has-text("Search")',
                'button:has-text("Find")',
                'input[type="submit"][value*="Search"]',
            ],
        }
    
    def get_actions(self, intent_data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Convert parsed intent data to browser actions."""
        intent = intent_data.get('intent', 'unknown')
        confidence = intent_data.get('confidence', 0.0)
        extracted_data = intent_data.get('extracted_data', {})
        
        if confidence < 0.5:
            return [('log', f'Low confidence intent: {intent}')]
        
        if intent in self.action_mappings:
            return self.action_mappings[intent](extracted_data)
        
        return [('log', f'Unknown intent: {intent}')]
    
    def _map_login_actions(self, data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Map login intent to actions."""
        actions = []
        
        username = data.get('username')
        password = data.get('password')
        
        if username:
            selectors = self.selector_patterns['username']
            actions.append(('fill', selectors, username))
        
        if password:
            selectors = self.selector_patterns['password']
            actions.append(('fill', selectors, password))
        
        # Add login button click
        login_selectors = self.selector_patterns['login']
        actions.append(('click', login_selectors))
        
        return actions
    
    def _map_search_actions(self, data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Map search intent to actions."""
        actions = []
        
        search_term = data.get('search_term')
        if search_term:
            # Fill search field
            search_selectors = self.selector_patterns['search']
            actions.append(('fill', search_selectors, search_term))
            
            # Click search button
            search_button_selectors = self.selector_patterns['search_button']
            actions.append(('click', search_button_selectors))
        
        return actions
    
    def _map_click_actions(self, data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Map click intent to actions."""
        actions = []
        
        target = data.get('target')
        if target:
            selectors = self._generate_click_selectors(target)
            actions.append(('click', selectors))
        
        return actions
    
    def _map_fill_actions(self, data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Map fill intent to actions."""
        actions = []
        
        field = data.get('field')
        value = data.get('value')
        
        if field and value:
            selectors = self._generate_field_selectors(field)
            actions.append(('fill', selectors, value))
        
        return actions
    
    def _map_navigate_actions(self, data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Map navigate intent to actions."""
        actions = []
        
        destination = data.get('destination')
        if destination:
            # Check if it's a URL
            if re.match(r'https?://', destination):
                actions.append(('navigate', destination))
            else:
                # Try to construct URL from common patterns
                url = self._construct_url(destination)
                actions.append(('navigate', url))
        
        return actions
    
    def _map_select_actions(self, data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Map select intent to actions."""
        actions = []
        
        option = data.get('option')
        if option:
            selectors = self._generate_select_selectors(option)
            actions.append(('select', selectors))
        
        return actions
    
    def _map_wait_actions(self, data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Map wait intent to actions."""
        actions = []
        
        duration = data.get('duration', 1)
        actions.append(('wait', duration * 1000))  # Convert to milliseconds
        
        return actions
    
    def _map_scroll_actions(self, data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Map scroll intent to actions."""
        actions = []
        
        direction = data.get('direction', 'down')
        amount = data.get('amount', 1)
        
        actions.append(('scroll', direction, amount))
        
        return actions
    
    def _map_assert_actions(self, data: Dict[str, Any]) -> List[Tuple[str, ...]]:
        """Map assert intent to actions."""
        actions = []
        
        assertion = data.get('assertion')
        if assertion:
            actions.append(('assert', assertion))
        
        return actions
    
    def _generate_click_selectors(self, target: str) -> List[str]:
        """Generate selectors for clicking elements."""
        selectors = []
        
        # Text-based selectors
        selectors.append(f'text="{target}"')
        selectors.append(f'*:has-text("{target}")')
        
        # Button/link specific
        selectors.append(f'button:has-text("{target}")')
        selectors.append(f'a:has-text("{target}")')
        
        # Common button patterns
        if 'login' in target.lower():
            selectors.extend(self.selector_patterns['login'])
        elif 'search' in target.lower():
            selectors.extend(self.selector_patterns['search_button'])
        
        return selectors
    
    def _generate_field_selectors(self, field: str) -> List[str]:
        """Generate selectors for form fields."""
        field_lower = field.lower()
        
        # Check if it's a known field type
        if 'username' in field_lower or 'user' in field_lower:
            return self.selector_patterns['username']
        elif 'password' in field_lower or 'pass' in field_lower:
            return self.selector_patterns['password']
        elif 'email' in field_lower or 'mail' in field_lower:
            return self.selector_patterns['email']
        elif 'search' in field_lower:
            return self.selector_patterns['search']
        
        # Generic field selectors
        return [
            f'input[name*="{field}"]',
            f'input[id*="{field}"]',
            f'input[placeholder*="{field}"]',
            f'textarea[name*="{field}"]',
            f'select[name*="{field}"]',
        ]
    
    def _generate_select_selectors(self, option: str) -> List[str]:
        """Generate selectors for select options."""
        return [
            f'select option:has-text("{option}")',
            f'option:has-text("{option}")',
            f'select[name*="{option}"]',
            f'input[value="{option}"]',
        ]
    
    def _construct_url(self, destination: str) -> str:
        """Construct URL from destination string."""
        # Common website patterns
        site_patterns = {
            'google': 'https://www.google.com',
            'facebook': 'https://www.facebook.com',
            'twitter': 'https://www.twitter.com',
            'amazon': 'https://www.amazon.com',
            'youtube': 'https://www.youtube.com',
            'linkedin': 'https://www.linkedin.com',
            'github': 'https://github.com',
            'stackoverflow': 'https://stackoverflow.com',
        }
        
        dest_lower = destination.lower()
        
        for site, url in site_patterns.items():
            if site in dest_lower:
                return url
        
        # Default: assume it's a domain
        if not destination.startswith('http'):
            if '.' in destination:
                return f"https://www.{destination}"
            else:
                return f"https://www.{destination}.com"
        
        return destination
    
    def get_action_descriptions(self, actions: List[Tuple[str, ...]]) -> List[str]:
        """Get human-readable descriptions of actions."""
        descriptions = []
        
        for action in actions:
            action_type = action[0]
            
            if action_type == 'fill':
                field = action[2]
                value = action[3] if len(action) > 3 else 'value'
                descriptions.append(f"Fill {field} with {value}")
            
            elif action_type == 'click':
                target = action[2] if len(action) > 2 else 'element'
                descriptions.append(f"Click {target}")
            
            elif action_type == 'navigate':
                url = action[1]
                descriptions.append(f"Navigate to {url}")
            
            elif action_type == 'select':
                option = action[2] if len(action) > 2 else 'option'
                descriptions.append(f"Select {option}")
            
            elif action_type == 'wait':
                duration = action[1] / 1000  # Convert back to seconds
                descriptions.append(f"Wait for {duration} seconds")
            
            elif action_type == 'scroll':
                direction = action[1]
                amount = action[2] if len(action) > 2 else 1
                descriptions.append(f"Scroll {direction} {amount} time(s)")
            
            elif action_type == 'assert':
                assertion = action[1]
                descriptions.append(f"Assert: {assertion}")
            
            elif action_type == 'log':
                message = action[1]
                descriptions.append(f"Log: {message}")
        
        return descriptions
    
    def validate_actions(self, actions: List[Tuple[str, ...]]) -> List[Tuple[str, ...]]:
        """Validate and filter actions."""
        valid_actions = []
        
        for action in actions:
            action_type = action[0]
            
            if action_type in ['fill', 'click', 'select', 'navigate', 'wait', 'scroll', 'assert', 'log']:
                valid_actions.append(action)
        
        return valid_actions


# Convenience function
def get_actions(intent_data: Dict[str, Any]) -> List[Tuple[str, ...]]:
    """Quick function to get actions from intent data."""
    engine = IntentEngine()
    return engine.get_actions(intent_data)
