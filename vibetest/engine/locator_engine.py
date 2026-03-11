"""
VibeTest locator engine.

Flow:
1. Smart locator scoring (intent-based).
2. If not found → try self-healing based on saved fingerprints.
"""

from vibetest.engine.scorer import score_element
from vibetest.engine.fingerprint import get_fingerprint
from vibetest.utils.history import save_fingerprint, load_fingerprint

# Candidate elements: clickable and focusable (spec)
CANDIDATE_SELECTOR = "button, a, input, textarea, [type=submit], [type=button]"


def _smart_find(page, label):
    if not page or not label or not label.strip():
        return None

    try:
        elements = page.query_selector_all(CANDIDATE_SELECTOR)
    except Exception:
        return None

    best_element = None
    best_score = 0

    for el in elements:
        try:
            score = score_element(el, label)
            if score > best_score:
                best_score = score
                best_element = el
        except Exception:
            continue

    return best_element


def similarity_score(element, fingerprint):

    score = 0

    if not fingerprint:
        return 0

    try:
        if fingerprint.get("tag") and fingerprint["tag"] == element.evaluate("el => el.tagName"):
            score += 30
    except Exception:
        pass

    try:
        text = element.inner_text() or ""
        if fingerprint.get("text") and fingerprint["text"] and fingerprint["text"] in text:
            score += 40
    except Exception:
        pass

    try:
        class_name = element.get_attribute("class") or ""
        if fingerprint.get("class") and fingerprint["class"] and fingerprint["class"] in class_name:
            score += 20
    except Exception:
        pass

    return score


def heal_locator(page, label, fingerprint):

    if not page or not fingerprint:
        return None

    try:
        elements = page.query_selector_all("*")
    except Exception:
        return None

    best = None
    best_score = 0

    for el in elements:
        try:
            score = similarity_score(el, fingerprint)
            if score > best_score:
                best_score = score
                best = el
        except Exception:
            continue

    return best


def find_element(page, label):

    # Step 1: normal smart locator
    element = _smart_find(page, label)

    if element:
        # Save / update fingerprint for future healing
        try:
            fp = get_fingerprint(element)
            save_fingerprint(label, fp)
        except Exception:
            pass
        return element

    # Step 2: try self-healing based on history
    try:
        old_fp = load_fingerprint(label)
    except Exception:
        old_fp = None

    healed = heal_locator(page, label, old_fp)

    if healed:
        try:
            new_fp = get_fingerprint(healed)
            save_fingerprint(label, new_fp)
        except Exception:
            pass

    return healed

