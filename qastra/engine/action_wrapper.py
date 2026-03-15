"""
Action Wrapper - User-friendly API for interacting with elements using smart locators.
"""

from typing import Optional, Dict, Any, List
import time

from .smart_locator import SmartLocator
from ..ai.self_healing import SelfHealingLocator


class ActionWrapper:
    """High-level action wrapper that combines smart locator with self-healing."""
    
    def __init__(self, confidence_threshold: float = 0.3, enable_healing: bool = True):
        self.smart_locator = SmartLocator(confidence_threshold)
        self.enable_healing = enable_healing
        self.healing_engine = SelfHealingLocator() if enable_healing else None
        self.action_log = []
    
    def click(self, page, intent: str, timeout: int = 5000) -> Dict[str, Any]:
        """
        Click an element by intent.
        
        Args:
            page: Playwright page object
            intent: User intent (e.g., "login", "submit", "menu")
            timeout: Timeout in milliseconds
            
        Returns:
            Action result dictionary
        """
        start_time = time.time()
        result = {
            'action': 'click',
            'intent': intent,
            'status': 'unknown',
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'error': None,
            'method': None
        }
        
        try:
            # Try smart locator first
            element, match_info = self.smart_locator.find_element(page, intent, 'button')
            
            if element:
                element.click()
                result['status'] = 'success'
                result['method'] = 'smart_locator'
                result['match_info'] = match_info
                print(f"✅ Clicked {intent} (smart locator, confidence: {match_info.get('confidence', 'unknown')})")
            
            else:
                # Try self-healing if enabled
                if self.healing_engine:
                    healed_element = self.healing_engine.find_element(page, page.url, intent)
                    if healed_element:
                        healed_element.click()
                        result['status'] = 'success'
                        result['method'] = 'self_healing'
                        print(f"✅ Clicked {intent} (self-healing)")
                    else:
                        result['status'] = 'failed'
                        result['error'] = f"Element not found for intent: {intent}"
                        print(f"❌ Failed to click {intent} - element not found")
                else:
                    result['status'] = 'failed'
                    result['error'] = f"Element not found for intent: {intent}"
                    print(f"❌ Failed to click {intent} - element not found")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error clicking {intent}: {e}")
        
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
            self.action_log.append(result)
        
        return result
    
    def fill(self, page, intent: str, value: str, timeout: int = 5000) -> Dict[str, Any]:
        """
        Fill an input field by intent.
        
        Args:
            page: Playwright page object
            intent: User intent (e.g., "username", "email", "password")
            value: Value to fill
            timeout: Timeout in milliseconds
            
        Returns:
            Action result dictionary
        """
        start_time = time.time()
        result = {
            'action': 'fill',
            'intent': intent,
            'value': value,
            'status': 'unknown',
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'error': None,
            'method': None
        }
        
        try:
            # Try smart locator first
            element, match_info = self.smart_locator.find_element(page, intent, 'input')
            
            if element:
                element.fill(value)
                result['status'] = 'success'
                result['method'] = 'smart_locator'
                result['match_info'] = match_info
                print(f"✅ Filled {intent} with '{value}' (smart locator, confidence: {match_info.get('confidence', 'unknown')})")
            
            else:
                # Try self-healing if enabled
                if self.healing_engine:
                    healed_element = self.healing_engine.find_element(page, page.url, intent)
                    if healed_element:
                        healed_element.fill(value)
                        result['status'] = 'success'
                        result['method'] = 'self_healing'
                        print(f"✅ Filled {intent} with '{value}' (self-healing)")
                    else:
                        result['status'] = 'failed'
                        result['error'] = f"Input field not found for intent: {intent}"
                        print(f"❌ Failed to fill {intent} - field not found")
                else:
                    result['status'] = 'failed'
                    result['error'] = f"Input field not found for intent: {intent}"
                    print(f"❌ Failed to fill {intent} - field not found")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error filling {intent}: {e}")
        
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
            self.action_log.append(result)
        
        return result
    
    def select(self, page, intent: str, value: str, timeout: int = 5000) -> Dict[str, Any]:
        """
        Select an option from a dropdown by intent.
        
        Args:
            page: Playwright page object
            intent: User intent (e.g., "country", "state", "language")
            value: Value to select
            timeout: Timeout in milliseconds
            
        Returns:
            Action result dictionary
        """
        start_time = time.time()
        result = {
            'action': 'select',
            'intent': intent,
            'value': value,
            'status': 'unknown',
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'error': None,
            'method': None
        }
        
        try:
            # Try smart locator first
            element, match_info = self.smart_locator.find_element(page, intent, 'select')
            
            if element:
                element.select_option(value)
                result['status'] = 'success'
                result['method'] = 'smart_locator'
                result['match_info'] = match_info
                print(f"✅ Selected '{value}' in {intent} (smart locator, confidence: {match_info.get('confidence', 'unknown')})")
            
            else:
                result['status'] = 'failed'
                result['error'] = f"Select element not found for intent: {intent}"
                print(f"❌ Failed to select in {intent} - element not found")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error selecting in {intent}: {e}")
        
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
            self.action_log.append(result)
        
        return result
    
    def wait_for(self, page, intent: str, timeout: int = 5000) -> Dict[str, Any]:
        """
        Wait for an element to appear by intent.
        
        Args:
            page: Playwright page object
            intent: User intent to wait for
            timeout: Timeout in milliseconds
            
        Returns:
            Action result dictionary
        """
        start_time = time.time()
        result = {
            'action': 'wait_for',
            'intent': intent,
            'status': 'unknown',
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'error': None,
            'timeout': timeout
        }
        
        try:
            # Poll for element
            end_time = start_time + (timeout / 1000)
            
            while time.time() < end_time:
                element, match_info = self.smart_locator.find_element(page, intent)
                
                if element:
                    result['status'] = 'success'
                    result['method'] = 'smart_locator'
                    result['match_info'] = match_info
                    print(f"✅ Found {intent} after {(time.time() - start_time):.2f}s")
                    break
                
                time.sleep(0.1)  # Poll every 100ms
            
            if result['status'] == 'unknown':
                result['status'] = 'timeout'
                result['error'] = f"Timeout waiting for element: {intent}"
                print(f"⏰ Timeout waiting for {intent}")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error waiting for {intent}: {e}")
        
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
            self.action_log.append(result)
        
        return result
    
    def get_text(self, page, intent: str) -> Dict[str, Any]:
        """
        Get text content of an element by intent.
        
        Args:
            page: Playwright page object
            intent: User intent
            
        Returns:
            Action result dictionary
        """
        start_time = time.time()
        result = {
            'action': 'get_text',
            'intent': intent,
            'status': 'unknown',
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'error': None,
            'text': None,
            'method': None
        }
        
        try:
            element, match_info = self.smart_locator.find_element(page, intent)
            
            if element:
                text = element.inner_text()
                result['status'] = 'success'
                result['text'] = text
                result['method'] = 'smart_locator'
                result['match_info'] = match_info
                print(f"✅ Got text from {intent}: '{text}'")
            else:
                result['status'] = 'failed'
                result['error'] = f"Element not found for intent: {intent}"
                print(f"❌ Failed to get text from {intent} - element not found")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error getting text from {intent}: {e}")
        
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
            self.action_log.append(result)
        
        return result
    
    def is_visible(self, page, intent: str) -> Dict[str, Any]:
        """
        Check if an element is visible by intent.
        
        Args:
            page: Playwright page object
            intent: User intent
            
        Returns:
            Action result dictionary
        """
        start_time = time.time()
        result = {
            'action': 'is_visible',
            'intent': intent,
            'status': 'success',
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'error': None,
            'visible': False,
            'method': None
        }
        
        try:
            element, match_info = self.smart_locator.find_element(page, intent)
            
            if element:
                result['visible'] = element.is_visible()
                result['method'] = 'smart_locator'
                result['match_info'] = match_info
                print(f"✅ {intent} is {'visible' if result['visible'] else 'not visible'}")
            else:
                result['visible'] = False
                result['method'] = 'not_found'
                print(f"❌ {intent} not found - assuming not visible")
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"❌ Error checking visibility of {intent}: {e}")
        
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
            self.action_log.append(result)
        
        return result
    
    def get_action_summary(self) -> Dict[str, Any]:
        """
        Get summary of all actions performed.
        
        Returns:
            Action summary dictionary
        """
        if not self.action_log:
            return {
                'total_actions': 0,
                'successful': 0,
                'failed': 0,
                'average_duration': 0,
                'methods': {}
            }
        
        total = len(self.action_log)
        successful = len([a for a in self.action_log if a['status'] == 'success'])
        failed = total - successful
        
        durations = [a['duration'] for a in self.action_log if a.get('duration')]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        methods = {}
        for action in self.action_log:
            method = action.get('method', 'unknown')
            methods[method] = methods.get(method, 0) + 1
        
        return {
            'total_actions': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'average_duration': avg_duration,
            'methods': methods
        }
    
    def print_action_summary(self):
        """Print a formatted action summary."""
        summary = self.get_action_summary()
        
        print(f"\n📊 Action Summary")
        print(f"{'='*40}")
        print(f"Total actions: {summary['total_actions']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Average duration: {summary['average_duration']:.2f}s")
        
        if summary['methods']:
            print(f"\nMethods used:")
            for method, count in summary['methods'].items():
                print(f"  {method}: {count}")


