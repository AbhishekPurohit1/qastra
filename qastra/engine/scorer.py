"""
Smart Locator Scoring — the brain of Qastra.
Scores elements by: text, aria-label, placeholder, element type, visibility.
Formula: ELEMENT SCORE = text_score + aria_score + placeholder_score + attribute_score + visibility_score
"""

# Spec weights (exact from Qastra design)
SCORE_EXACT_TEXT = 50
SCORE_PARTIAL_TEXT = 30
SCORE_ARIA_LABEL = 40
SCORE_PLACEHOLDER = 40
SCORE_ELEMENT_TYPE = 20  # button, a, input[type=submit]
SCORE_VISIBLE = 10


def score_element(element, label):
    """
    Score a single element against the user's label (intent).
    Whichever element gets highest score wins.
    """
    score = 0
    label_lower = label.lower()

    # 1. Text matching — exact = +50, partial = +30
    try:
        text = element.inner_text()
        if text is not None:
            text = text.strip()
            text_lower = text.lower()
            
            # Exact match
            if label_lower == text_lower:
                score += SCORE_EXACT_TEXT
            # Partial match in both directions
            elif label_lower in text_lower:
                score += SCORE_PARTIAL_TEXT
            elif text_lower in label_lower:
                score += SCORE_PARTIAL_TEXT
            # Word-level matching for phrases
            elif any(word in text_lower for word in label_lower.split() if len(word) > 2):
                score += 15
    except Exception:
        pass

    # 2. ARIA attributes — aria-label contains keyword = +40
    try:
        aria = element.get_attribute("aria-label")
        if aria and label_lower in aria.lower():
            score += SCORE_ARIA_LABEL
    except Exception:
        pass

    # 3. Placeholder (for inputs) — placeholder match = +40
    try:
        placeholder = element.get_attribute("placeholder")
        if placeholder and label_lower in placeholder.lower():
            score += SCORE_PLACEHOLDER
    except Exception:
        pass

    # 3.5. Name attribute — for form inputs = +35
    try:
        name = element.get_attribute("name")
        if name and label_lower in name.lower():
            score += 35
    except Exception:
        pass

    # 3.6. ID attribute — exact match = +45
    try:
        element_id = element.get_attribute("id")
        if element_id and label_lower == element_id.lower():
            score += 45
        elif element_id and label_lower in element_id.lower():
            score += 25
    except Exception:
        pass

    # 4. Element type — button, a, input, textarea = +20
    try:
        tag = (element.evaluate("e => e.tagName") or "").lower()
        type_attr = (element.get_attribute("type") or "").lower()
        if tag in ("button", "a", "input", "textarea") or type_attr == "submit":
            score += SCORE_ELEMENT_TYPE
    except Exception:
        pass

    # 5. Visibility — visible element = +10
    try:
        if element.is_visible():
            score += SCORE_VISIBLE
    except Exception:
        pass

    return score
