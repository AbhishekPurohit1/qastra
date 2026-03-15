"""
Locator store for caching element fingerprints.
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib


class LocatorStore:
    """Stores and manages element locator cache."""
    
    def __init__(self, cache_dir: str = ".qastra_cache"):
        self.cache_dir = cache_dir
        self.locators_file = os.path.join(cache_dir, "locators.json")
        self.locators = self._load_locators()
    
    def _load_locators(self) -> Dict[str, Any]:
        """Load locators from cache file."""
        if not os.path.exists(self.locators_file):
            return {}
        
        try:
            with open(self.locators_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    def _save_locators(self):
        """Save locators to cache file."""
        os.makedirs(self.cache_dir, exist_ok=True)
        
        try:
            with open(self.locators_file, 'w') as f:
                json.dump(self.locators, f, indent=2)
        except IOError:
            pass
    
    def _generate_locator_key(self, url: str, element_description: str) -> str:
        """Generate a unique key for a locator."""
        content = f"{url}:{element_description}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def store_locator(self, url: str, element_description: str, element_fingerprint: Dict[str, Any]):
        """Store an element fingerprint in the cache."""
        key = self._generate_locator_key(url, element_description)
        
        locator_entry = {
            'url': url,
            'description': element_description,
            'fingerprint': element_fingerprint,
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'usage_count': 1
        }
        
        self.locators[key] = locator_entry
        self._save_locators()
    
    def get_locator(self, url: str, element_description: str) -> Optional[Dict[str, Any]]:
        """Retrieve a locator from the cache."""
        key = self._generate_locator_key(url, element_description)
        
        if key in self.locators:
            # Update usage statistics
            self.locators[key]['last_used'] = datetime.now().isoformat()
            self.locators[key]['usage_count'] += 1
            self._save_locators()
            
            return self.locators[key]
        
        return None
    
    def update_locator(self, url: str, element_description: str, new_fingerprint: Dict[str, Any]):
        """Update an existing locator with new fingerprint."""
        key = self._generate_locator_key(url, element_description)
        
        if key in self.locators:
            self.locators[key]['fingerprint'] = new_fingerprint
            self.locators[key]['last_updated'] = datetime.now().isoformat()
            self._save_locators()
    
    def find_similar_locators(self, url: str, element_fingerprint: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find locators with similar fingerprints."""
        similar_locators = []
        
        for key, locator in self.locators.items():
            if locator['url'] == url:
                # Simple similarity check based on text and tag
                fingerprint = locator['fingerprint']
                
                text_match = (
                    element_fingerprint.get('text', '').lower() == 
                    fingerprint.get('text', '').lower()
                )
                
                tag_match = (
                    element_fingerprint.get('tag', '') == 
                    fingerprint.get('tag', '')
                )
                
                if text_match or tag_match:
                    similar_locators.append(locator)
        
        return similar_locators
    
    def get_all_locators(self) -> Dict[str, Any]:
        """Get all cached locators."""
        return self.locators.copy()
    
    def clear_cache(self):
        """Clear all cached locators."""
        self.locators = {}
        self._save_locators()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_locators = len(self.locators)
        
        if total_locators == 0:
            return {
                'total_locators': 0,
                'urls': {},
                'most_used': None,
                'recently_used': None
            }
        
        urls = {}
        most_used = None
        recently_used = None
        max_usage = 0
        latest_time = None
        
        for locator in self.locators.values():
            url = locator['url']
            urls[url] = urls.get(url, 0) + 1
            
            usage = locator.get('usage_count', 0)
            if usage > max_usage:
                max_usage = usage
                most_used = locator
            
            last_used = locator.get('last_used', '')
            if last_used and (not latest_time or last_used > latest_time):
                latest_time = last_used
                recently_used = locator
        
        return {
            'total_locators': total_locators,
            'urls': urls,
            'most_used': most_used,
            'recently_used': recently_used
        }


def create_element_fingerprint(element) -> Dict[str, Any]:
    """Create a fingerprint for a DOM element."""
    fingerprint = {
        'tag': element.name.lower() if element.name else '',
        'text': element.get_text(strip=True) if hasattr(element, 'get_text') else '',
        'id': element.get('id', '') if element else '',
        'class': element.get('class', '') if element else '',
        'name': element.get('name', '') if element else '',
        'placeholder': element.get('placeholder', '') if element else '',
        'type': element.get('type', '') if element else '',
        'value': element.get('value', '') if element else '',
        'href': element.get('href', '') if element else '',
        'action': element.get('action', '') if element else '',
        'method': element.get('method', '') if element else '',
    }
    
    # Clean up class attribute
    if isinstance(fingerprint['class'], list):
        fingerprint['class'] = ' '.join(fingerprint['class'])
    
    return fingerprint
