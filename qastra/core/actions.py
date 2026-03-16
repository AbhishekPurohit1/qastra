from qastra.browser.driver import driver
from qastra.engine.locator_engine import find_element


def open_page(url):
    """Open a web page in the browser.
    
    Args:
        url (str): The URL to navigate to
    """
    if not driver.page:
        driver.start()
    driver.open(url)
    if driver.page:
        driver.page.wait_for_load_state("networkidle", timeout=10000)


def click(label):
    if not driver.page:
        driver.start()
    element = find_element(driver.page, label)

    if element:
        driver.click_element(element)
    else:
        raise Exception(f"{label} not found")


def type_into(label, value):
    """Type text into an element.
    
    Args:
        label (str): The label/locator for the element
        value (str): The text to type
    """
    if not driver.page:
        driver.start()
    element = find_element(driver.page, label)

    if element:
        driver.type_into(element, value)
    else:
        raise Exception(f"{label} not found")
