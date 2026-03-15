"""
Page Analyzer - AI-powered page structure analysis and element understanding.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from playwright.sync_api import Page, ElementHandle
from dataclasses import dataclass


@dataclass
class Product:
    """Represents a product found on a page."""
    element: ElementHandle
    text: str
    price: Optional[float]
    name: str
    brand: Optional[str]
    rating: Optional[float]
    availability: Optional[str]
    url: Optional[str]


@dataclass
class Form:
    """Represents a form found on a page."""
    element: ElementHandle
    action: str
    method: str
    fields: List[Dict[str, Any]]
    submit_button: Optional[ElementHandle]


@dataclass
class NavigationItem:
    """Represents a navigation item."""
    element: ElementHandle
    text: str
    url: Optional[str]
    type: str  # menu, link, button, etc.


class PageAnalyzer:
    """Analyzes page structure and extracts meaningful information."""
    
    def __init__(self):
        # Product patterns
        self.price_patterns = [
            r'\$(\d+(?:\.\d{2})?)',  # $123.45
            r'(\d+(?:\.\d{2})?)\s*USD',  # 123.45 USD
            r'EUR\s*(\d+(?:\.\d{2})?)',  # EUR 123.45
            r'£(\d+(?:\.\d{2})?)',  # £123.45
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)',  # 1,234.56
        ]
        
        # Rating patterns
        self.rating_patterns = [
            r'(\d+(?:\.\d+)?)\s*\/\s*5',  # 4.5 / 5
            r'(\d+)\s*stars?',  # 4 stars
            r'rating[:\s]*(\d+(?:\.\d+)?)',  # rating: 4.5
        ]
        
        # Brand patterns (common tech brands)
        self.brand_patterns = [
            r'\b(apple|samsung|dell|hp|lenovo|asus|acer|microsoft|sony|lg|toshiba|msi|razer)\b',
            r'\b(iphone|macbook|ipad|galaxy|thinkpad|pavilion|inspiron|vivobook|surface)\b',
        ]
        
        # Product type patterns
        self.product_type_patterns = [
            r'\b(laptop|phone|tablet|desktop|monitor|keyboard|mouse|headphones|speaker|camera)\b',
            r'\b(computer|pc|notebook|smartphone|mobile|display)\b',
        ]
        
        # Action patterns
        self.action_patterns = {
            'buy': r'\b(buy|purchase|order|add to cart|shop|get)\b',
            'search': r'\b(search|find|look for|explore)\b',
            'compare': r'\b(compare|vs|versus)\b',
            'filter': r'\b(filter|sort|refine)\b',
            'navigate': r'\b(go to|navigate|visit|open)\b',
        }
    
    def extract_products(self, page: Page) -> List[Product]:
        """
        Extract products from the current page.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of Product objects
        """
        products = []
        
        # Common product container selectors
        product_selectors = [
            'div[data-product]', '[data-testid*="product"]',
            '.product', '.item', '.card',
            'article', '[role="article"]',
            'li[class*="product"]', 'div[class*="item"]',
            '.search-result', '.listing'
        ]
        
        elements = []
        for selector in product_selectors:
            try:
                found = page.query_selector_all(selector)
                elements.extend(found)
            except:
                continue
        
        # Remove duplicates
        unique_elements = list(set(elements))
        
        for element in unique_elements:
            try:
                product = self._analyze_product_element(element)
                if product:
                    products.append(product)
            except:
                continue
        
        return products
    
    def _analyze_product_element(self, element: ElementHandle) -> Optional[Product]:
        """Analyze a single element to determine if it's a product."""
        try:
            text = element.inner_text().strip()
            if len(text) < 10:  # Skip very short elements
                return None
            
            # Extract price
            price = self._extract_price(text)
            if not price:
                return None  # Only consider elements with prices as products
            
            # Extract product name
            name = self._extract_product_name(text)
            
            # Extract brand
            brand = self._extract_brand(text)
            
            # Extract rating
            rating = self._extract_rating(text)
            
            # Extract availability
            availability = self._extract_availability(text)
            
            # Extract URL
            url = self._extract_url(element)
            
            return Product(
                element=element,
                text=text,
                price=price,
                name=name,
                brand=brand,
                rating=rating,
                availability=availability,
                url=url
            )
        
        except:
            return None
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price from text."""
        for pattern in self.price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    price_str = match.group(1).replace(',', '')
                    return float(price_str)
                except:
                    continue
        return None
    
    def _extract_product_name(self, text: str) -> str:
        """Extract product name from text."""
        # Remove price and other noise
        cleaned = re.sub(r'\$\d+(?:\.\d{2})?', '', text)
        cleaned = re.sub(r'\d+(?:,\d{3})*(?:\.\d{2})?', '', cleaned)
        cleaned = re.sub(r'USD|EUR|GBP|£|\$', '', cleaned)
        cleaned = re.sub(r'star[s]?|rating|out of \d+', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Take first meaningful part (usually the product name)
        parts = cleaned.split()[:8]  # First 8 words
        return ' '.join(parts)
    
    def _extract_brand(self, text: str) -> Optional[str]:
        """Extract brand from text."""
        for pattern in self.brand_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).title()
        return None
    
    def _extract_rating(self, text: str) -> Optional[float]:
        """Extract rating from text."""
        for pattern in self.rating_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        return None
    
    def _extract_availability(self, text: str) -> Optional[str]:
        """Extract availability information."""
        availability_patterns = [
            r'\b(in stock|available|ready to ship|buy now)\b',
            r'\b(out of stock|unavailable|sold out)\b',
            r'\b(pre-order|coming soon|back order)\b',
        ]
        
        for pattern in availability_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).lower()
        return None
    
    def _extract_url(self, element: ElementHandle) -> Optional[str]:
        """Extract URL from element."""
        try:
            # Check if element itself is a link
            href = element.get_attribute('href')
            if href:
                return href
            
            # Check for links inside the element
            link = element.query_selector('a[href]')
            if link:
                return link.get_attribute('href')
            
            # Check for onclick handlers
            onclick = element.get_attribute('onclick')
            if onclick and 'window.location' in onclick:
                # Extract URL from onclick
                match = re.search(r'window\.location\s*=\s*[\'"]([^\'"]+)[\'"]', onclick)
                if match:
                    return match.group(1)
        
        except:
            pass
        
        return None
    
    def extract_forms(self, page: Page) -> List[Form]:
        """Extract forms from the current page."""
        forms = []
        
        try:
            form_elements = page.query_selector_all('form')
            
            for form_element in form_elements:
                form = self._analyze_form_element(form_element)
                if form:
                    forms.append(form)
        
        except:
            pass
        
        return forms
    
    def _analyze_form_element(self, form_element: ElementHandle) -> Optional[Form]:
        """Analyze a form element."""
        try:
            action = form_element.get_attribute('action') or ''
            method = form_element.get_attribute('method') or 'GET'
            
            # Extract fields
            fields = []
            input_elements = form_element.query_selector_all('input, select, textarea')
            
            for input_elem in input_elements:
                field_info = {
                    'type': input_elem.get_attribute('type') or 'text',
                    'name': input_elem.get_attribute('name') or '',
                    'id': input_elem.get_attribute('id') or '',
                    'placeholder': input_elem.get_attribute('placeholder') or '',
                    'required': input_elem.get_attribute('required') is not None,
                    'label': self._get_field_label(input_elem)
                }
                fields.append(field_info)
            
            # Find submit button
            submit_button = form_element.query_selector('button[type="submit"], input[type="submit"]')
            
            return Form(
                element=form_element,
                action=action,
                method=method,
                fields=fields,
                submit_button=submit_button
            )
        
        except:
            return None
    
    def _get_field_label(self, input_element: ElementHandle) -> str:
        """Get label for an input field."""
        try:
            # Check for label element
            input_id = input_element.get_attribute('id')
            if input_id:
                label = input_element.query_selector(f'label[for="{input_id}"]')
                if label:
                    return label.inner_text().strip()
            
            # Check for parent label
            parent = input_element.evaluate('el => el.closest("label")')
            if parent:
                return parent.inner_text().strip()
            
            # Use placeholder as fallback
            placeholder = input_element.get_attribute('placeholder')
            if placeholder:
                return placeholder.strip()
            
            # Use name as fallback
            name = input_element.get_attribute('name')
            if name:
                return name.replace('_', ' ').title()
        
        except:
            pass
        
        return ''
    
    def extract_navigation(self, page: Page) -> List[NavigationItem]:
        """Extract navigation items from the page."""
        navigation = []
        
        # Common navigation selectors
        nav_selectors = [
            'nav a', '.menu a', '.navigation a',
            'header a', '.navbar a', '.nav-link',
            '[role="navigation"] a', '.breadcrumb a'
        ]
        
        elements = []
        for selector in nav_selectors:
            try:
                found = page.query_selector_all(selector)
                elements.extend(found)
            except:
                continue
        
        # Remove duplicates
        unique_elements = list(set(elements))
        
        for element in unique_elements:
            try:
                nav_item = self._analyze_navigation_element(element)
                if nav_item:
                    navigation.append(nav_item)
            except:
                continue
        
        return navigation
    
    def _analyze_navigation_element(self, element: ElementHandle) -> Optional[NavigationItem]:
        """Analyze a navigation element."""
        try:
            text = element.inner_text().strip()
            if len(text) < 1 or len(text) > 100:  # Skip empty or very long elements
                return None
            
            url = element.get_attribute('href')
            
            # Determine type
            element_tag = element.evaluate('el => el.tagName.toLowerCase()')
            parent_tag = element.evaluate('el => el.parentElement?.tagName.toLowerCase()')
            
            nav_type = 'link'
            if parent_tag in ['nav', 'header']:
                nav_type = 'menu'
            elif element_tag == 'button':
                nav_type = 'button'
            
            return NavigationItem(
                element=element,
                text=text,
                url=url,
                type=nav_type
            )
        
        except:
            return None
    
    def analyze_page_type(self, page: Page) -> str:
        """Analyze the page to determine its type."""
        try:
            title = page.title().lower()
            url = page.url.lower()
            content = page.content().lower()
            
            # E-commerce indicators
            ecommerce_indicators = [
                'cart', 'checkout', 'product', 'shop', 'buy', 'price',
                'add to cart', 'wishlist', 'order', 'payment'
            ]
            
            # Search indicators
            search_indicators = [
                'search', 'find', 'results', 'query', 'filter'
            ]
            
            # Form indicators
            form_indicators = [
                'login', 'register', 'signup', 'form', 'submit', 'sign in'
            ]
            
            # Count indicators
            ecommerce_score = sum(1 for indicator in ecommerce_indicators if indicator in content)
            search_score = sum(1 for indicator in search_indicators if indicator in content)
            form_score = sum(1 for indicator in form_indicators if indicator in content)
            
            # Determine page type
            if ecommerce_score >= 3:
                return 'ecommerce'
            elif search_score >= 2:
                return 'search'
            elif form_score >= 2:
                return 'form'
            else:
                return 'general'
        
        except:
            return 'unknown'
    
    def get_page_summary(self, page: Page) -> Dict[str, Any]:
        """Get a comprehensive summary of the page."""
        try:
            page_type = self.analyze_page_type(page)
            
            summary = {
                'url': page.url,
                'title': page.title(),
                'page_type': page_type,
                'products': self.extract_products(page),
                'forms': self.extract_forms(page),
                'navigation': self.extract_navigation(page),
                'analysis_timestamp': re.sub(r'\.\d+', '', str(re.sub(r'T.*', '', str(__import__('datetime').datetime.now()))))
            }
            
            # Add counts
            summary['product_count'] = len(summary['products'])
            summary['form_count'] = len(summary['forms'])
            summary['navigation_count'] = len(summary['navigation'])
            
            return summary
        
        except Exception as e:
            return {
                'error': str(e),
                'url': page.url,
                'title': page.title(),
                'page_type': 'unknown'
            }


# Convenience functions
def extract_products(page: Page) -> List[Product]:
    """Quick function to extract products from a page."""
    analyzer = PageAnalyzer()
    return analyzer.extract_products(page)


def analyze_page(page: Page) -> Dict[str, Any]:
    """Quick function to get comprehensive page analysis."""
    analyzer = PageAnalyzer()
    return analyzer.get_page_summary(page)