# Global action wrapper instance
_default_wrapper = None


def get_action_wrapper(confidence_threshold: float = 0.3, enable_healing: bool = True) -> ActionWrapper:
    """Get or create default action wrapper."""
    global _default_wrapper
    if _default_wrapper is None:
        _default_wrapper = ActionWrapper(confidence_threshold, enable_healing)
    return _default_wrapper


# Convenience functions for quick usage
def click(page, intent: str, timeout: int = 5000) -> Dict[str, Any]:
    """Quick click function."""
    wrapper = get_action_wrapper()
    return wrapper.click(page, intent, timeout)


def fill(page, intent: str, value: str, timeout: int = 5000) -> Dict[str, Any]:
    """Quick fill function."""
    wrapper = get_action_wrapper()
    return wrapper.fill(page, intent, value, timeout)


def select(page, intent: str, value: str, timeout: int = 5000) -> Dict[str, Any]:
    """Quick select function."""
    wrapper = get_action_wrapper()
    return wrapper.select(page, intent, value, timeout)


def wait_for(page, intent: str, timeout: int = 5000) -> Dict[str, Any]:
    """Quick wait function."""
    wrapper = get_action_wrapper()
    return wrapper.wait_for(page, intent, timeout)


def get_text(page, intent: str) -> Dict[str, Any]:
    """Quick get text function."""
    wrapper = get_action_wrapper()
    return wrapper.get_text(page, intent)


def is_visible(page, intent: str) -> Dict[str, Any]:
    """Quick is visible function."""
    wrapper = get_action_wrapper()
    return wrapper.is_visible(page, intent)
