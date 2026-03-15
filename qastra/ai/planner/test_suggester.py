"""
Test Suggester - Generates intelligent test suggestions based on page analysis.
"""

from typing import Dict, List, Any, Optional, Set
import re


class TestSuggester:
    """Suggests relevant test cases based on page analysis and detected features."""
    
    def __init__(self):
        # Test templates for different scenarios
        self.test_templates = {
            'authentication': {
                'login': [
                    'Login with valid credentials',
                    'Login with invalid username',
                    'Login with invalid password',
                    'Login with empty fields',
                    'Login with special characters',
                    'Login with SQL injection attempts',
                    'Login session timeout test',
                    'Login after logout'
                ],
                'signup': [
                    'Signup with valid data',
                    'Signup with existing email',
                    'Signup with weak password',
                    'Signup with invalid email format',
                    'Signup with empty required fields',
                    'Signup with password confirmation mismatch',
                    'Email verification after signup',
                    'Duplicate username prevention'
                ]
            },
            'ecommerce': {
                'search': [
                    'Search with valid keywords',
                    'Search with no results',
                    'Search with special characters',
                    'Search filters and sorting',
                    'Search pagination',
                    'Search autocomplete',
                    'Search from category page'
                ],
                'cart': [
                    'Add item to cart',
                    'Add multiple items to cart',
                    'Remove item from cart',
                    'Update item quantity',
                    'Cart persistence',
                    'Empty cart state',
                    'Cart from different pages',
                    'Cart item details'
                ],
                'checkout': [
                    'Checkout as guest',
                    'Checkout with registered user',
                    'Checkout with invalid payment',
                    'Checkout with expired card',
                    'Checkout address validation',
                    'Checkout shipping options',
                    'Checkout tax calculation',
                    'Checkout order confirmation'
                ]
            },
            'content': {
                'navigation': [
                    'Main menu navigation',
                    'Breadcrumb navigation',
                    'Footer links navigation',
                    'Mobile menu navigation',
                    'Search from navigation',
                    'Navigation accessibility',
                    'Navigation responsiveness'
                ],
                'forms': [
                    'Form submission with valid data',
                    'Form validation errors',
                    'Form field requirements',
                    'Form file upload',
                    'Form character limits',
                    'Form special characters',
                    'Form duplicate submission',
                    'Form session timeout'
                ]
            },
            'general': {
                'ui': [
                    'Page load performance',
                    'Mobile responsiveness',
                    'Browser compatibility',
                    'Accessibility compliance',
                    'Broken links check',
                    'Image loading',
                    'Font rendering',
                    'Color contrast'
                ],
                'security': [
                    'SQL injection prevention',
                    'XSS vulnerability check',
                    'CSRF token validation',
                    'Secure headers check',
                    'Input sanitization',
                    'Authentication bypass',
                    'Authorization test',
                    'Data encryption'
                ]
            }
        }
        
        # Priority levels for different test types
        self.test_priorities = {
            'critical': ['Login with valid credentials', 'Login with invalid credentials'],
            'high': ['Add item to cart', 'Checkout as guest', 'Form submission with valid data'],
            'medium': ['Search with valid keywords', 'Navigation accessibility', 'Mobile responsiveness'],
            'low': ['Font rendering', 'Color contrast', 'Search autocomplete']
        }
    
    def suggest_tests(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate test suggestions based on page analysis.
        
        Args:
            analysis: Page analysis result from DOMAnalyzer
            
        Returns:
            List of test suggestions with metadata
        """
        suggestions = []
        features = analysis.get('features', {})
        forms = analysis.get('forms', [])
        buttons = analysis.get('buttons', [])
        links = analysis.get('links', [])
        inputs = analysis.get('inputs', [])
        page_type = analysis.get('page_type', 'unknown')
        user_flows = analysis.get('user_flows', [])
        
        # Generate suggestions based on detected features
        suggestions.extend(self._suggest_feature_tests(features))
        
        # Generate suggestions based on forms
        suggestions.extend(self._suggest_form_tests(forms))
        
        # Generate suggestions based on page type
        suggestions.extend(self._suggest_page_type_tests(page_type, analysis))
        
        # Generate suggestions based on user flows
        suggestions.extend(self._suggest_flow_tests(user_flows))
        
        # Generate general UI tests
        suggestions.extend(self._suggest_general_ui_tests(analysis))
        
        # Generate security tests
        suggestions.extend(self._suggest_security_tests(analysis))
        
        # Remove duplicates and sort by priority
        unique_suggestions = self._deduplicate_suggestions(suggestions)
        sorted_suggestions = self._sort_by_priority(unique_suggestions)
        
        return sorted_suggestions
    
    def _suggest_feature_tests(self, features: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Generate tests based on detected features."""
        suggestions = []
        
        if features.get('login'):
            suggestions.extend([
                {
                    'name': 'Login Flow Test',
                    'description': 'Test user login functionality',
                    'category': 'authentication',
                    'priority': 'critical',
                    'steps': ['Navigate to login page', 'Enter credentials', 'Submit form', 'Verify login'],
                    'test_cases': self.test_templates['authentication']['login']
                }
            ])
        
        if features.get('signup'):
            suggestions.extend([
                {
                    'name': 'Registration Flow Test',
                    'description': 'Test user registration functionality',
                    'category': 'authentication',
                    'priority': 'high',
                    'steps': ['Navigate to signup page', 'Fill registration form', 'Submit form', 'Verify registration'],
                    'test_cases': self.test_templates['authentication']['signup']
                }
            ])
        
        if features.get('search'):
            suggestions.extend([
                {
                    'name': 'Search Functionality Test',
                    'description': 'Test search feature',
                    'category': 'content',
                    'priority': 'high',
                    'steps': ['Enter search query', 'Submit search', 'Verify results', 'Test filters'],
                    'test_cases': self.test_templates['ecommerce']['search']
                }
            ])
        
        if features.get('cart'):
            suggestions.extend([
                {
                    'name': 'Shopping Cart Test',
                    'description': 'Test shopping cart functionality',
                    'category': 'ecommerce',
                    'priority': 'high',
                    'steps': ['Add item to cart', 'View cart', 'Modify cart', 'Proceed to checkout'],
                    'test_cases': self.test_templates['ecommerce']['cart']
                }
            ])
        
        if features.get('checkout'):
            suggestions.extend([
                {
                    'name': 'Checkout Process Test',
                    'description': 'Test checkout functionality',
                    'category': 'ecommerce',
                    'priority': 'critical',
                    'steps': ['Initiate checkout', 'Enter shipping info', 'Enter payment info', 'Complete order'],
                    'test_cases': self.test_templates['ecommerce']['checkout']
                }
            ])
        
        if features.get('contact'):
            suggestions.extend([
                {
                    'name': 'Contact Form Test',
                    'description': 'Test contact form functionality',
                    'category': 'content',
                    'priority': 'medium',
                    'steps': ['Navigate to contact page', 'Fill contact form', 'Submit form', 'Verify submission'],
                    'test_cases': ['Contact form with valid data', 'Contact form validation', 'Contact form spam prevention']
                }
            ])
        
        return suggestions
    
    def _suggest_form_tests(self, forms: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate tests based on detected forms."""
        suggestions = []
        
        for form in forms:
            form_purpose = form.get('purpose', 'general')
            
            if form_purpose == 'authentication':
                suggestions.append({
                    'name': f'Authentication Form Test',
                    'description': f'Test authentication form ({form.get("action", "unknown")})',
                    'category': 'authentication',
                    'priority': 'critical',
                    'form_index': form.get('index'),
                    'test_cases': self.test_templates['authentication']['login']
                })
            
            elif form_purpose == 'search':
                suggestions.append({
                    'name': f'Search Form Test',
                    'description': f'Test search form functionality',
                    'category': 'content',
                    'priority': 'high',
                    'form_index': form.get('index'),
                    'test_cases': self.test_templates['ecommerce']['search']
                })
            
            elif form_purpose == 'contact':
                suggestions.append({
                    'name': f'Contact Form Test',
                    'description': f'Test contact form functionality',
                    'category': 'content',
                    'priority': 'medium',
                    'form_index': form.get('index'),
                    'test_cases': ['Valid submission', 'Form validation', 'Error handling']
                })
            
            elif form_purpose == 'checkout':
                suggestions.append({
                    'name': f'Checkout Form Test',
                    'description': f'Test checkout form functionality',
                    'category': 'ecommerce',
                    'priority': 'critical',
                    'form_index': form.get('index'),
                    'test_cases': self.test_templates['ecommerce']['checkout']
                })
            
            else:
                # General form test
                suggestions.append({
                    'name': f'Form Validation Test',
                    'description': f'Test general form validation',
                    'category': 'content',
                    'priority': 'medium',
                    'form_index': form.get('index'),
                    'test_cases': self.test_templates['content']['forms']
                })
        
        return suggestions
    
    def _suggest_page_type_tests(self, page_type: str, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate tests based on page type."""
        suggestions = []
        
        if page_type == 'ecommerce':
            suggestions.extend([
                {
                    'name': 'Product Catalog Test',
                    'description': 'Test product catalog functionality',
                    'category': 'ecommerce',
                    'priority': 'high',
                    'test_cases': ['Product listing', 'Product details', 'Product filtering', 'Product sorting']
                },
                {
                    'name': 'User Account Test',
                    'description': 'Test user account management',
                    'category': 'authentication',
                    'priority': 'high',
                    'test_cases': ['Account creation', 'Profile update', 'Order history', 'Wishlist management']
                }
            ])
        
        elif page_type == 'social':
            suggestions.extend([
                {
                    'name': 'Social Features Test',
                    'description': 'Test social media functionality',
                    'category': 'content',
                    'priority': 'high',
                    'test_cases': ['Post creation', 'Comment functionality', 'Like/Share features', 'User interaction']
                }
            ])
        
        elif page_type == 'blog':
            suggestions.extend([
                {
                    'name': 'Blog Functionality Test',
                    'description': 'Test blog features',
                    'category': 'content',
                    'priority': 'medium',
                    'test_cases': ['Article display', 'Comment system', 'Category navigation', 'Search functionality']
                }
            ])
        
        elif page_type == 'corporate':
            suggestions.extend([
                {
                    'name': 'Corporate Site Test',
                    'description': 'Test corporate website functionality',
                    'category': 'content',
                    'priority': 'medium',
                    'test_cases': ['About page', 'Services page', 'Contact form', 'Team information']
                }
            ])
        
        return suggestions
    
    def _suggest_flow_tests(self, user_flows: List[str]) -> List[Dict[str, Any]]:
        """Generate tests based on identified user flows."""
        suggestions = []
        
        for flow in user_flows:
            flow_lower = flow.lower()
            
            if 'login' in flow_lower:
                suggestions.append({
                    'name': f'{flow} End-to-End Test',
                    'description': f'Test complete {flow.lower()} user journey',
                    'category': 'authentication',
                    'priority': 'critical',
                    'flow': flow
                })
            
            elif 'search' in flow_lower:
                suggestions.append({
                    'name': f'{flow} End-to-End Test',
                    'description': f'Test complete {flow.lower()} user journey',
                    'category': 'content',
                    'priority': 'high',
                    'flow': flow
                })
            
            elif 'cart' in flow_lower or 'checkout' in flow_lower:
                suggestions.append({
                    'name': f'{flow} End-to-End Test',
                    'description': f'Test complete {flow.lower()} user journey',
                    'category': 'ecommerce',
                    'priority': 'critical',
                    'flow': flow
                })
            
            else:
                suggestions.append({
                    'name': f'{flow} End-to-End Test',
                    'description': f'Test complete {flow.lower()} user journey',
                    'category': 'general',
                    'priority': 'medium',
                    'flow': flow
                })
        
        return suggestions
    
    def _suggest_general_ui_tests(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate general UI/UX tests."""
        suggestions = []
        
        # Always suggest basic UI tests
        suggestions.extend([
            {
                'name': 'Responsive Design Test',
                'description': 'Test website on different screen sizes',
                'category': 'ui',
                'priority': 'high',
                'test_cases': ['Mobile view', 'Tablet view', 'Desktop view', 'Orientation changes']
            },
            {
                'name': 'Browser Compatibility Test',
                'description': 'Test website on different browsers',
                'category': 'ui',
                'priority': 'medium',
                'test_cases': ['Chrome', 'Firefox', 'Safari', 'Edge']
            },
            {
                'name': 'Performance Test',
                'description': 'Test website performance metrics',
                'category': 'ui',
                'priority': 'medium',
                'test_cases': ['Page load time', 'Image optimization', 'Script loading', 'Cache behavior']
            }
        ])
        
        # Suggest accessibility tests if complex
        if analysis.get('complexity_score', 0) > 50:
            suggestions.append({
                'name': 'Accessibility Test',
                'description': 'Test website accessibility compliance',
                'category': 'ui',
                'priority': 'medium',
                'test_cases': ['Keyboard navigation', 'Screen reader compatibility', 'Color contrast', 'Alt text for images']
            })
        
        return suggestions
    
    def _suggest_security_tests(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security-related tests."""
        suggestions = []
        
        # Always suggest basic security tests
        suggestions.extend([
            {
                'name': 'Input Validation Test',
                'description': 'Test input validation and sanitization',
                'category': 'security',
                'priority': 'high',
                'test_cases': ['SQL injection prevention', 'XSS prevention', 'Input length limits', 'Special characters']
            },
            {
                'name': 'Authentication Security Test',
                'description': 'Test authentication security measures',
                'category': 'security',
                'priority': 'critical',
                'test_cases': ['Password strength', 'Session management', 'Login attempts limit', 'Logout functionality']
            }
        ])
        
        # Suggest advanced security tests for complex sites
        if analysis.get('complexity_score', 0) > 100:
            suggestions.extend([
                {
                    'name': 'Advanced Security Test',
                    'description': 'Test advanced security features',
                    'category': 'security',
                    'priority': 'medium',
                    'test_cases': ['CSRF protection', 'Secure headers', 'Data encryption', 'API security']
                }
            ])
        
        return suggestions
    
    def _deduplicate_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate suggestions."""
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            key = suggestion.get('name', '').lower()
            if key and key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions
    
    def _sort_by_priority(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort suggestions by priority."""
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        
        return sorted(suggestions, key=lambda x: priority_order.get(x.get('priority', 'low'), 3))
    
    def generate_test_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive test plan."""
        suggestions = self.suggest_tests(analysis)
        
        # Group suggestions by category
        categorized_suggestions = {}
        for suggestion in suggestions:
            category = suggestion.get('category', 'general')
            if category not in categorized_suggestions:
                categorized_suggestions[category] = []
            categorized_suggestions[category].append(suggestion)
        
        # Calculate test statistics
        total_tests = len(suggestions)
        critical_tests = len([s for s in suggestions if s.get('priority') == 'critical'])
        high_tests = len([s for s in suggestions if s.get('priority') == 'high'])
        
        return {
            'page_info': {
                'url': analysis.get('url'),
                'title': analysis.get('title'),
                'page_type': analysis.get('page_type'),
                'complexity_score': analysis.get('complexity_score')
            },
            'test_statistics': {
                'total_suggestions': total_tests,
                'critical_priority': critical_tests,
                'high_priority': high_tests,
                'categories': len(categorized_suggestions)
            },
            'categorized_suggestions': categorized_suggestions,
            'all_suggestions': suggestions,
            'recommended_approach': self._get_recommended_approach(analysis, suggestions)
        }
    
    def _get_recommended_approach(self, analysis: Dict[str, Any], suggestions: List[Dict[str, Any]]) -> str:
        """Get recommended testing approach based on analysis."""
        page_type = analysis.get('page_type', 'unknown')
        complexity = analysis.get('complexity_score', 0)
        
        if page_type == 'ecommerce':
            if complexity > 100:
                return "Start with critical authentication and checkout flows, then proceed to search and cart functionality. Include comprehensive UI and security testing."
            else:
                return "Focus on core e-commerce flows: login, product search, cart, and checkout. Add basic UI testing."
        
        elif page_type == 'social':
            return "Prioritize authentication and user interaction features. Test content creation, commenting, and social features."
        
        elif page_type == 'corporate':
            return "Focus on navigation, contact forms, and information accessibility. Include responsive design testing."
        
        elif complexity > 100:
            return "Start with critical functionality and authentication. Add comprehensive UI, performance, and security testing."
        
        else:
            return "Begin with basic functionality testing, then add UI compatibility and security validation."
    
    def format_test_plan(self, test_plan: Dict[str, Any]) -> str:
        """Format test plan for display."""
        output = []
        
        # Header
        output.append("🧠 Qastra AI Test Plan")
        output.append("=" * 50)
        
        # Page info
        page_info = test_plan['page_info']
        output.append(f"📄 Page: {page_info.get('title', 'Unknown')}")
        output.append(f"🌐 URL: {page_info.get('url', 'Unknown')}")
        output.append(f"🏷️  Type: {page_info.get('page_type', 'unknown').title()}")
        output.append(f"📊 Complexity: {page_info.get('complexity_score', 0)}")
        output.append("")
        
        # Statistics
        stats = test_plan['test_statistics']
        output.append("📈 Test Statistics")
        output.append("-" * 20)
        output.append(f"Total Tests: {stats['total_suggestions']}")
        output.append(f"Critical: {stats['critical_priority']}")
        output.append(f"High Priority: {stats['high_priority']}")
        output.append(f"Categories: {stats['categories']}")
        output.append("")
        
        # Recommendations by priority
        suggestions = test_plan['all_suggestions']
        critical_tests = [s for s in suggestions if s.get('priority') == 'critical']
        high_tests = [s for s in suggestions if s.get('priority') == 'high']
        
        if critical_tests:
            output.append("🔥 Critical Tests (Run First)")
            output.append("-" * 30)
            for i, test in enumerate(critical_tests, 1):
                output.append(f"{i}. {test['name']}")
                output.append(f"   {test['description']}")
            output.append("")
        
        if high_tests:
            output.append("⚡ High Priority Tests")
            output.append("-" * 25)
            for i, test in enumerate(high_tests, 1):
                output.append(f"{i}. {test['name']}")
                output.append(f"   {test['description']}")
            output.append("")
        
        # Recommended approach
        output.append("💡 Recommended Approach")
        output.append("-" * 25)
        output.append(test_plan['recommended_approach'])
        output.append("")
        
        return "\n".join(output)


# Convenience function
def suggest_tests(analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Quick function to generate test suggestions."""
    suggester = TestSuggester()
    return suggester.suggest_tests(analysis)
