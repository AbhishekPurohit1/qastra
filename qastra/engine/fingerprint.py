"""Element fingerprinting for Qastra self-healing locators."""


def get_fingerprint(element):

    fingerprint = {}

    try:
        fingerprint["tag"] = element.evaluate("el => el.tagName")
    except Exception:
        fingerprint["tag"] = None

    try:
        fingerprint["text"] = element.inner_text()
    except Exception:
        fingerprint["text"] = None

    try:
        fingerprint["class"] = element.get_attribute("class")
    except Exception:
        fingerprint["class"] = None

    try:
        fingerprint["id"] = element.get_attribute("id")
    except Exception:
        fingerprint["id"] = None

    return fingerprint

