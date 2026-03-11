"""Cross-browser support for VibeTest."""

from enum import Enum
from vibetest.browser.browser import browser

class BrowserType(Enum):
    CHROME = "chromium"
    FIREFOX = "firefox"
    SAFARI = "webkit"
    EDGE = "msedge"

class CrossBrowser:
    def __init__(self, browser_type=BrowserType.CHROME, headless=False):
        self.browser_type = browser_type
        self.headless = headless
        self.current_browser = None
        
    def start(self):
        """Start the specified browser."""
        if self.current_browser:
            self.stop()
            
        launch_options = {
            "headless": self.headless,
        }
        
        if self.browser_type == BrowserType.FIREFOX:
            launch_options["firefox"] = True
        elif self.browser_type == BrowserType.SAFARI:
            launch_options["webkit"] = True
        elif self.browser_type == BrowserType.EDGE:
            launch_options["msedge"] = True
            
        self.current_browser = browser
        browser.start(launch_options)
        
    def stop(self):
        """Stop the current browser."""
        if self.current_browser:
            browser.stop()
            self.current_browser = None
            
    def restart(self):
        """Restart browser with same settings."""
        self.stop()
        self.start()

def cross_browser_test(test_name, browsers=None, headless=False):
    """Decorator to run tests across multiple browsers."""
    if browsers is None:
        browsers = [BrowserType.CHROME, BrowserType.FIREFOX]
        
    def decorator(test_func):
        def wrapper():
            print(f"\n🌐 Running '{test_name}' across {len(browsers)} browsers...")
            
            for browser_type in browsers:
                print(f"\n--- Testing on {browser_type.value.upper()} ---")
                cb = CrossBrowser(browser_type, headless)
                try:
                    cb.start()
                    test_func()
                    print(f"✅ {browser_type.value.upper()}: PASSED")
                except Exception as e:
                    print(f"❌ {browser_type.value.upper()}: FAILED - {e}")
                finally:
                    cb.stop()
                    
        return wrapper
    return decorator
