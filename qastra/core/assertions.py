"""Advanced assertions for Qastra E2E testing."""

import time
from qastra.browser.browser import browser

class Expect:
    """Advanced expectation class for E2E testing."""
    
    def __init__(self, actual):
        self.actual = actual
        
    def to_be_visible(self, timeout=5000):
        """Expect element to be visible."""
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            try:
                if self.actual and self.actual.is_visible():
                    print(f"✅ Element is visible")
                    return self
            except:
                pass
            time.sleep(0.1)
        raise AssertionError(f"Element not visible within {timeout}ms")
        
    def to_contain_text(self, text, timeout=5000):
        """Expect element to contain specific text."""
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            try:
                if self.actual and text in (self.actual.inner_text() or ""):
                    print(f"✅ Element contains text: '{text}'")
                    return self
            except:
                pass
            time.sleep(0.1)
        raise AssertionError(f"Element does not contain text '{text}' within {timeout}ms")
        
    def to_have_attribute(self, attr, value, timeout=5000):
        """Expect element to have specific attribute."""
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            try:
                if self.actual and self.actual.get_attribute(attr) == value:
                    print(f"✅ Element has attribute '{attr}'='{value}'")
                    return self
            except:
                pass
            time.sleep(0.1)
        raise AssertionError(f"Element does not have attribute '{attr}'='{value}' within {timeout}ms")
        
    def to_be_enabled(self, timeout=5000):
        """Expect element to be enabled."""
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            try:
                if self.actual and not self.actual.is_disabled():
                    print(f"✅ Element is enabled")
                    return self
            except:
                pass
            time.sleep(0.1)
        raise AssertionError(f"Element not enabled within {timeout}ms")

def expect(element):
    """Create expectation for element."""
    if isinstance(element, str):
        # Legacy support for string expectations
        page_content = browser.page.content()
        if element not in page_content:
            raise Exception(f"{element} not found on page")
        return Expect(None)
    return Expect(element)

def expect_page_title(title, timeout=5000):
    """Expect page to have specific title."""
    start_time = time.time()
    while time.time() - start_time < timeout / 1000:
        try:
            if browser.page and browser.page.title() == title:
                print(f"✅ Page title is: '{title}'")
                return True
        except:
            pass
        time.sleep(0.1)
    raise AssertionError(f"Page title not '{title}' within {timeout}ms")

def expect_url(url, timeout=5000):
    """Expect page to have specific URL."""
    start_time = time.time()
    while time.time() - start_time < timeout / 1000:
        try:
            if browser.page and url in browser.page.url:
                print(f"✅ Page URL contains: '{url}'")
                return True
        except:
            pass
        time.sleep(0.1)
    raise AssertionError(f"Page URL does not contain '{url}' within {timeout}ms")

def expect_page_title_contains(title, timeout=5000):
    """Expect page title to contain specific text."""
    start_time = time.time()
    while time.time() - start_time < timeout / 1000:
        try:
            if browser.page and title in browser.page.title():
                print(f"✅ Page title contains: '{title}'")
                return True
        except:
            pass
        time.sleep(0.1)
    raise AssertionError(f"Page title does not contain '{title}' within {timeout}ms")

def wait_for_element(label, timeout=5000):
    """Wait for element to appear."""
    from qastra.engine.locator_engine import find_element
    start_time = time.time()
    while time.time() - start_time < timeout / 1000:
        element = find_element(browser.page, label)
        if element:
            print(f"✅ Element found: '{label}'")
            return element
        time.sleep(0.1)
    raise AssertionError(f"Element '{label}' not found within {timeout}ms")
