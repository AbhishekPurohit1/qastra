"""
Natural Language Parser for Qastra - Converts plain English/Hinglish to test intents.
"""

import re
from typing import Dict, Any, List, Optional


class NLPParser:
    """Natural Language Parser for converting text to test actions."""
    
    def __init__(self):
        # Action patterns for English and Hinglish
        self.patterns = {
            'login': [
                r'login\s+(?:with\s+)?username\s+(\w+)(?:\s+and\s+password\s+(\w+))?',
                r'login\s+(?:with\s+)?user\s+(\w+)(?:\s+and\s+pass\s+(\w+))?',
                r'login\s+karo\s+username\s+(\w+)(?:\s+password\s+(\w+))?',
                r'login\s+karo\s+user\s+(\w+)(?:\s+pass\s+(\w+))?',
                r'sign\s+in\s+(?:with\s+)?username\s+(\w+)(?:\s+and\s+password\s+(\w+))?',
                r'sign\s+up\s+(?:with\s+)?username\s+(\w+)(?:\s+and\s+password\s+(\w+))?',
            ],
            'search': [
                r'search\s+(?:for\s+)?(.+)',
                r'find\s+(.+)',
                r'dhoondho\s+(.+)',
                r'khoj\s+(.+)',
            ],
            'click': [
                r'click\s+(?:on\s+)?(.+)',
                r'press\s+(?:the\s+)?(.+)',
                r'touch\s+(?:the\s+)?(.+)',
                r'dabao\s+(.+)',
                r'click\s+karo\s+(.+)',
            ],
            'fill': [
                r'fill\s+(?:the\s+)?(\w+)\s+(?:with\s+)?(.+)',
                r'enter\s+(.+)\s+in\s+(\w+)',
                r'type\s+(.+)\s+in\s+(\w+)',
                r'bharo\s+(\w+)\s+(?:me\s+)?(.+)',
                r'daalna\s+(\w+)\s+(?:me\s+)?(.+)',
            ],
            'navigate': [
                r'go\s+to\s+(.+)',
                r'open\s+(.+)',
                r'navigate\s+to\s+(.+)',
                r'jaao\s+(.+)',
                r'kholo\s+(.+)',
            ],
            'select': [
                r'select\s+(?:the\s+)?(.+)',
                r'choose\s+(?:the\s+)?(.+)',
                r'pick\s+(?:the\s+)?(.+)',
                'chuno\s+(.+)',
                'select\s+karo\s+(.+)',
            ],
            'wait': [
                r'wait\s+(?:for\s+)?(\d+)\s*(?:seconds?|secs?|s)?',
                r'rukho\s+(?:for\s+)?(\d+)\s*(?:seconds?|secs?|s)?',
                r'wait\s+karo\s+(\d+)\s*(?:seconds?|secs?|s)?',
            ],
            'scroll': [
                r'scroll\s+(?:down|up|left|right)',
                r'scroll\s+(?:down|up|left|right)\s+(\d+)',
                r'scroll\s+karo\s+(?:down|up|left|right)',
            ],
            'assert': [
                r'assert\s+(.+)',
                r'verify\s+(.+)',
                r'check\s+(.+)',
                r'dekho\s+(.+)',
                r'check\s+karo\s+(.+)',
            ]
        }
        
        # Field mappings for common form fields
        self.field_mappings = {
            'username': ['username', 'user', 'email', 'login', 'id'],
            'password': ['password', 'pass', 'pwd', 'secret'],
            'name': ['name', 'fullname', 'firstname', 'lastname'],
            'email': ['email', 'emailaddress', 'mail'],
            'phone': ['phone', 'mobile', 'telephone'],
            'address': ['address', 'location'],
        }
    
    def parse_sentence(self, sentence: str) -> Dict[str, Any]:
        """Parse a natural language sentence into structured intent."""
        sentence = sentence.lower().strip()
        
        # Try each pattern to find the intent
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, sentence)
                if match:
                    return self._extract_intent_data(intent, match, sentence)
        
        # Fallback - try to extract any action
        return self._fallback_parse(sentence)
    
    def _extract_intent_data(self, intent: str, match: re.Match, sentence: str) -> Dict[str, Any]:
        """Extract structured data from pattern match."""
        result = {
            'intent': intent,
            'confidence': 0.8,
            'raw_sentence': sentence,
            'extracted_data': {}
        }
        
        if intent == 'login':
            groups = match.groups()
            if groups[0]:  # username
                result['extracted_data']['username'] = groups[0]
            if groups[1]:  # password
                result['extracted_data']['password'] = groups[1]
        
        elif intent == 'search':
            search_term = match.group(1).strip()
            result['extracted_data']['search_term'] = search_term
        
        elif intent == 'click':
            target = match.group(1).strip()
            result['extracted_data']['target'] = target
        
        elif intent == 'fill':
            field = match.group(1).strip()
            value = match.group(2).strip()
            result['extracted_data']['field'] = field
            result['extracted_data']['value'] = value
        
        elif intent == 'navigate':
            destination = match.group(1).strip()
            result['extracted_data']['destination'] = destination
        
        elif intent == 'select':
            option = match.group(1).strip()
            result['extracted_data']['option'] = option
        
        elif intent == 'wait':
            duration = int(match.group(1))
            result['extracted_data']['duration'] = duration
        
        elif intent == 'scroll':
            direction = match.group(1) if match.lastindex else 'down'
            amount = int(match.group(2)) if match.lastindex > 1 else 1
            result['extracted_data']['direction'] = direction
            result['extracted_data']['amount'] = amount
        
        elif intent == 'assert':
            assertion = match.group(1).strip()
            result['extracted_data']['assertion'] = assertion
        
        return result
    
    def _fallback_parse(self, sentence: str) -> Dict[str, Any]:
        """Fallback parsing when no specific pattern matches."""
        # Try to extract any action-like words
        action_words = ['click', 'fill', 'type', 'enter', 'search', 'find', 'open', 'go', 'select']
        
        for word in action_words:
            if word in sentence:
                return {
                    'intent': 'unknown_action',
                    'confidence': 0.3,
                    'raw_sentence': sentence,
                    'extracted_data': {
                        'action_word': word,
                        'remaining_text': sentence.replace(word, '').strip()
                    }
                }
        
        return {
            'intent': 'unknown',
            'confidence': 0.1,
            'raw_sentence': sentence,
            'extracted_data': {}
        }
    
    def normalize_field_name(self, field: str) -> str:
        """Normalize field names to common form field identifiers."""
        field_lower = field.lower()
        
        for standard_name, variations in self.field_mappings.items():
            if field_lower in variations:
                return standard_name
        
        return field_lower
    
    def parse_multiple_sentences(self, text: str) -> List[Dict[str, Any]]:
        """Parse multiple sentences or commands."""
        # Split by common separators
        sentences = re.split(r'[.!?;]\s*|\n\s*', text)
        results = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                parsed = self.parse_sentence(sentence)
                results.append(parsed)
        
        return results
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents."""
        return list(self.patterns.keys())
    
    def add_pattern(self, intent: str, pattern: str):
        """Add a new pattern for an intent."""
        if intent not in self.patterns:
            self.patterns[intent] = []
        self.patterns[intent].append(pattern)
    
    def is_hinglish(self, sentence: str) -> bool:
        """Check if sentence contains Hinglish words."""
        hinglish_words = ['karo', 'kholo', 'dabao', 'bharo', 'jaao', 'chuno', 'rukho', 'dekho']
        return any(word in sentence.lower() for word in hinglish_words)


# Convenience function for quick parsing
def parse_sentence(sentence: str) -> Dict[str, Any]:
    """Quick parse function."""
    parser = NLPParser()
    return parser.parse_sentence(sentence)


def parse_multiple_sentences(text: str) -> List[Dict[str, Any]]:
    """Quick multiple sentences parse function."""
    parser = NLPParser()
    return parser.parse_multiple_sentences(text)
