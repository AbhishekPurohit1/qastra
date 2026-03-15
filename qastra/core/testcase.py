"""Test case management for Qastra DSL."""

current_test = None

def qastra(func_or_name):
    """Define a test case with a name or decorate a function.
    
    Can be used as:
    @qastra
    def test_func():
        pass
        
    or:
    
    qastra("Test Name")
    """
    global current_test
    
    if callable(func_or_name):
        # Used as decorator without name
        func = func_or_name
        current_test = func.__name__
        print(f"\n[Qastra] Running Test: {current_test}")
        print("=" * 50)
        return func
    else:
        # Used with name parameter
        name = func_or_name
        current_test = name
        print(f"\n[Qastra] Running Test: {name}")
        print("=" * 50)
        def decorator(func):
            return func
        return decorator
