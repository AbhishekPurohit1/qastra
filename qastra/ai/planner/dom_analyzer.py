"""
DOM Analyzer - Analyzes website structure to detect key features and components.
"""

from typing import Dict, List, Any, Optional, Set
from playwright.sync_api import Page
import re


class DOMAnalyzer:
    """Analyzes DOM structure to identify key UI components and user flows."""
    
    def __init__(self):
        # Feature detection patterns
        self.feature_patterns = {
            'login': [
                r'login', r'sign\s*in', r'log\s*in', r'signin',
                r'authenticate', r'enter', r'access'
            ],
            'signup': [
                r'sign\s*up', r'register', r'create\s*account',
                r'join', r'signup', r'get\s*started'
            ],
            'search': [
                r'search', r'find', r'lookup', r'query',
                r'explore', r'discover'
            ],
            'cart': [
                r'cart', r'basket', r'bag', r'shopping',
                r'add\s*to\s*cart', r'checkout'
            ],
            'menu': [
                r'menu', r'navigation', r'nav', r'hamburger',
                r'sidebar', r'drawer'
            ],
            'profile': [
                r'profile', r'account', r'my\s*account',
                r'settings', r'preferences'
            ],
            'contact': [
                r'contact', r'reach\s*out', r'get\s*in\s*touch',
                r'email', r'support', r'help'
            ],
            'checkout': [
                r'checkout', r'buy', r'purchase', r'pay',
                r'order', r'submit\s*order'
            ],
            'wishlist': [
                r'wishlist', r'favorites', r'save',
                r'bookmark', r'like'
            ],
            'filter': [
                r'filter', r'sort', r'refine', r'narrow',
                r'category', r'brand'
            ]
        }
        
        # Input field patterns
        self.input_patterns = {
            'username': [
                r'username', r'user', r'email', r'login',
                r'id', r'account'
            ],
            'password': [
                r'password', r'pass', r'pwd', r'secret',
                r'key', r'pin'
            ],
            'email': [
                r'email', r'mail', r'emailaddress',
                r'e-mail'
            ],
            'phone': [
                r'phone', r'mobile', r'telephone',
                r'cell', r'contact'
            ],
            'address': [
                r'address', r'location', r'street',
                r'city', r'zip', r'postal'
            ],
            'name': [
                r'name', r'fullname', r'firstname',
                r'lastname', r'displayname'
            ],
            'search': [
                r'search', r'query', r'keyword',
                r'find', r'lookup'
            ]
        }
        
        # Page type indicators
        self.page_type_indicators = {
            'ecommerce': [
                r'product', r'price', r'cart', r'checkout',
                r'shop', r'store', r'buy', r'purchase',
                r'add\s*to\s*cart', r'wishlist'
            ],
            'social': [
                r'profile', r'friend', r'post', r'comment',
                r'like', r'share', r'message', r'follow'
            ],
            'blog': [
                r'post', r'article', r'blog', r'comment',
                r'author', r'category', r'tag'
            ],
            'corporate': [
                r'about', r'services', r'contact', r'careers',
                r'company', r'team', r'investors'
            ],
            'education': [
                r'course', r'lesson', r'tutorial', r'learn',
                r'student', r'teacher', r'education'
            ]
        }
    
    def analyze_page(self, page: Page) -> Dict[str, Any]:
        """
        Analyze the page and detect key features.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary with detected features and page analysis
        """
        analysis = {
            'url': page.url,
            'title': page.title(),
            'features': {},
            'forms': [],
            'buttons': [],
            'links': [],
            'inputs': [],
            'page_type': 'unknown',
            'complexity_score': 0,
            'user_flows': [],
            'test_suggestions': []
        }
        
        try:
            # Get page content
            content = page.content()
            title = page.title().lower()
            url = page.url.lower()
            
            # Analyze page type
            analysis['page_type'] = self._detect_page_type(content, title, url)
            
            # Analyze forms
            analysis['forms'] = self._analyze_forms(page)
            
            # Analyze buttons
            analysis['buttons'] = self._analyze_buttons(page)
            
            # Analyze links
            analysis['links'] = self._analyze_links(page)
            
            # Analyze inputs
            analysis['inputs'] = self._analyze_inputs(page)
            
            # Detect features
            analysis['features'] = self._detect_features(content, title, url, analysis)
            
            # Calculate complexity score
            analysis['complexity_score'] = self._calculate_complexity(analysis)
            
            # Identify user flows
            analysis['user_flows'] = self._identify_user_flows(analysis)
            
        except Exception as e:
            print(f"Error analyzing page: {e}")
        
        return analysis
    
    def _detect_page_type(self, content: str, title: str, url: str) -> str:
        """Detect the type of website based on content."""
        content_lower = content.lower()
        title_lower = title
        url_lower = url
        
        scores = {}
        
        for page_type, indicators in self.page_type_indicators.items():
            score = 0
            for indicator in indicators:
                pattern = re.compile(indicator, re.IGNORECASE)
                
                # Check title (highest weight)
                if pattern.search(title_lower):
                    score += 10
                
                # Check URL (medium weight)
                if pattern.search(url_lower):
                    score += 5
                
                # Check content (lower weight)
                matches = pattern.findall(content_lower)
                score += len(matches)
            
            scores[page_type] = score
        
        # Return the page type with highest score
        if scores and max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'unknown'
    
    def _analyze_forms(self, page: Page) -> List[Dict[str, Any]]:
        """Analyze all forms on the page."""
        forms = []
        
        try:
            form_elements = page.query_selector_all('form')
            
            for i, form in enumerate(form_elements):
                form_info = {
                    'index': i,
                    'action': form.get_attribute('action') or '',
                    'method': form.get_attribute('method') or 'GET',
                    'id': form.get_attribute('id') or '',
                    'class': form.get_attribute('class') or '',
                    'input_count': 0,
                    'button_count': 0,
                    'has_password': False,
                    'has_email': False,
                    'has_search': False,
                    'purpose': 'unknown'
                }
                
                # Count inputs and buttons within form
                inputs = form.query_selector_all('input, textarea, select')
                form_info['input_count'] = len(inputs)
                
                buttons = form.query_selector_all('button, input[type="submit"], input[type="button"]')
                form_info['button_count'] = len(buttons)
                
                # Detect input types
                for inp in inputs:
                    input_type = inp.get_attribute('type') or 'text'
                    input_name = (inp.get_attribute('name') or '').lower()
                    input_placeholder = (inp.get_attribute('placeholder') or '').lower()
                    
                    if input_type == 'password' or 'password' in input_name or 'password' in input_placeholder:
                        form_info['has_password'] = True
                    
                    if input_type == 'email' or 'email' in input_name or 'email' in input_placeholder:
                        form_info['has_email'] = True
                    
                    if 'search' in input_name or 'search' in input_placeholder:
                        form_info['has_search'] = True
                
                # Determine form purpose
                form_info['purpose'] = self._determine_form_purpose(form_info)
                
                forms.append(form_info)
        
        except Exception as e:
            print(f"Error analyzing forms: {e}")
        
        return forms
    
    def _analyze_buttons(self, page: Page) -> List[Dict[str, Any]]:
        """Analyze all buttons on the page."""
        buttons = []
        
        try:
            button_elements = page.query_selector_all('button, input[type="button"], input[type="submit"], [role="button"]')
            
            for button in button_elements:
                button_info = {
                    'text': button.inner_text().strip(),
                    'id': button.get_attribute('id') or '',
                    'class': button.get_attribute('class') or '',
                    'type': button.get_attribute('type') or 'button',
                    'purpose': 'unknown',
                    'intent': self._extract_intent(button.inner_text().strip())
                }
                
                button_info['purpose'] = self._determine_button_purpose(button_info)
                buttons.append(button_info)
        
        except Exception as e:
            print(f"Error analyzing buttons: {e}")
        
        return buttons
    
    def _analyze_links(self, page: Page) -> List[Dict[str, Any]]:
        """Analyze all links on the page."""
        links = []
        
        try:
            link_elements = page.query_selector_all('a[href]')
            
            for link in link_elements:
                link_info = {
                    'text': link.inner_text().strip(),
                    'href': link.get_attribute('href') or '',
                    'id': link.get_attribute('id') or '',
                    'class': link.get_attribute('class') or '',
                    'purpose': 'unknown',
                    'is_external': self._is_external_link(link.get_attribute('href') or ''),
                    'intent': self._extract_intent(link.inner_text().strip())
                }
                
                link_info['purpose'] = self._determine_link_purpose(link_info)
                links.append(link_info)
        
        except Exception as e:
            print(f"Error analyzing links: {e}")
        
        return links
    
    def _analyze_inputs(self, page: Page) -> List[Dict[str, Any]]:
        """Analyze all input fields on the page."""
        inputs = []
        
        try:
            input_elements = page.query_selector_all('input, textarea, select')
            
            for inp in input_elements:
                input_info = {
                    'type': inp.get_attribute('type') or 'text',
                    'name': inp.get_attribute('name') or '',
                    'id': inp.get_attribute('id') or '',
                    'placeholder': inp.get_attribute('placeholder') or '',
                    'class': inp.get_attribute('class') or '',
                    'purpose': 'unknown',
                    'intent': self._extract_input_intent(inp)
                }
                
                input_info['purpose'] = self._determine_input_purpose(input_info)
                inputs.append(input_info)
        
        except Exception as e:
            print(f"Error analyzing inputs: {e}")
        
        return inputs
    
    def _detect_features(self, content: str, title: str, url: str, analysis: Dict[str, Any]) -> Dict[str, bool]:
        """Detect specific features on the page."""
        features = {}
        content_lower = content.lower()
        title_lower = title
        url_lower = url
        
        for feature, patterns in self.feature_patterns.items():
            feature_found = False
            
            for pattern in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                
                # Check in title
                if regex.search(title_lower):
                    feature_found = True
                    break
                
                # Check in URL
                if regex.search(url_lower):
                    feature_found = True
                    break
                
                # Check in button texts
                for button in analysis.get('buttons', []):
                    if regex.search(button['text'].lower()):
                        feature_found = True
                        break
                
                if feature_found:
                    break
                
                # Check in link texts
                for link in analysis.get('links', []):
                    if regex.search(link['text'].lower()):
                        feature_found = True
                        break
                
                if feature_found:
                    break
                
                # Check in content
                if regex.search(content_lower):
                    feature_found = True
                    break
            
            features[feature] = feature_found
        
        return features
    
    def _calculate_complexity(self, analysis: Dict[str, Any]) -> int:
        """Calculate a complexity score for the page."""
        score = 0
        
        # Forms contribute to complexity
        score += len(analysis.get('forms', [])) * 5
        
        # Buttons contribute
        score += len(analysis.get('buttons', [])) * 2
        
        # Links contribute
        score += min(len(analysis.get('links', [])), 20)  # Cap at 20 links
        
        # Inputs contribute
        score += len(analysis.get('inputs', [])) * 3
        
        # Features contribute
        feature_count = sum(analysis.get('features', {}).values())
        score += feature_count * 10
        
        return score
    
    def _identify_user_flows(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify potential user flows based on detected features."""
        flows = []
        features = analysis.get('features', {})
        forms = analysis.get('forms', [])
        
        # Authentication flows
        if features.get('login'):
            flows.append('Login Flow')
        
        if features.get('signup'):
            flows.append('Registration Flow')
        
        # Search flows
        if features.get('search'):
            flows.append('Search Flow')
        
        # E-commerce flows
        if features.get('cart') or features.get('checkout'):
            flows.append('Shopping Cart Flow')
            flows.append('Checkout Flow')
        
        # Content flows
        if features.get('menu'):
            flows.append('Navigation Flow')
        
        # Contact flows
        if features.get('contact'):
            flows.append('Contact Flow')
        
        # Profile flows
        if features.get('profile'):
            flows.append('Profile Management Flow')
        
        # Form-based flows
        for form in forms:
            if form['purpose'] != 'unknown':
                flows.append(f"{form['purpose'].title()} Flow")
        
        return list(set(flows))  # Remove duplicates
    
    def _determine_form_purpose(self, form_info: Dict[str, Any]) -> str:
        """Determine the purpose of a form based on its characteristics."""
        if form_info['has_password'] and form_info['has_email']:
            return 'authentication'
        elif form_info['has_search']:
            return 'search'
        elif form_info['has_email'] and not form_info['has_password']:
            return 'newsletter'
        elif 'contact' in form_info['action'].lower() or 'contact' in form_info['class'].lower():
            return 'contact'
        elif 'checkout' in form_info['action'].lower() or 'payment' in form_info['class'].lower():
            return 'checkout'
        else:
            return 'general'
    
    def _determine_button_purpose(self, button_info: Dict[str, Any]) -> str:
        """Determine the purpose of a button."""
        text = button_info['text'].lower()
        
        for feature, patterns in self.feature_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return feature
        
        return 'general'
    
    def _determine_link_purpose(self, link_info: Dict[str, Any]) -> str:
        """Determine the purpose of a link."""
        text = link_info['text'].lower()
        href = link_info['href'].lower()
        
        for feature, patterns in self.feature_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text) or re.search(pattern, href):
                    return feature
        
        return 'navigation'
    
    def _determine_input_purpose(self, input_info: Dict[str, Any]) -> str:
        """Determine the purpose of an input field."""
        name = input_info['name'].lower()
        placeholder = input_info['placeholder'].lower()
        input_type = input_info['type'].lower()
        
        for field_type, patterns in self.input_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, name) or 
                    re.search(pattern, placeholder) or 
                    input_type == field_type):
                    return field_type
        
        return 'general'
    
    def _extract_intent(self, text: str) -> str:
        """Extract intent from text."""
        text_lower = text.lower()
        
        for feature, patterns in self.feature_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return feature
        
        return 'general'
    
    def _extract_input_intent(self, input_element) -> str:
        """Extract intent from an input element."""
        name = (input_element.get_attribute('name') or '').lower()
        placeholder = (input_element.get_attribute('placeholder') or '').lower()
        input_type = (input_element.get_attribute('type') or '').lower()
        
        for field_type, patterns in self.input_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, name) or 
                    re.search(pattern, placeholder) or 
                    input_type == field_type):
                    return field_type
        
        return 'general'
    
    def _is_external_link(self, href: str) -> bool:
        """Check if a link is external."""
        if not href or href.startswith('#'):
            return False
        
        if href.startswith(('http://', 'https://')):
            # For simplicity, consider all external HTTP links as external
            return True
        
        return False
    
    def get_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """Get a human-readable summary of the analysis."""
        summary = []
        
        summary.append(f"Page Type: {analysis['page_type'].title()}")
        summary.append(f"Complexity Score: {analysis['complexity_score']}")
        summary.append(f"Forms: {len(analysis['forms'])}")
        summary.append(f"Buttons: {len(analysis['buttons'])}")
        summary.append(f"Links: {len(analysis['links'])}")
        summary.append(f"Inputs: {len(analysis['inputs'])}")
        
        features = analysis.get('features', {})
        active_features = [k for k, v in features.items() if v]
        
        if active_features:
            summary.append(f"Features: {', '.join(active_features)}")
        
        flows = analysis.get('user_flows', [])
        if flows:
            summary.append(f"Detected Flows: {len(flows)}")
        
        return '\n'.join(summary)


# Convenience function
def analyze_page(page: Page) -> Dict[str, Any]:
    """Quick function to analyze a page."""
    analyzer = DOMAnalyzer()
    return analyzer.analyze_page(page)
