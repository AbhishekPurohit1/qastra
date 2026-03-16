"""
Test API - Simple interface for writing Qastra tests.

This module provides the main `test()` function and other utilities
for writing clean, readable tests.
"""

import re
import time
from typing import Optional, Union, Dict, Any

from ..engine.smart_locator import SmartLocator
from ..ai.nlp.executor import NLPExecutor
from ..browser.driver import driver


class TestAPI:
    """Main test API class that handles test execution."""
    
    def __init__(self):
        self.page = None
        self.browser = None
        self.context = None
        self.smart_locator: Optional[SmartLocator] = None
        self.nlp_executor: Optional[NLPExecutor] = None
        self.test_results = []
        
    def setup_browser(self, headless: bool = True):
        """Setup browser and page using the shared driver."""
        if not driver.page:
            driver.start({"headless": headless})

        self.page = driver.page
        self.browser = None
        self.context = None
        self.smart_locator = SmartLocator(self.page)
        self.nlp_executor = NLPExecutor(headless=headless)
    
    def teardown_browser(self):
        """Cleanup browser resources."""
        driver.stop()
        self.page = None
        self.browser = None
        self.context = None
    
    def test(self, instruction: str, timeout: int = 30000) -> Dict[str, Any]:
        """
        Execute a test instruction.
        
        Args:
            instruction: Natural language instruction
            timeout: Timeout in milliseconds
            
        Returns:
            Test result dictionary
        """
        start_time = time.time()
        
        try:
            # Setup browser if not already done
            self.setup_browser()
            
            # Execute instruction using NLP executor
            result = self.nlp_executor.execute_instruction(instruction)
            
            execution_time = (time.time() - start_time) * 1000
            
            test_result = {
                'instruction': instruction,
                'status': 'PASS' if result.get('success', False) else 'FAIL',
                'execution_time': execution_time,
                'actions': result.get('actions', []),
                'errors': result.get('errors', []),
                'timestamp': time.time()
            }
            
            self.test_results.append(test_result)
            return test_result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            test_result = {
                'instruction': instruction,
                'status': 'FAIL',
                'execution_time': execution_time,
                'actions': [],
                'errors': [str(e)],
                'timestamp': time.time()
            }
            
            self.test_results.append(test_result)
            return test_result
    
    def click(self, element: str, timeout: int = 10000) -> bool:
        """
        Click on an element using smart locator.
        
        Args:
            element: Element description or locator
            timeout: Timeout in milliseconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.setup_browser()
            
            # Use smart locator to find element
            located_element = self.smart_locator.locate_element(element, timeout)
            if located_element:
                located_element.click()
                return True
            return False
            
        except Exception as e:
            print(f"❌ Click failed: {e}")
            return False
    
    def fill(self, element: str, value: str, timeout: int = 10000) -> bool:
        """
        Fill an input field using smart locator.
        
        Args:
            element: Element description or locator
            value: Value to fill
            timeout: Timeout in milliseconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.setup_browser()
            
            # Use smart locator to find element
            located_element = self.smart_locator.locate_element(element, timeout)
            if located_element:
                located_element.fill(value)
                return True
            return False
            
        except Exception as e:
            print(f"❌ Fill failed: {e}")
            return False
    
    def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            wait_until: Wait condition ('load', 'domcontentloaded', 'networkidle')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.setup_browser()
            
            self.page.goto(url, wait_until=wait_until)
            return True
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            return False
    
    def wait(self, condition: Union[str, int], timeout: int = 10000) -> bool:
        """
        Wait for a condition.
        
        Args:
            condition: Either timeout in ms or selector to wait for
            timeout: Maximum wait time in milliseconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.page:
                self.setup_browser()
            
            if isinstance(condition, int):
                # Wait for specified time
                self.page.wait_for_timeout(condition)
                return True
            else:
                # Wait for selector
                self.page.wait_for_selector(condition, timeout=timeout)
                return True
                
        except Exception as e:
            print(f"❌ Wait failed: {e}")
            return False
    
    def verify(self, condition: str, timeout: int = 10000) -> bool:
        """
        Verify a condition on the page.
        
        Args:
            condition: Condition to verify (selector, text, etc.)
            timeout: Timeout in milliseconds
            
        Returns:
            True if condition is met, False otherwise
        """
        try:
            if not self.page:
                self.setup_browser()
            
            # Check if condition is a selector
            if condition.startswith(('#', '.', '[', '//')):
                element = self.page.query_selector(condition)
                return element is not None
            
            # Check if condition is text on page
            page_text = self.page.inner_text('body')
            return condition in page_text
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def get_test_results(self) -> list:
        """Get all test results."""
        return self.test_results.copy()
    
    def clear_results(self):
        """Clear test results."""
        self.test_results.clear()


# Global test API instance
_test_api = TestAPI()


# Global functions for easy access
def test(instruction: str, timeout: int = 30000) -> Dict[str, Any]:
    """
    Execute a test instruction.
    
    Args:
        instruction: Natural language instruction
        timeout: Timeout in milliseconds
        
    Returns:
        Test result dictionary
        
    Example:
        test("open https://example.com")
        test("login with username admin password 123")
        test("click login button")
    """
    try:
        return _test_api.test(instruction, timeout)
    except Exception as e:
        return {
            'instruction': instruction,
            'status': 'FAIL',
            'execution_time': 0,
            'actions': [],
            'errors': [str(e)],
            'timestamp': time.time()
        }


def click(element: str, timeout: int = 10000) -> bool:
    """
    Click on an element.
    
    Args:
        element: Element description
        timeout: Timeout in milliseconds
        
    Returns:
        True if successful
        
    Example:
        click("login button")
        click("#submit")
        click("text=Submit")
    """
    return _test_api.click(element, timeout)


def fill(element: str, value: str, timeout: int = 10000) -> bool:
    """
    Fill an input field.
    
    Args:
        element: Element description
        value: Value to fill
        timeout: Timeout in milliseconds
        
    Returns:
        True if successful
        
    Example:
        fill("username", "admin")
        fill("#password", "123")
        fill("email input", "test@example.com")
    """
    return _test_api.fill(element, value, timeout)


def navigate(url: str, wait_until: str = "networkidle") -> bool:
    """
    Navigate to a URL.
    
    Args:
        url: URL to navigate to
        wait_until: Wait condition
        
    Returns:
        True if successful
        
    Example:
        navigate("https://example.com")
        navigate("https://github.com")
    """
    return _test_api.navigate(url, wait_until)


def wait(condition: Union[str, int], timeout: int = 10000) -> bool:
    """
    Wait for a condition.
    
    Args:
        condition: Timeout in ms or selector
        timeout: Maximum wait time
        
    Returns:
        True if successful
        
    Example:
        wait(2000)  # Wait 2 seconds
        wait("#loading")  # Wait for element
    """
    return _test_api.wait(condition, timeout)


def verify(condition: str, timeout: int = 10000) -> bool:
    """
    Verify a condition.
    
    Args:
        condition: Condition to verify
        timeout: Timeout in milliseconds
        
    Returns:
        True if condition is met
        
    Example:
        verify("Welcome")
        verify("#dashboard")
        verify("text=Success")
    """
    return _test_api.verify(condition, timeout)


def setup(headless: bool = True):
    """Setup browser manually."""
    _test_api.setup_browser(headless)


def teardown():
    """Cleanup browser resources."""
    _test_api.teardown_browser()


def get_results() -> list:
    """Get all test results."""
    return _test_api.get_test_results()


def clear_results():
    """Clear test results."""
    _test_api.clear_results()


# Context manager for easy setup/teardown
class QastraTest:
    """Context manager for Qastra tests."""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
    
    def __enter__(self):
        setup(self.headless)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        teardown()
