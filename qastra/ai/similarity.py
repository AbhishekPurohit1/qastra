"""
Similarity scoring system for self-healing locators.
"""

from difflib import SequenceMatcher
from typing import Dict, Any, List
import re


class SimilarityScorer:
    """Calculates similarity scores between elements."""
    
    def __init__(self):
        self.tag_weights = {
            'button': 1.0,
            'input': 1.0,
            'a': 1.0,
            'select': 0.9,
            'textarea': 0.9,
            'div': 0.7,
            'span': 0.6
        }
    
    def text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using SequenceMatcher."""
        if not text1 or not text2:
            return 0.0
        
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        return SequenceMatcher(None, text1, text2).ratio()
    
    def partial_similarity(self, text1: str, text2: str) -> float:
        """Calculate partial text similarity."""
        if not text1 or not text2:
            return 0.0
        
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()
        
        # Check if one text contains the other
        if text1 in text2 or text2 in text1:
            return 0.8
        
        # Check for partial matches
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def class_similarity(self, class1: str, class2: str) -> float:
        """Calculate class similarity."""
        if not class1 or not class2:
            return 0.0
        
        classes1 = set(class1.split())
        classes2 = set(class2.split())
        
        if not classes1 or not classes2:
            return 0.0
        
        intersection = classes1.intersection(classes2)
        union = classes1.union(classes2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def id_similarity(self, id1: str, id2: str) -> float:
        """Calculate ID similarity."""
        if not id1 or not id2:
            return 0.0
        
        if id1 == id2:
            return 1.0
        
        # Partial ID matches
        if id1 in id2 or id2 in id1:
            return 0.7
        
        # Check for similar patterns (e.g., submit-btn vs submit-button)
        id1_parts = set(re.split(r'[-_]', id1))
        id2_parts = set(re.split(r'[-_]', id2))
        
        intersection = id1_parts.intersection(id2_parts)
        union = id1_parts.union(id2_parts)
        
        return len(intersection) / len(union) if union else 0.0
    
    def tag_similarity(self, tag1: str, tag2: str) -> float:
        """Calculate tag similarity."""
        if tag1 == tag2:
            return 1.0
        
        # Some tags are functionally similar
        similar_tags = {
            'button': ['input[type=submit]', 'input[type=button]'],
            'input': ['textarea', 'select'],
            'a': ['button'],
        }
        
        if tag1 in similar_tags and tag2 in similar_tags[tag1]:
            return 0.8
        
        if tag2 in similar_tags and tag1 in similar_tags[tag2]:
            return 0.8
        
        return 0.0
    
    def calculate_similarity(self, element1: Dict[str, Any], element2: Dict[str, Any]) -> float:
        """Calculate overall similarity score between two elements."""
        score = 0.0
        total_weight = 0.0
        
        # Text similarity (highest weight)
        text_weight = 0.4
        text_sim = self.text_similarity(
            element1.get('text', ''), 
            element2.get('text', '')
        )
        score += text_sim * text_weight
        total_weight += text_weight
        
        # Tag similarity
        tag_weight = 0.2
        tag_sim = self.tag_similarity(
            element1.get('tag', ''), 
            element2.get('tag', '')
        )
        score += tag_sim * tag_weight
        total_weight += tag_weight
        
        # Class similarity
        class_weight = 0.15
        class_sim = self.class_similarity(
            element1.get('class', ''), 
            element2.get('class', '')
        )
        score += class_sim * class_weight
        total_weight += class_weight
        
        # ID similarity
        id_weight = 0.15
        id_sim = self.id_similarity(
            element1.get('id', ''), 
            element2.get('id', '')
        )
        score += id_sim * id_weight
        total_weight += id_weight
        
        # Partial text similarity (bonus)
        partial_weight = 0.1
        partial_sim = self.partial_similarity(
            element1.get('text', ''), 
            element2.get('text', '')
        )
        score += partial_sim * partial_weight
        total_weight += partial_weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def find_best_match(self, target_element: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the best matching element from candidates."""
        if not candidates:
            return None
        
        best_match = None
        best_score = 0.0
        
        for candidate in candidates:
            score = self.calculate_similarity(target_element, candidate)
            candidate['similarity_score'] = score
            
            if score > best_score:
                best_score = score
                best_match = candidate
        
        # Only return matches above threshold
        if best_score >= 0.6:
            return best_match
        
        return None
