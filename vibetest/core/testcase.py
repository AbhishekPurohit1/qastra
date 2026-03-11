"""Test case management for VibeTest DSL."""

current_test = None

def test(name):
    """Define a test case with a name.
    
    Args:
        name (str): The name/description of the test case
    """
    global current_test
    current_test = name
    print(f"\n[VibeTest] Running Test: {name}")
    print("=" * 50)
