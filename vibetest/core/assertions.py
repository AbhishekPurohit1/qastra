from vibetest.browser.browser import browser


def expect(text):

    page_content = browser.page.content()

    if text not in page_content:
        raise Exception(f"{text} not found on page")
