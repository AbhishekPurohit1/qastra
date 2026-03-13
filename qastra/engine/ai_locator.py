"""
AI-Powered Intent Locator Engine - The first real AI feature for Qastra.

This goes beyond smart locators to true AI understanding:
- Natural language processing
- Context awareness  
- Semantic similarity
- Position understanding
"""

import re
from typing import List, Dict, Any
from qastra.engine.scorer import score_element
from qastra.engine.locator_engine import find_element

class AILocator:
    """AI-powered locator that understands natural language intent."""
    
    def __init__(self):
        # Synonym mappings for NLP understanding
        self.synonyms = {
            "login": ["sign in", "submit", "authenticate", "log in"],
            "register": ["sign up", "create account", "join"],
            "search": ["find", "look for", "query"],
            "submit": ["send", "save", "continue", "next"],
            "cancel": ["close", "exit", "back"],
            "menu": ["navigation", "hamburger", "options"],
            "profile": ["account", "user", "settings"],
            "cart": ["basket", "shopping", "checkout"],
            "delete": ["remove", "trash", "clear"],
            "edit": ["modify", "change", "update"]
        }
        
        # Position keywords
        self.position_keywords = {
            "left": ["left", "start", "beginning"],
            "right": ["right", "end"], 
            "top": ["top", "above", "upper"],
            "bottom": ["bottom", "below", "lower"],
            "center": ["center", "middle"]
        }
        
        # Color keywords
        self.color_keywords = {
            "blue": ["blue", "navy", "azure"],
            "red": ["red", "crimson", "ruby"],
            "green": ["green", "emerald", "lime"],
            "yellow": ["yellow", "gold", "amber"],
            "gray": ["gray", "grey", "silver"],
            "black": ["black", "dark"],
            "white": ["white", "light"]
        }

    def understand_intent(self, text: str) -> Dict[str, Any]:
        """Parse natural language intent into structured understanding."""
        intent = {
            "action": None,
            "target": None,
            "position": None,
            "color": None,
            "description": text.lower(),
            "confidence": 0.0
        }
        
        text_lower = text.lower()
        
        # Extract action
        actions = ["click", "type", "select", "hover", "double click"]
        for action in actions:
            if action in text_lower:
                intent["action"] = action
                break
                
        # Extract position
        for position, keywords in self.position_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent["position"] = position
                    break
                    
        # Extract color
        for color, keywords in self.color_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    intent["color"] = color
                    break
                    
        # Extract main target (remove descriptive words)
        target = text_lower
        remove_words = ["button", "field", "input", "link", "the", "a", "an", "on", "in", "at"]
        for word in remove_words:
            target = target.replace(word, "").strip()
            
        # Remove position and color words
        if intent["position"]:
            for keyword in self.position_keywords[intent["position"]]:
                target = target.replace(keyword, "").strip()
                
        if intent["color"]:
            for keyword in self.color_keywords[intent["color"]]:
                target = target.replace(keyword, "").strip()
                
        intent["target"] = target
        
        # Calculate confidence based on specificity
        confidence = 0.5  # Base confidence
        if intent["position"]:
            confidence += 0.2
        if intent["color"]:
            confidence += 0.2
        if len(intent["target"]) > 2:
            confidence += 0.1
            
        intent["confidence"] = min(confidence, 1.0)
        
        return intent

    def expand_synonyms(self, target: str) -> List[str]:
        """Expand target with synonyms for better matching."""
        expanded = [target]
        
        for key, synonyms in self.synonyms.items():
            if key in target:
                expanded.extend(synonyms)
            for synonym in synonyms:
                if synonym in target:
                    expanded.append(key)
                    expanded.extend([s for s in synonyms if s != synonym])
                    
        return list(set(expanded))  # Remove duplicates

    def ai_score_element(self, element, intent: Dict[str, Any]) -> float:
        """AI-powered element scoring with context understanding."""
        score = 0.0
        
        try:
            # Base smart locator score
            base_score = score_element(element, intent["target"])
            score += base_score * 0.6  # 60% weight for base scoring
            
            # NLP synonym matching
            synonyms = self.expand_synonyms(intent["target"])
            for synonym in synonyms:
                element_text = (element.inner_text() or "").lower()
                if synonym in element_text:
                    score += 30  # Bonus for synonym match
                    
            # Context awareness - check surrounding elements
            if intent["position"]:
                position_score = self._calculate_position_score(element, intent["position"])
                score += position_score * 0.2
                
            # Color matching
            if intent["color"]:
                color_score = self._calculate_color_score(element, intent["color"])
                score += color_score * 0.2
                
        except Exception:
            pass
            
        return score

    def _calculate_position_score(self, element, position: str) -> float:
        """Calculate position-based score."""
        try:
            bbox = element.bounding_box()
            if not bbox:
                return 0.0
                
            # Simple position scoring based on viewport
            viewport = element.page.viewport_size or {"width": 1920, "height": 1080}
            
            x_center = bbox["x"] + bbox["width"] / 2
            y_center = bbox["y"] + bbox["height"] / 2
            
            score = 0.0
            
            if position == "left" and x_center < viewport["width"] * 0.3:
                score = 20.0
            elif position == "right" and x_center > viewport["width"] * 0.7:
                score = 20.0
            elif position == "top" and y_center < viewport["height"] * 0.3:
                score = 20.0
            elif position == "bottom" and y_center > viewport["height"] * 0.7:
                score = 20.0
            elif position == "center":
                center_x = viewport["width"] / 2
                center_y = viewport["height"] / 2
                distance = ((x_center - center_x) ** 2 + (y_center - center_y) ** 2) ** 0.5
                if distance < 200:  # Within 200px of center
                    score = 20.0
                    
            return score
            
        except Exception:
            return 0.0

    def _calculate_color_score(self, element, color: str) -> float:
        """Calculate color-based score."""
        try:
            # Check for color in CSS classes
            class_list = element.get_attribute("class") or ""
            if color in class_list.lower():
                return 15.0
                
            # Check for color in styles
            style = element.get_attribute("style") or ""
            if color in style.lower():
                return 15.0
                
            # Check for color in text content
            text = element.inner_text() or ""
            if color in text.lower():
                return 10.0
                
            return 0.0
            
        except Exception:
            return 0.0

    def find_element_ai(self, page, description: str):
        """Find element using AI-powered intent understanding."""
        if not page or not description:
            return None
            
        # Understand the intent
        intent = self.understand_intent(description)
        print(f"🤖 AI Intent: {intent}")
        
        # Get all candidate elements
        from qastra.engine.locator_engine import CANDIDATE_SELECTOR
        elements = page.query_selector_all(CANDIDATE_SELECTOR)
        
        if not elements:
            return None
            
        # Score elements with AI
        best_element = None
        best_score = 0.0
        
        for element in elements:
            try:
                score = self.ai_score_element(element, intent)
                if score > best_score:
                    best_score = score
                    best_element = element
            except Exception:
                continue
                
        # Only return if confidence is high enough
        if best_score > 30 and intent["confidence"] > 0.6:
            print(f"✅ AI found element with score: {best_score:.1f}")
            return best_element
        else:
            print(f"⚠️ AI confidence too low: {best_score:.1f} (intent: {intent['confidence']:.1f})")
            return None

# Global AI locator instance
ai_locator = AILocator()

def find_element_ai(page, description: str):
    """Convenience function for AI-powered element finding."""
    return ai_locator.find_element_ai(page, description)
