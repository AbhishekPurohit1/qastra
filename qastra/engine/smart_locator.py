"""
Smart Locator Engine - Finds elements by intent using advanced matching algorithms.
"""

from typing import Dict, List, Any, Optional, Tuple
from difflib import SequenceMatcher
import re

from .element_scanner import ElementScanner


class SmartLocator:
    """Advanced element locator that finds elements by user intent."""
    
    def __init__(self, confidence_threshold: float = 0.3):
        self.confidence_threshold = confidence_threshold
        self.scanner = ElementScanner()
        
        # Intent synonyms for better matching
        self.synonyms = {
            'login': ['login', 'signin', 'sign in', 'log in', 'authenticate', 'sign-in'],
            'register': ['register', 'signup', 'sign up', 'create', 'join', 'sign-up'],
            'submit': ['submit', 'send', 'save', 'continue', 'proceed', 'confirm'],
            'cancel': ['cancel', 'close', 'back', 'exit', 'dismiss', 'abort'],
            'search': ['search', 'find', 'lookup', 'query', 'explore'],
            'click': ['click', 'press', 'tap', 'select', 'choose'],
            'username': ['username', 'user', 'email', 'login', 'id', 'account'],
            'password': ['password', 'pass', 'pwd', 'secret', 'key'],
            'checkout': ['checkout', 'buy', 'purchase', 'pay', 'order'],
            'cart': ['cart', 'basket', 'bag', 'shopping'],
            'menu': ['menu', 'navigation', 'nav', 'hamburger'],
            'home': ['home', 'homepage', 'main', 'start'],
        }
        
        # Weights for different matching criteria
        self.weights = {
            'exact_text_match': 10,
            'partial_text_match': 8,
            'exact_id_match': 9,
            'partial_id_match': 6,
            'exact_placeholder_match': 8,
            'partial_placeholder_match': 5,
            'exact_name_match': 7,
            'partial_name_match': 4,
            'class_match': 3,
            'semantic_match': 6,
            'synonym_match': 7,
            'keyword_match': 2,
        }
    
    def find_element(self, page, intent: str, element_type: Optional[str] = None) -> Tuple[Optional[Any], Dict[str, Any]]:
        """
        Find the best matching element for given intent.
        
        Args:
            page: Playwright page object
            intent: User intent (e.g., "login", "username")
            element_type: Optional element type filter
            
        Returns:
            Tuple of (element, match_info)
        """
        # Scan page elements
        if element_type:
            elements_data = self.scanner.scan_elements_by_type(page, element_type)
        else:
            elements_data = self.scanner.scan_page(page)
        
        if not elements_data:
            return None, {'error': 'No elements found on page'}
        
        # Find best match
        best_element = None
        best_score = 0
        best_match_info = {}
        
        for element, features in elements_data:
            score, match_info = self._calculate_match_score(intent, features)
            
            if score > best_score:
                best_score = score
                best_element = element
                best_match_info = match_info
                best_match_info['score'] = score
                best_match_info['features'] = features
        
        # Check if confidence threshold is met
        if best_score < self.confidence_threshold:
            return None, {
                'error': f'No element found with sufficient confidence for intent: {intent}',
                'best_score': best_score,
                'threshold': self.confidence_threshold
            }
        
        best_match_info['confidence'] = 'high' if best_score > 0.7 else 'medium' if best_score > 0.4 else 'low'
        
        return best_element, best_match_info
    
    def _calculate_match_score(self, intent: str, features: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate match score between intent and element features.
        
        Args:
            intent: User intent
            features: Element features
            
        Returns:
            Tuple of (score, match_info)
        """
        score = 0
        match_info = {
            'matches': [],
            'intent': intent,
            'max_possible_score': sum(self.weights.values())
        }
        
        intent_lower = intent.lower()
        intent_clean = self._clean_text(intent)
        
        # Text matching
        text = features.get('text_clean', '')
        if text:
            if intent_lower == text:
                score += self.weights['exact_text_match']
                match_info['matches'].append(('exact_text_match', text, self.weights['exact_text_match']))
            elif intent_lower in text:
                score += self.weights['partial_text_match']
                match_info['matches'].append(('partial_text_match', text, self.weights['partial_text_match']))
            elif self._fuzzy_match(intent_clean, text) > 0.7:
                score += self.weights['partial_text_match'] * 0.8
                match_info['matches'].append(('fuzzy_text_match', text, self.weights['partial_text_match'] * 0.8))
        
        # ID matching
        element_id = features.get('id_clean', '')
        if element_id:
            if intent_lower in element_id:
                if intent_lower == element_id:
                    score += self.weights['exact_id_match']
                    match_info['matches'].append(('exact_id_match', element_id, self.weights['exact_id_match']))
                else:
                    score += self.weights['partial_id_match']
                    match_info['matches'].append(('partial_id_match', element_id, self.weights['partial_id_match']))
        
        # Placeholder matching
        placeholder = features.get('placeholder', '').lower()
        if placeholder:
            if intent_lower == placeholder:
                score += self.weights['exact_placeholder_match']
                match_info['matches'].append(('exact_placeholder_match', placeholder, self.weights['exact_placeholder_match']))
            elif intent_lower in placeholder:
                score += self.weights['partial_placeholder_match']
                match_info['matches'].append(('partial_placeholder_match', placeholder, self.weights['partial_placeholder_match']))
        
        # Name matching
        name = features.get('name', '').lower()
        if name:
            if intent_lower == name:
                score += self.weights['exact_name_match']
                match_info['matches'].append(('exact_name_match', name, self.weights['exact_name_match']))
            elif intent_lower in name:
                score += self.weights['partial_name_match']
                match_info['matches'].append(('partial_name_match', name, self.weights['partial_name_match']))
        
        # Class matching
        class_attr = features.get('class_clean', '')
        if class_attr:
            if intent_lower in class_attr:
                score += self.weights['class_match']
                match_info['matches'].append(('class_match', class_attr, self.weights['class_match']))
        
        # Semantic type matching
        semantic_type = features.get('semantic_type', '')
        if semantic_type and semantic_type != 'unknown':
            if intent_lower == semantic_type:
                score += self.weights['semantic_match']
                match_info['matches'].append(('semantic_match', semantic_type, self.weights['semantic_match']))
        
        # Synonym matching
        for main_term, synonyms in self.synonyms.items():
            if intent_lower in [s.lower() for s in synonyms]:
                if semantic_type == main_term:
                    score += self.weights['synonym_match']
                    match_info['matches'].append(('synonym_match', main_term, self.weights['synonym_match']))
                    break
        
        # Keyword matching
        keywords = features.get('keywords', [])
        for keyword in keywords:
            if intent_lower == keyword:
                score += self.weights['keyword_match']
                match_info['matches'].append(('keyword_match', keyword, self.weights['keyword_match']))
        
        # Normalize score
        max_score = match_info['max_possible_score']
        normalized_score = score / max_score if max_score > 0 else 0
        
        match_info['raw_score'] = score
        match_info['normalized_score'] = normalized_score
        
        return normalized_score, match_info
    
    def _clean_text(self, text: str) -> str:
        """Clean text for matching."""
        if not text:
            return ""
        
        # Remove special characters and normalize
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip().lower()
    
    def _fuzzy_match(self, text1: str, text2: str) -> float:
        """Calculate fuzzy match ratio between two texts."""
        if not text1 or not text2:
            return 0.0
        
        return SequenceMatcher(None, text1, text2).ratio()
    
    def find_all_matches(self, page, intent: str, max_results: int = 5) -> List[Tuple[Any, Dict[str, Any]]]:
        """
        Find all matching elements for given intent.
        
        Args:
            page: Playwright page object
            intent: User intent
            max_results: Maximum number of results to return
            
        Returns:
            List of tuples (element, match_info) sorted by score
        """
        elements_data = self.scanner.scan_page(page)
        
        matches = []
        for element, features in elements_data:
            score, match_info = self._calculate_match_score(intent, features)
            
            if score > 0.1:  # Minimum threshold for inclusion
                matches.append((element, match_info))
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x[1]['normalized_score'], reverse=True)
        
        return matches[:max_results]
    
    def explain_match(self, intent: str, features: Dict[str, Any]) -> str:
        """
        Generate human-readable explanation of why an element matches.
        
        Args:
            intent: User intent
            features: Element features
            
        Returns:
            Explanation string
        """
        score, match_info = self._calculate_match_score(intent, features)
        
        if not match_info['matches']:
            return f"No strong matches found for '{intent}'"
        
        explanations = []
        for match_type, value, weight in match_info['matches']:
            if match_type == 'exact_text_match':
                explanations.append(f"Exact text match: '{value}'")
            elif match_type == 'partial_text_match':
                explanations.append(f"Partial text match: '{value}' contains '{intent}'")
            elif match_type == 'exact_id_match':
                explanations.append(f"Exact ID match: '{value}'")
            elif match_type == 'semantic_match':
                explanations.append(f"Semantic type match: {value}")
            elif match_type == 'synonym_match':
                explanations.append(f"Synonym match: '{intent}' matches {value}")
            elif match_type == 'keyword_match':
                explanations.append(f"Keyword match: '{value}'")
        
        confidence = match_info['normalized_score']
        confidence_desc = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
        
        explanation = f"Match confidence: {confidence_desc} ({confidence:.2f})\n"
        explanation += "Reasons:\n" + "\n".join(f"  - {exp}" for exp in explanations)
        
        return explanation
    
    def add_synonyms(self, term: str, synonyms: List[str]):
        """Add new synonyms for a term."""
        term_lower = term.lower()
        if term_lower not in self.synonyms:
            self.synonyms[term_lower] = []
        
        self.synonyms[term_lower].extend([s.lower() for s in synonyms])
    
    def set_weight(self, match_type: str, weight: float):
        """Set weight for a specific match type."""
        if match_type in self.weights:
            self.weights[match_type] = weight
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intent terms."""
        return list(self.synonyms.keys())
    
    def benchmark_page(self, page) -> Dict[str, Any]:
        """
        Benchmark the smart locator on current page.
        
        Args:
            page: Playwright page object
            
        Returns:
            Benchmark results
        """
        elements_data = self.scanner.scan_page(page)
        
        benchmark = {
            'total_elements': len(elements_data),
            'elements_with_text': 0,
            'elements_with_id': 0,
            'elements_with_placeholder': 0,
            'semantic_elements': 0,
            'average_keywords': 0,
            'test_intents': []
        }
        
        total_keywords = 0
        
        for element, features in elements_data:
            if features.get('has_text'):
                benchmark['elements_with_text'] += 1
            if features.get('id'):
                benchmark['elements_with_id'] += 1
            if features.get('placeholder'):
                benchmark['elements_with_placeholder'] += 1
            if features.get('semantic_type') != 'unknown':
                benchmark['semantic_elements'] += 1
            
            keywords = features.get('keywords', [])
            total_keywords += len(keywords)
        
        if elements_data:
            benchmark['average_keywords'] = total_keywords / len(elements_data)
        
        # Test common intents
        test_intents = ['login', 'username', 'password', 'submit', 'search', 'menu']
        for intent in test_intents:
            element, match_info = self.find_element(page, intent)
            benchmark['test_intents'].append({
                'intent': intent,
                'found': element is not None,
                'score': match_info.get('normalized_score', 0)
            })
        
        return benchmark

def debug_find_attempts(self, intent: str) -> List[Dict[str, Any]]:
    """
    Debug method to show all locator attempts for an intent.
    
    Args:
        intent: The intent string to search for
        
    Returns:
        List of attempts with scores and elements
    """
    attempts = []
    
    # Get all candidate elements
    elements = self.scanner.scan_page(self.page)
    
    for element in elements:
        try:
            score, explanations = self._calculate_score(element, intent)
            attempts.append({
                'element': self._get_element_description(element),
                'score': score,
                'explanations': explanations
            })
        except Exception:
            continue
    
    # Sort by score (highest first)
    attempts.sort(key=lambda x: x['score'], reverse=True)
    return attempts[:5]  # Return top 5 attempts

def _get_element_description(self, element) -> str:
    """Get a human-readable description of an element."""
    try:
        tag = element.evaluate("el => el.tagName")
        text = element.inner_text() or ""
        text = text[:20] + "..." if len(text) > 20 else text
        id_attr = element.get_attribute("id") or ""
        class_attr = element.get_attribute("class") or ""
        
        if id_attr:
            return f"{tag}#{id_attr}"
        elif class_attr:
            classes = class_attr.split()[:2]  # First 2 classes
            return f"{tag}.{'.'.join(classes)}"
        elif text:
            return f"{tag}[text='{text}']"
        else:
            return tag
            
    except Exception:
        return "unknown"


# Convenience functions
def find_element(page, intent: str, element_type: Optional[str] = None) -> Tuple[Optional[Any], Dict[str, Any]]:
    """Quick function to find element by intent."""
    locator = SmartLocator()
    return locator.find_element(page, intent, element_type)

def find_all_matches(page, intent: str, max_results: int = 5) -> List[Tuple[Any, Dict[str, Any]]]:
    """Quick function to find all matching elements."""
    locator = SmartLocator()
    return locator.find_all_matches(page, intent, max_results)
