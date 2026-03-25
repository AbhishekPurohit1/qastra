from qastra.browser.driver import driver
from qastra.engine.locator_engine import find_element


def open_page(url):
    """Open a web page in the browser.
    
    Args:
        url (str): The URL to navigate to
    """
    # Check if page is provided from runner
    import sys
    page = sys.modules.get('__main__').globals().get('page') if hasattr(sys.modules.get('__main__'), 'globals') else None
    
    if page:
        # Use page provided by runner
        page.goto(url)
        page.wait_for_load_state("networkidle", timeout=10000)
    else:
        # Use driver
        if not driver.page:
            driver.start()
        driver.open(url)
        if driver.page:
            driver.page.wait_for_load_state("networkidle", timeout=10000)


def click(label):
    # Check if page is provided from runner
    import sys
    page = sys.modules.get('__main__').globals().get('page') if hasattr(sys.modules.get('__main__'), 'globals') else None
    
    if page:
        # Use page provided by runner
        element = find_element(page, label)
        if element:
            element.click()
        else:
            raise Exception(f"{label} not found")
    else:
        # Use driver
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
    # Check if page is provided from runner
    import sys
    page = sys.modules.get('__main__').globals().get('page') if hasattr(sys.modules.get('__main__'), 'globals') else None
    
    if page:
        # Use page provided by runner
        element = find_element(page, label)
        if element:
            element.fill(value)
        else:
            raise Exception(f"{label} not found")
    else:
        # Use driver
        if not driver.page:
            driver.start()
        element = find_element(driver.page, label)

        if element:
            driver.type_into(element, value)
        else:
            raise Exception(f"{label} not found")
