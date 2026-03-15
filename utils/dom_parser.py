"""
DOM parser utility for analyzing web pages.
"""

from bs4 import BeautifulSoup, Tag
from typing import Dict, List, Any, Optional
import re
from urllib.parse import urljoin, urlparse


class DOMParser:
    """Parser for analyzing DOM structure and extracting testable elements."""
    
    def __init__(self, html_content: str, base_url: str = ""):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.base_url = base_url
        self.forms = []
        self.inputs = []
        self.buttons = []
        self.links = []
        self.interactive_elements = []
        
        self._parse_page()
    
    def _parse_page(self):
        """Parse the page and extract relevant elements."""
        self._extract_forms()
        self._extract_inputs()
        self._extract_buttons()
        self._extract_links()
        self._extract_interactive_elements()
    
    def _extract_forms(self):
        """Extract all forms from the page."""
        forms = self.soup.find_all('form')
        
        for form in forms:
            # Handle class attribute properly
            class_attr = form.get('class', '')
            if isinstance(class_attr, list):
                class_attr = ' '.join(class_attr)
            
            form_data = {
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'id': form.get('id', ''),
                'class': class_attr,
                'inputs': [],
                'buttons': [],
                'submit_button': None
            }
            
            # Extract inputs within form
            inputs = form.find_all(['input', 'select', 'textarea'])
            for input_elem in inputs:
                input_data = self._parse_input_element(input_elem)
                if input_data:
                    form_data['inputs'].append(input_data)
            
            # Extract buttons within form
            buttons = form.find_all(['button', 'input[type=submit]', 'input[type=button]'])
            for button in buttons:
                button_data = self._parse_button_element(button)
                if button_data:
                    form_data['buttons'].append(button_data)
                    
                    # Identify submit button
                    if (button.get('type') == 'submit' or 
                        button.get('type') is None or
                        'submit' in button.get_text().lower()):
                        form_data['submit_button'] = button_data
            
            self.forms.append(form_data)
    
    def _extract_inputs(self):
        """Extract all input elements."""
        inputs = self.soup.find_all(['input', 'select', 'textarea'])
        
        for input_elem in inputs:
            input_data = self._parse_input_element(input_elem)
            if input_data:
                self.inputs.append(input_data)
    
    def _extract_buttons(self):
        """Extract all button elements."""
        buttons = self.soup.find_all(['button', 'input[type=submit]', 'input[type=button]'])
        
        for button in buttons:
            button_data = self._parse_button_element(button)
            if button_data:
                self.buttons.append(button_data)
    
    def _extract_links(self):
        """Extract all clickable links."""
        links = self.soup.find_all('a', href=True)
        
        for link in links:
            # Handle class attribute properly
            class_attr = link.get('class', '')
            if isinstance(class_attr, list):
                class_attr = ' '.join(class_attr)
            
            link_data = {
                'text': link.get_text(strip=True),
                'href': link.get('href', ''),
                'id': link.get('id', ''),
                'class': class_attr,
                'title': link.get('title', ''),
                'target': link.get('target', ''),
                'is_external': self._is_external_link(link.get('href', '')),
                'selector': self._generate_selector(link)
            }
            
            if link_data['text'] or link_data['title']:
                self.links.append(link_data)
    
    def _extract_interactive_elements(self):
        """Extract all interactive elements."""
        interactive_selectors = [
            '[onclick]',
            '[onsubmit]', 
            '[onchange]',
            '[role="button"]',
            '[role="link"]',
            '[tabindex]',
            'button',
            'input',
            'select',
            'textarea',
            'a[href]'
        ]
        
        for selector in interactive_selectors:
            try:
                elements = self.soup.select(selector)
                
                for element in elements:
                    # Handle class attribute properly
                    class_attr = element.get('class', '')
                    if isinstance(class_attr, list):
                        class_attr = ' '.join(class_attr)
                    
                    element_data = {
                        'tag': element.name,
                        'text': element.get_text(strip=True),
                        'id': element.get('id', ''),
                        'class': class_attr,
                        'attributes': {k: v for k, v in element.attrs.items() if '=' not in k},
                        'selector': self._generate_selector(element),
                        'is_interactive': True
                    }
                    
                    self.interactive_elements.append(element_data)
            except Exception as e:
                # Skip problematic selectors
                continue
    
    def _parse_input_element(self, element: Tag) -> Optional[Dict[str, Any]]:
        """Parse an input element and extract relevant data."""
        if not element:
            return None
        
        input_type = element.get('type', 'text').lower()
        
        # Handle class attribute properly
        class_attr = element.get('class', '')
        if isinstance(class_attr, list):
            class_attr = ' '.join(class_attr)
        
        input_data = {
            'tag': element.name,
            'type': input_type,
            'name': element.get('name', ''),
            'id': element.get('id', ''),
            'class': class_attr,
            'placeholder': element.get('placeholder', ''),
            'value': element.get('value', ''),
            'required': element.has_attr('required'),
            'disabled': element.has_attr('disabled'),
            'readonly': element.has_attr('readonly'),
            'text': element.get_text(strip=True),
            'selector': self._generate_selector(element),
            'test_value': self._generate_test_value(input_type, element)
        }
        
        # Handle select elements
        if element.name == 'select':
            options = element.find_all('option')
            input_data['options'] = [opt.get('value', opt.get_text(strip=True)) for opt in options if opt.get('value')]
            input_data['test_value'] = input_data['options'][0] if input_data['options'] else ''
        
        # Handle textarea
        elif element.name == 'textarea':
            input_data['test_value'] = 'Test text content'
        
        return input_data
    
    def _parse_button_element(self, element: Tag) -> Optional[Dict[str, Any]]:
        """Parse a button element and extract relevant data."""
        if not element:
            return None
        
        # Handle class attribute properly
        class_attr = element.get('class', '')
        if isinstance(class_attr, list):
            class_attr = ' '.join(class_attr)
        
        button_data = {
            'tag': element.name,
            'type': element.get('type', 'button'),
            'text': element.get_text(strip=True),
            'value': element.get('value', ''),
            'id': element.get('id', ''),
            'class': class_attr,
            'title': element.get('title', ''),
            'disabled': element.has_attr('disabled'),
            'selector': self._generate_selector(element),
            'action_type': self._determine_action_type(element)
        }
        
        return button_data
    
    def _generate_test_value(self, input_type: str, element: Tag) -> str:
        """Generate appropriate test values for different input types."""
        test_values = {
            'text': 'test@example.com',
            'email': 'test@example.com',
            'password': 'TestPassword123',
            'number': '123',
            'tel': '+1234567890',
            'url': 'https://example.com',
            'search': 'search term',
            'date': '2024-01-01',
            'time': '12:00',
            'datetime-local': '2024-01-01T12:00',
            'month': '2024-01',
            'week': '2024-W01',
            'color': '#ff0000',
            'range': '50',
            'file': 'test_file.txt'
        }
        
        # Check for specific patterns in name/id/placeholder
        name = element.get('name', '').lower()
        placeholder = element.get('placeholder', '').lower()
        id_attr = element.get('id', '').lower()
        
        combined_text = f"{name} {placeholder} {id_attr}"
        
        if 'email' in combined_text:
            return 'test@example.com'
        elif 'password' in combined_text or 'pass' in combined_text:
            return 'TestPassword123'
        elif 'username' in combined_text or 'user' in combined_text:
            return 'testuser'
        elif 'phone' in combined_text or 'tel' in combined_text:
            return '+1234567890'
        elif 'name' in combined_text:
            return 'Test User'
        elif 'search' in combined_text:
            return 'search term'
        elif 'address' in combined_text:
            return '123 Test Street'
        
        return test_values.get(input_type, 'test value')
    
    def _determine_action_type(self, element: Tag) -> str:
        """Determine the likely action type of a button."""
        text = element.get_text(strip=True).lower()
        value = element.get('value', '').lower()
        button_type = element.get('type', '').lower()
        
        combined = f"{text} {value} {button_type}"
        
        if any(word in combined for word in ['submit', 'send', 'save', 'continue', 'next']):
            return 'submit'
        elif any(word in combined for word in ['cancel', 'close', 'back', 'previous']):
            return 'cancel'
        elif any(word in combined for word in ['reset', 'clear']):
            return 'reset'
        elif any(word in combined for word in ['login', 'sign', 'log']):
            return 'login'
        elif any(word in combined for word in ['register', 'signup', 'create']):
            return 'register'
        elif any(word in combined for word in ['search', 'find']):
            return 'search'
        elif any(word in combined for word in ['add', 'create', 'new']):
            return 'add'
        elif any(word in combined for word in ['edit', 'modify', 'update']):
            return 'edit'
        elif any(word in combined for word in ['delete', 'remove', 'trash']):
            return 'delete'
        
        return 'click'
    
    def _generate_selector(self, element: Tag) -> str:
        """Generate a CSS selector for an element."""
        if element.get('id'):
            return f"#{element.get('id')}"
        
        class_attr = element.get('class', '')
        if class_attr:
            if isinstance(class_attr, list):
                if class_attr:
                    return f".{class_attr[0]}"
            else:
                classes = class_attr.split()
                if classes:
                    return f".{classes[0]}"
        
        # Generate selector based on tag and attributes
        selector = element.name if element.name else ''
        
        if element.get('name'):
            selector += f"[name='{element.get('name')}']"
        
        if element.get('type'):
            selector += f"[type='{element.get('type')}']"
        
        return selector
    
    def _is_external_link(self, href: str) -> bool:
        """Check if a link is external."""
        if not href or href.startswith('#'):
            return False
        
        if href.startswith(('http://', 'https://')):
            try:
                base_domain = urlparse(self.base_url).netloc
                link_domain = urlparse(href).netloc
                return base_domain != link_domain
            except:
                return True
        
        return False
    
    def get_page_structure(self) -> Dict[str, Any]:
        """Get the complete page structure."""
        return {
            'forms': self.forms,
            'inputs': self.inputs,
            'buttons': self.buttons,
            'links': self.links,
            'interactive_elements': self.interactive_elements,
            'page_info': {
                'title': self.soup.title.get_text(strip=True) if self.soup.title else '',
                'total_forms': len(self.forms),
                'total_inputs': len(self.inputs),
                'total_buttons': len(self.buttons),
                'total_links': len(self.links),
                'total_interactive': len(self.interactive_elements)
            }
        }
    
    def get_testable_elements(self) -> List[Dict[str, Any]]:
        """Get all elements that can be tested."""
        testable = []
        
        # Add forms
        for form in self.forms:
            testable.append({
                'type': 'form',
                'data': form,
                'priority': 'high' if form['submit_button'] else 'medium'
            })
        
        # Add standalone buttons
        for button in self.buttons:
            testable.append({
                'type': 'button',
                'data': button,
                'priority': 'high' if button['action_type'] in ['submit', 'login'] else 'medium'
            })
        
        # Add all links (not just important ones for now)
        for link in self.links:
            testable.append({
                'type': 'link',
                'data': link,
                'priority': 'medium'
            })
        
        # Sort by priority
        testable.sort(key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['priority']])
        
        return testable
    
    def find_element_by_text(self, text: str) -> List[Dict[str, Any]]:
        """Find elements containing specific text."""
        results = []
        text_lower = text.lower()
        
        # Search in all element types
        all_elements = self.forms + self.inputs + self.buttons + self.links + self.interactive_elements
        
        for element in all_elements:
            if isinstance(element, dict) and 'text' in element:
                if text_lower in element['text'].lower():
                    results.append(element)
        
        return results
    
    def find_elements_by_type(self, element_type: str) -> List[Dict[str, Any]]:
        """Find elements by type."""
        type_mapping = {
            'form': self.forms,
            'input': self.inputs,
            'button': self.buttons,
            'link': self.links,
            'interactive': self.interactive_elements
        }
        
        return type_mapping.get(element_type, [])
