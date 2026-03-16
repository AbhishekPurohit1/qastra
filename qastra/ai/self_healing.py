"""
Self-healing locator engine.
"""

from typing import Dict, Any, List, Optional, Tuple
from playwright.sync_api import Page, ElementHandle
import time
import logging

from .similarity import SimilarityScorer
from .locator_store import LocatorStore, create_element_fingerprint


class SelfHealingLocator:
    """Self-healing locator that can find elements even when they change."""
    
    def __init__(self, cache_dir: str = ".qastra_cache"):
        self.locator_store = LocatorStore(cache_dir)
        self.similarity_scorer = SimilarityScorer()
        self.healing_log = []
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def find_element(self, page: Page, url: str, description: str, timeout: int = 5000) -> Optional[ElementHandle]:
        """Find an element with self-healing capability."""
        start_time = time.time()
        
        # Try to get cached locator first
        cached_locator = self.locator_store.get_locator(url, description)
        
        if cached_locator:
            # Try to find element using cached fingerprint
            element = self._find_by_fingerprint(page, cached_locator['fingerprint'])
            if element:
                self.logger.info(f"Found element using cache: {description}")
                return element
            else:
                self.logger.warning(f"Cached locator failed for: {description}")
                # Element changed, try to heal
                healed_element = self._heal_locator(page, url, description, cached_locator['fingerprint'])
                if healed_element:
                    return healed_element
        
        # No cached locator, try to find by description
        element = self._find_by_description(page, description)
        if element:
            # Cache the found element
            fingerprint = self._extract_fingerprint(page, element)
            self.locator_store.store_locator(url, description, fingerprint)
            return element
        
        # Still not found, try healing with basic strategies
        return self._heal_without_cache(page, url, description)
    
    def _find_by_fingerprint(self, page: Page, fingerprint: Dict[str, Any]) -> Optional[ElementHandle]:
        """Find element using its fingerprint."""
        try:
            # Try ID first
            if fingerprint.get('id'):
                element = page.query_selector(f"#{fingerprint['id']}")
                if element and self._verify_fingerprint(element, fingerprint):
                    return element
            
            # Try text content
            if fingerprint.get('text'):
                text = fingerprint['text'].strip()
                if text:
                    # Try exact text match
                    element = page.query_selector(f"text={text}")
                    if element and self._verify_fingerprint(element, fingerprint):
                        return element
                    
                    # Try partial text match
                    element = page.query_selector(f"text={text}")
                    if element and self._verify_fingerprint(element, fingerprint):
                        return element
            
            # Try class
            if fingerprint.get('class'):
                classes = fingerprint['class'].split()
                for class_name in classes:
                    element = page.query_selector(f".{class_name}")
                    if element and self._verify_fingerprint(element, fingerprint):
                        return element
            
            # Try tag + attributes
            tag = fingerprint.get('tag', '')
            if tag:
                selector = tag
                
                # Add other attributes
                if fingerprint.get('name'):
                    selector += f"[name='{fingerprint['name']}']"
                
                if fingerprint.get('type'):
                    selector += f"[type='{fingerprint['type']}']"
                
                if fingerprint.get('placeholder'):
                    selector += f"[placeholder='{fingerprint['placeholder']}']"
                
                element = page.query_selector(selector)
                if element and self._verify_fingerprint(element, fingerprint):
                    return element
        
        except Exception as e:
            self.logger.error(f"Error finding by fingerprint: {e}")
        
        return None
    
    def _find_by_description(self, page: Page, description: str) -> Optional[ElementHandle]:
        """Find element by natural language description."""
        try:
            # Simple text-based lookup
            element = page.query_selector(f"text={description}")
            if element:
                return element
            
            # Try common button/link patterns
            if any(word in description.lower() for word in ['login', 'submit', 'sign', 'button']):
                selectors = [
                    f"button:has-text('{description}')",
                    f"input[type=submit]:has-text('{description}')",
                    f"a:has-text('{description}')",
                    "button[type=submit]",
                    "input[type=submit]"
                ]
                
                for selector in selectors:
                    element = page.query_selector(selector)
                    if element:
                        return element
            
            # Try input fields
            if any(word in description.lower() for word in ['username', 'password', 'email', 'name', 'input']):
                selectors = [
                    f"input[name*='{description.lower()}']",
                    f"input[placeholder*='{description}']",
                    f"input[id*='{description.lower()}']",
                    "input[type=text]",
                    "input[type=password]",
                    "input[type=email]"
                ]
                
                for selector in selectors:
                    element = page.query_selector(selector)
                    if element:
                        return element
        
        except Exception as e:
            self.logger.error(f"Error finding by description: {e}")
        
        return None
    
    def _heal_locator(self, page: Page, url: str, description: str, old_fingerprint: Dict[str, Any]) -> Optional[ElementHandle]:
        """Heal a failed locator by finding similar elements."""
        self.logger.info(f"Attempting to heal locator for: {description}")
        
        # Get all interactive elements from the page
        candidates = self._get_interactive_elements(page)
        
        # Convert to fingerprints for comparison
        candidate_fingerprints = []
        for element in candidates:
            try:
                fingerprint = self._extract_fingerprint(page, element)
                if fingerprint:
                    fingerprint['element'] = element
                    candidate_fingerprints.append(fingerprint)
            except Exception:
                continue
        
        # Find best match
        best_match = self.similarity_scorer.find_best_match(old_fingerprint, candidate_fingerprints)
        
        if best_match and best_match.get('element'):
            element = best_match['element']
            similarity_score = best_match.get('similarity_score', 0)
            
            self.logger.info(f"Healed locator with similarity score: {similarity_score:.2f}")
            
            # Update cache with new fingerprint
            new_fingerprint = self._extract_fingerprint(page, element)
            self.locator_store.update_locator(url, description, new_fingerprint)
            
            # Log healing event
            self._log_healing_event(url, description, old_fingerprint, new_fingerprint, similarity_score)
            
            return element
        
        return None
    
    def _heal_without_cache(self, page: Page, url: str, description: str) -> Optional[ElementHandle]:
        """Heal locator when no cache exists."""
        self.logger.info(f"Attempting to find element without cache: {description}")
        
        # Try broader search strategies
        strategies = [
            # Text-based search
            lambda: page.query_selector(f"text={description}"),
            lambda: page.query_selector(f"*:has-text('{description}')"),
            
            # Attribute-based search
            lambda: page.query_selector(f"[title*='{description}']"),
            lambda: page.query_selector(f"[alt*='{description}']"),
            
            # Common element types
            lambda: page.query_selector("button"),
            lambda: page.query_selector("input[type=submit]"),
            lambda: page.query_selector("a"),
            lambda: page.query_selector("input"),
        ]
        
        for strategy in strategies:
            try:
                elements = strategy()
                if elements:
                    # If multiple elements, try to find the best one
                    if isinstance(elements, list):
                        for element in elements:
                            if self._is_relevant_element(element, description):
                                # Cache the found element
                                fingerprint = self._extract_fingerprint(page, element)
                                self.locator_store.store_locator(url, description, fingerprint)
                                return element
                    else:
                        if self._is_relevant_element(elements, description):
                            # Cache the found element
                            fingerprint = self._extract_fingerprint(page, elements)
                            self.locator_store.store_locator(url, description, fingerprint)
                            return elements
            except Exception:
                continue
        
        return None
    
    def _get_interactive_elements(self, page: Page) -> List[ElementHandle]:
        """Get all interactive elements from the page."""
        selectors = [
            'button', 'input', 'a', 'select', 'textarea',
            '[role="button"]', '[onclick]', '[onsubmit]'
        ]
        
        elements = []
        for selector in selectors:
            try:
                found = page.query_selector_all(selector)
                elements.extend(found)
            except Exception:
                continue
        
        return elements
    
    def _extract_fingerprint(self, page: Page, element: ElementHandle) -> Dict[str, Any]:
        """Extract fingerprint from element."""
        try:
            fingerprint = {
                'tag': element.evaluate("el => el.tagName.toLowerCase()"),
                'text': element.evaluate("el => el.textContent?.trim() || ''"),
                'id': element.get_attribute('id') or '',
                'class': element.get_attribute('class') or '',
                'name': element.get_attribute('name') or '',
                'placeholder': element.get_attribute('placeholder') or '',
                'type': element.get_attribute('type') or '',
                'value': element.get_attribute('value') or '',
                'href': element.get_attribute('href') or '',
                'title': element.get_attribute('title') or '',
                'alt': element.get_attribute('alt') or '',
            }
            
            return fingerprint
        except Exception as e:
            self.logger.error(f"Error extracting fingerprint: {e}")
            return {}
    
    def _verify_fingerprint(self, element: ElementHandle, fingerprint: Dict[str, Any]) -> bool:
        """Verify if element matches the fingerprint."""
        try:
            current_fingerprint = self._extract_fingerprint(element.page, element)
            
            # Check key attributes
            if fingerprint.get('id') and current_fingerprint.get('id') != fingerprint.get('id'):
                return False
            
            if fingerprint.get('text') and fingerprint['text'].lower() not in current_fingerprint.get('text', '').lower():
                return False
            
            if fingerprint.get('tag') and current_fingerprint.get('tag') != fingerprint.get('tag'):
                return False
            
            return True
        except Exception:
            return False
    
    def _is_relevant_element(self, element: ElementHandle, description: str) -> bool:
        """Check if element is relevant to the description."""
        try:
            text = element.evaluate("el => el.textContent?.trim() || ''").lower()
            desc_lower = description.lower()
            
            # Check if description text is in element text
            if desc_lower in text:
                return True
            
            # Check common keywords
            keywords = {
                'login': ['login', 'sign', 'submit'],
                'username': ['username', 'user', 'email', 'name'],
                'password': ['password', 'pass'],
                'submit': ['submit', 'send', 'save', 'continue'],
                'cancel': ['cancel', 'close', 'back'],
            }
            
            for key, words in keywords.items():
                if key in desc_lower:
                    return any(word in text for word in words)
            
            return False
        except Exception:
            return False
    
    def _log_healing_event(self, url: str, description: str, old_fingerprint: Dict[str, Any], 
                          new_fingerprint: Dict[str, Any], similarity_score: float):
        """Log a healing event for reporting."""
        event = {
            'timestamp': time.time(),
            'url': url,
            'description': description,
            'old_fingerprint': old_fingerprint,
            'new_fingerprint': new_fingerprint,
            'similarity_score': similarity_score
        }
        
        self.healing_log.append(event)
        
        # Keep only last 100 events
        if len(self.healing_log) > 100:
            self.healing_log = self.healing_log[-100:]
    
    def get_healing_report(self) -> Dict[str, Any]:
        """Generate a healing report."""
        total_healings = len(self.healing_log)
        
        if total_healings == 0:
            return {
                'total_healings': 0,
                'average_similarity': 0,
                'recent_healings': [],
                'healing_by_url': {}
            }
        
        # Calculate statistics
        similarities = [event['similarity_score'] for event in self.healing_log]
        avg_similarity = sum(similarities) / len(similarities)
        
        # Group by URL
        healing_by_url = {}
        for event in self.healing_log:
            url = event['url']
            if url not in healing_by_url:
                healing_by_url[url] = 0
            healing_by_url[url] += 1
        
        return {
            'total_healings': total_healings,
            'average_similarity': avg_similarity,
            'recent_healings': self.healing_log[-10:],  # Last 10 events
            'healing_by_url': healing_by_url
        }


# Add alias for compatibility
SelfHealingEngine = SelfHealingLocator
