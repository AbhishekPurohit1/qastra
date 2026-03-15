"""
Element Scanner - Collects DOM element metadata for smart locator engine.
"""

from typing import Dict, List, Any, Tuple, Optional
from playwright.sync_api import Page, ElementHandle
import re


class ElementScanner:
    """Scans DOM elements and extracts their features for smart matching."""
    
    def __init__(self):
        self.interactive_selectors = [
            'button', 'input', 'a', 'select', 'textarea',
            '[role="button"]', '[role="link"]', '[onclick]',
            '[onsubmit]', '[type="submit"]', '[type="button"]'
        ]
        
        # Common field patterns for better matching
        self.field_patterns = {
            'username': ['username', 'user', 'email', 'login', 'id'],
            'password': ['password', 'pass', 'pwd', 'secret'],
            'email': ['email', 'mail', 'emailaddress'],
            'name': ['name', 'fullname', 'firstname', 'lastname'],
            'phone': ['phone', 'mobile', 'telephone'],
            'search': ['search', 'query', 'find'],
            'login': ['login', 'signin', 'sign-in', 'log in'],
            'register': ['register', 'signup', 'sign-up', 'create'],
            'submit': ['submit', 'send', 'save', 'continue'],
            'cancel': ['cancel', 'close', 'back', 'exit'],
            'checkout': ['checkout', 'buy', 'purchase', 'pay'],
        }
    
    def get_element_features(self, element: ElementHandle) -> Dict[str, Any]:
        """
        Extract comprehensive features from a DOM element.
        
        Args:
            element: Playwright ElementHandle
            
        Returns:
            Dictionary of element features
        """
        try:
            features = {
                'text': self._safe_get_text(element),
                'id': self._safe_get_attribute(element, 'id'),
                'class': self._safe_get_attribute(element, 'class'),
                'tag': self._safe_get_tag(element),
                'name': self._safe_get_attribute(element, 'name'),
                'placeholder': self._safe_get_attribute(element, 'placeholder'),
                'type': self._safe_get_attribute(element, 'type'),
                'value': self._safe_get_attribute(element, 'value'),
                'title': self._safe_get_attribute(element, 'title'),
                'alt': self._safe_get_attribute(element, 'alt'),
                'href': self._safe_get_attribute(element, 'href'),
                'role': self._safe_get_attribute(element, 'role'),
                'aria_label': self._safe_get_attribute(element, 'aria-label'),
                'data_test': self._safe_get_attribute(element, 'data-test'),
                'data_cy': self._safe_get_attribute(element, 'data-cy'),
                'visible': self._is_visible(element),
                'enabled': self._is_enabled(element),
                'xpath': self._get_xpath(element),
                'css_selector': self._get_css_selector(element),
            }
            
            # Add computed features
            features['text_clean'] = self._clean_text(features['text'])
            features['class_clean'] = self._clean_class(features['class'])
            features['id_clean'] = self._clean_text(features['id'])
            features['has_text'] = bool(features['text_clean'])
            features['has_placeholder'] = bool(features['placeholder'])
            features['is_input'] = features['tag'] in ['input', 'textarea', 'select']
            features['is_button'] = features['tag'] == 'button' or features['type'] in ['submit', 'button']
            features['is_link'] = features['tag'] == 'a'
            
            # Add semantic features
            features['semantic_type'] = self._detect_semantic_type(features)
            features['keywords'] = self._extract_keywords(features)
            
            return features
        
        except Exception as e:
            print(f"Error extracting features: {e}")
            return {}
    
    def _safe_get_text(self, element: ElementHandle) -> str:
        """Safely get element text content."""
        try:
            return element.inner_text().strip()
        except:
            return ""
    
    def _safe_get_attribute(self, element: ElementHandle, attr: str) -> str:
        """Safely get element attribute."""
        try:
            value = element.get_attribute(attr)
            return value.strip() if value else ""
        except:
            return ""
    
    def _safe_get_tag(self, element: ElementHandle) -> str:
        """Safely get element tag name."""
        try:
            return element.evaluate("el => el.tagName.toLowerCase()").strip()
        except:
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and special characters
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-_.]', ' ', text)
        text = text.strip().lower()
        
        return text
    
    def _clean_class(self, class_attr: str) -> str:
        """Clean and normalize class attribute."""
        if not class_attr:
            return ""
        
        # Split classes and clean each one
        classes = class_attr.split()
        cleaned = [self._clean_text(cls) for cls in classes if cls]
        return ' '.join(cleaned)
    
    def _is_visible(self, element: ElementHandle) -> bool:
        """Check if element is visible."""
        try:
            return element.is_visible()
        except:
            return False
    
    def _is_enabled(self, element: ElementHandle) -> bool:
        """Check if element is enabled."""
        try:
            return not element.is_disabled()
        except:
            return False
    
    def _get_xpath(self, element: ElementHandle) -> str:
        """Generate XPath for element."""
        try:
            return element.evaluate("""
                function getXPath(el) {
                    if (!el) return '';
                    if (el.id) return `//*[@id="${el.id}"]`;
                    
                    let parts = [];
                    while (el && el.nodeType === Node.ELEMENT_NODE) {
                        let index = 0;
                        let sibling = el.previousSibling;
                        while (sibling) {
                            if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === el.tagName) {
                                index++;
                            }
                            sibling = sibling.previousSibling;
                        }
                        
                        let tagName = el.tagName.toLowerCase();
                        let pathIndex = index > 0 ? `[${index + 1}]` : '';
                        parts.unshift(`${tagName}${pathIndex}`);
                        el = el.parentNode;
                    }
                    return '/' + parts.join('/');
                }
                return getXPath(this);
            """)
        except:
            return ""
    
    def _get_css_selector(self, element: ElementHandle) -> str:
        """Generate CSS selector for element."""
        try:
            return element.evaluate("""
                function getSelector(el) {
                    if (!el) return '';
                    if (el.id) return `#${el.id}`;
                    
                    let path = [];
                    while (el && el.nodeType === Node.ELEMENT_NODE) {
                        let selector = el.tagName.toLowerCase();
                        if (el.className) {
                            let classes = el.className.trim().split(/\\s+/);
                            selector += '.' + classes.join('.');
                        }
                        path.unshift(selector);
                        el = el.parentNode;
                        if (path.length > 3) break; // Limit depth
                    }
                    return path.join(' > ');
                }
                return getSelector(this);
            """)
        except:
            return ""
    
    def _detect_semantic_type(self, features: Dict[str, Any]) -> str:
        """Detect semantic type of element based on features."""
        text = features.get('text_clean', '')
        placeholder = features.get('placeholder', '').lower()
        element_id = features.get('id_clean', '')
        name = features.get('name', '').lower()
        tag = features.get('tag', '')
        element_type = features.get('type', '')
        
        combined_text = f"{text} {placeholder} {element_id} {name}".lower()
        
        # Check for semantic patterns
        for semantic_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                if pattern in combined_text:
                    return semantic_type
        
        # Type-based detection
        if tag == 'input':
            if element_type == 'password':
                return 'password'
            elif element_type == 'email':
                return 'email'
            elif element_type == 'submit':
                return 'submit'
            elif element_type == 'button':
                return 'button'
        
        # Tag-based detection
        if tag == 'button':
            return 'button'
        elif tag == 'a':
            return 'link'
        elif tag in ['input', 'textarea', 'select']:
            return 'input'
        
        return 'unknown'
    
    def _extract_keywords(self, features: Dict[str, Any]) -> List[str]:
        """Extract relevant keywords from element features."""
        keywords = set()
        
        # Add text keywords
        text = features.get('text_clean', '')
        if text:
            keywords.update(text.split())
        
        # Add placeholder keywords
        placeholder = features.get('placeholder', '').lower()
        if placeholder:
            keywords.update(placeholder.split())
        
        # Add ID keywords
        element_id = features.get('id_clean', '')
        if element_id:
            keywords.update(element_id.split())
        
        # Add class keywords (split by common separators)
        class_attr = features.get('class_clean', '')
        if class_attr:
            keywords.update(re.split(r'[-_\s]', class_attr))
        
        # Add name keywords
        name = features.get('name', '').lower()
        if name:
            keywords.update(name.split())
        
        # Filter and clean keywords
        filtered_keywords = []
        for keyword in keywords:
            if len(keyword) >= 2 and keyword.isalnum():
                filtered_keywords.append(keyword)
        
        return filtered_keywords
    
    def scan_page(self, page: Page, include_hidden: bool = False) -> List[Tuple[ElementHandle, Dict[str, Any]]]:
        """
        Scan the page and collect all interactive elements with their features.
        
        Args:
            page: Playwright page object
            include_hidden: Whether to include hidden elements
            
        Returns:
            List of tuples (element, features)
        """
        elements_data = []
        
        try:
            # Find all interactive elements
            for selector in self.interactive_selectors:
                try:
                    elements = page.query_selector_all(selector)
                    
                    for element in elements:
                        try:
                            # Skip hidden elements unless explicitly included
                            if not include_hidden:
                                bbox = element.bounding_box()
                                if not bbox or bbox['height'] == 0 or bbox['width'] == 0:
                                    continue
                            
                            features = self.get_element_features(element)
                            if features:
                                elements_data.append((element, features))
                        
                        except Exception as e:
                            print(f"Error processing element: {e}")
                            continue
                
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
        
        except Exception as e:
            print(f"Error scanning page: {e}")
        
        return elements_data
    
    def scan_elements_by_type(self, page: Page, element_type: str) -> List[Tuple[ElementHandle, Dict[str, Any]]]:
        """
        Scan page for elements of specific type.
        
        Args:
            page: Playwright page object
            element_type: Type of elements to find (button, input, link, etc.)
            
        Returns:
            List of tuples (element, features)
        """
        all_elements = self.scan_page(page)
        
        filtered_elements = []
        for element, features in all_elements:
            semantic_type = features.get('semantic_type', '')
            tag = features.get('tag', '')
            
            # Match by semantic type or tag
            if (semantic_type == element_type or 
                tag == element_type or
                (element_type == 'button' and features.get('is_button')) or
                (element_type == 'link' and features.get('is_link')) or
                (element_type == 'input' and features.get('is_input'))):
                
                filtered_elements.append((element, features))
        
        return filtered_elements
    
    def get_page_summary(self, page: Page) -> Dict[str, Any]:
        """
        Get a summary of all interactive elements on the page.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary with page summary
        """
        elements_data = self.scan_page(page)
        
        summary = {
            'total_elements': len(elements_data),
            'by_tag': {},
            'by_semantic_type': {},
            'by_type': {
                'buttons': 0,
                'inputs': 0,
                'links': 0,
                'other': 0
            },
            'visible_elements': 0,
            'hidden_elements': 0
        }
        
        for element, features in elements_data:
            # Count by tag
            tag = features.get('tag', 'unknown')
            summary['by_tag'][tag] = summary['by_tag'].get(tag, 0) + 1
            
            # Count by semantic type
            semantic_type = features.get('semantic_type', 'unknown')
            summary['by_semantic_type'][semantic_type] = summary['by_semantic_type'].get(semantic_type, 0) + 1
            
            # Count by general type
            if features.get('is_button'):
                summary['by_type']['buttons'] += 1
            elif features.get('is_link'):
                summary['by_type']['links'] += 1
            elif features.get('is_input'):
                summary['by_type']['inputs'] += 1
            else:
                summary['by_type']['other'] += 1
            
            # Count visibility
            if features.get('visible', False):
                summary['visible_elements'] += 1
            else:
                summary['hidden_elements'] += 1
        
        return summary


# Convenience functions
def get_element_features(element: ElementHandle) -> Dict[str, Any]:
    """Quick function to get element features."""
    scanner = ElementScanner()
    return scanner.get_element_features(element)


def scan_page(page: Page, include_hidden: bool = False) -> List[Tuple[ElementHandle, Dict[str, Any]]]:
    """Quick function to scan page elements."""
    scanner = ElementScanner()
    return scanner.scan_page(page, include_hidden)
