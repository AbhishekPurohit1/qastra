"""
Natural Language Test Executor - Executes parsed intents using Qastra framework.
"""

import time
from typing import Any, Dict, List, Tuple, Optional

from .parser import NLPParser
from .intent_engine import IntentEngine
from ..self_healing import SelfHealingLocator
from ...browser.driver import driver


class NLPExecutor:
    """Executes natural language tests using Qastra framework."""
    
    def __init__(self, headless: bool = True, cache_dir: str = ".qastra_cache"):
        self.headless = headless
        self.cache_dir = cache_dir
        self.parser = NLPParser()
        self.intent_engine = IntentEngine()
        self.self_healing = SelfHealingLocator(cache_dir)
        self.execution_log = []
    
    def execute_test(self, sentence: str, url: Optional[str] = None) -> Dict[str, Any]:
        """Execute a natural language test sentence."""
        start_time = time.time()
        
        result = {
            'sentence': sentence,
            'status': 'unknown',
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'actions_performed': [],
            'errors': [],
            'parsed_intent': None,
            'generated_actions': None
        }
        
        try:
            # Parse the sentence
            parsed_intent = self.parser.parse_sentence(sentence)
            result['parsed_intent'] = parsed_intent
            
            # Get actions from intent
            actions = self.intent_engine.get_actions(parsed_intent)
            result['generated_actions'] = actions
            
            # Validate actions
            valid_actions = self.intent_engine.validate_actions(actions)
            
            if not valid_actions:
                result['status'] = 'no_actions'
                result['errors'].append('No valid actions generated')
                return result
            
            # Ensure browser is running
            if not driver.page:
                driver.start({"headless": self.headless})

            page = driver.page

            # Navigate to URL if provided
            if url:
                page.goto(url, wait_until="networkidle")
                result['actions_performed'].append(f"Navigated to {url}")
            else:
                # Try to extract URL from actions
                for action in valid_actions:
                    if action[0] == 'navigate':
                        page.goto(action[1], wait_until="networkidle")
                        result['actions_performed'].append(f"Navigated to {action[1]}")
                        break
                else:
                    # Default to example.com if no URL provided
                    page.goto("https://example.com", wait_until="networkidle")
                    result['actions_performed'].append("Navigated to default URL: https://example.com")

            # Execute each action
            for action in valid_actions:
                success = self._execute_action(page, action, url or "https://example.com")
                if success:
                    action_desc = self.intent_engine.get_action_descriptions([action])[0]
                    result['actions_performed'].append(f"✅ {action_desc}")
                else:
                    action_desc = self.intent_engine.get_action_descriptions([action])[0]
                    result['actions_performed'].append(f"❌ {action_desc}")
                    result['errors'].append(f"Failed to execute: {action_desc}")

            result['status'] = 'completed'
        
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(f"Execution error: {e}")
        
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
            self.execution_log.append(result)
        
        return result
    
    def _execute_action(self, page: Any, action: Tuple, url: str) -> bool:
        """Execute a single action using Qastra framework."""
        action_type = action[0]
        
        try:
            if action_type == 'fill':
                selectors = action[1]
                value = action[2]
                
                # Try each selector with self-healing
                for selector in selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            element.fill(value)
                            return True
                    except:
                        # Try self-healing
                        healed_element = self.self_healing.find_element(page, url, selector)
                        if healed_element:
                            healed_element.fill(value)
                            return True
                return False
            
            elif action_type == 'click':
                selectors = action[1]
                
                # Try each selector with self-healing
                for selector in selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            element.click()
                            page.wait_for_load_state("networkidle", timeout=3000)
                            return True
                    except:
                        # Try self-healing
                        healed_element = self.self_healing.find_element(page, url, selector)
                        if healed_element:
                            healed_element.click()
                            page.wait_for_load_state("networkidle", timeout=3000)
                            return True
                return False
            
            elif action_type == 'navigate':
                url = action[1]
                page.goto(url, wait_until="networkidle")
                return True
            
            elif action_type == 'select':
                selectors = action[1]
                
                for selector in selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            element.click()
                            return True
                    except:
                        # Try self-healing
                        healed_element = self.self_healing.find_element(page, url, selector)
                        if healed_element:
                            healed_element.click()
                            return True
                return False
            
            elif action_type == 'wait':
                duration = action[1]
                page.wait_for_timeout(duration)
                return True
            
            elif action_type == 'scroll':
                direction = action[1]
                amount = action[2] if len(action) > 2 else 1
                
                for _ in range(amount):
                    if direction == 'down':
                        page.keyboard.press('PageDown')
                    elif direction == 'up':
                        page.keyboard.press('PageUp')
                    elif direction == 'left':
                        page.keyboard.press('ArrowLeft')
                    elif direction == 'right':
                        page.keyboard.press('ArrowRight')
                    
                    page.wait_for_timeout(500)
                
                return True
            
            elif action_type == 'assert':
                assertion = action[1]
                # Simple assertion check
                page_content = page.content()
                if assertion.lower() in page_content.lower():
                    return True
                return False
            
            elif action_type == 'log':
                message = action[1]
                print(f"LOG: {message}")
                return True
            
            return False
        
        except Exception as e:
            print(f"Error executing action {action}: {e}")
            return False
    
    def execute_multiple_sentences(self, text: str, url: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute multiple sentences."""
        parsed_sentences = self.parser.parse_multiple_sentences(text)
        results = []
        
        for parsed in parsed_sentences:
            result = self.execute_test(parsed['raw_sentence'], url)
            results.append(result)
        
        return results
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of all executions."""
        if not self.execution_log:
            return {
                'total_executions': 0,
                'successful': 0,
                'failed': 0,
                'average_duration': 0,
                'most_common_intents': {}
            }
        
        total = len(self.execution_log)
        successful = len([r for r in self.execution_log if r['status'] == 'completed'])
        failed = total - successful
        
        durations = [r['duration'] for r in self.execution_log if r.get('duration')]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Count intents
        intents = {}
        for result in self.execution_log:
            if result.get('parsed_intent'):
                intent = result['parsed_intent'].get('intent', 'unknown')
                intents[intent] = intents.get(intent, 0) + 1
        
        return {
            'total_executions': total,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total * 100) if total > 0 else 0,
            'average_duration': avg_duration,
            'most_common_intents': intents
        }
    
    def print_execution_result(self, result: Dict[str, Any]):
        """Print execution result in a readable format."""
        print(f"\n🧠 Natural Language Test Execution")
        print(f"{'='*50}")
        print(f"Sentence: {result['sentence']}")
        
        if result['parsed_intent']:
            intent = result['parsed_intent']
            print(f"Detected Intent: {intent['intent']} (confidence: {intent['confidence']:.2f})")
            
            if intent['extracted_data']:
                print(f"Extracted Data: {intent['extracted_data']}")
        
        print(f"Status: {result['status'].upper()}")
        print(f"Duration: {result['duration']:.2f}s")
        
        if result['actions_performed']:
            print(f"\nActions Performed:")
            for action in result['actions_performed']:
                print(f"  {action}")
        
        if result['errors']:
            print(f"\nErrors:")
            for error in result['errors']:
                print(f"  ❌ {error}")
        
        if result['status'] == 'completed':
            print(f"\n✅ Test completed successfully!")
        else:
            print(f"\n❌ Test failed!")


# Convenience function for quick execution
def execute_test(sentence: str, url: Optional[str] = None, headless: bool = True) -> Dict[str, Any]:
    """Quick function to execute a natural language test."""
    executor = NLPExecutor(headless=headless)
    result = executor.execute_test(sentence, url)
    executor.print_execution_result(result)
    return result


def execute_multiple_sentences(text: str, url: Optional[str] = None, headless: bool = True) -> List[Dict[str, Any]]:
    """Quick function to execute multiple sentences."""
    executor = NLPExecutor(headless=headless)
    results = executor.execute_multiple_sentences(text, url)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Test {i} ---")
        executor.print_execution_result(result)
    
    return results
