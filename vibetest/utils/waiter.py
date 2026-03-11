import time


def wait_for_element(find_func, timeout=10):

    start = time.time()

    while time.time() - start < timeout:

        element = find_func()

        if element:
            return element

        time.sleep(0.5)

    return None

