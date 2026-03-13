"""Test case management for Qastra DSL."""

current_test = None

def qastra(name):
    """Define a test case with a name.
    
    Args:
        name (str): The name/description of the test case
    """
    global current_test
    current_test = name
    print(f"\n[Qastra] Running Test: {name}")
    print("=" * 50)
