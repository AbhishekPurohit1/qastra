from vibetest.browser.browser import browser
from vibetest.engine.locator_engine import find_element


def open_page(url):
    """Open a web page in the browser.
    
    Args:
        url (str): The URL to navigate to
    """
    browser.open(url)


def click(label):

    element = find_element(browser.page, label)

    if element:
        browser.click(element)
    else:
        raise Exception(f"{label} not found")


def type_into(label, value):
    """Type text into an element.
    
    Args:
        label (str): The label/locator for the element
        value (str): The text to type
    """
    element = find_element(browser.page, label)

    if element:
        browser.type(element, value)
    else:
        raise Exception(f"{label} not found")
