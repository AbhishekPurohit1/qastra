from playwright.sync_api import sync_playwright

class Browser:

    def __init__(self):
        self.p = None
        self.browser = None
        self.page = None

    def start(self, options=None):
        """Start browser with optional configuration."""
        if options is None:
            options = {"headless": False}
            
        self.p = sync_playwright().start()
        
        # Support different browsers
        if options.get("firefox"):
            self.browser = self.p.firefox.launch(headless=options.get("headless", False))
        elif options.get("webkit"):
            self.browser = self.p.webkit.launch(headless=options.get("headless", False))
        elif options.get("msedge"):
            self.browser = self.p.msedge.launch(headless=options.get("headless", False))
        else:
            self.browser = self.p.chromium.launch(headless=options.get("headless", False))
            
        self.page = self.browser.new_page()

    def stop(self):
        """Stop browser and cleanup."""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.p:
            self.p.stop()
            
        self.page = None
        self.browser = None
        self.p = None

    def open(self, url):
        if not self.page:
            self.start()
        self.page.goto(url, wait_until="load")
        self.page.wait_for_load_state("load")

    def click(self, element):
        element.click()

    def type(self, element, value):
        element.fill(value)

    def screenshot(self, name="failure.png"):
        self.page.screenshot(path=name)


# Single shared instance so actions and assertions use the same browser
browser = Browser()