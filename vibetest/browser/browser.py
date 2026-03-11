from playwright.sync_api import sync_playwright

class Browser:

    def __init__(self):

        self.p = sync_playwright().start()

        self.browser = self.p.chromium.launch(
            headless=False
        )

        self.page = self.browser.new_page()

    def open(self, url):
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