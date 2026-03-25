"""
AI test generator from web pages.
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from playwright.sync_api import Page, Browser
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.dom_parser import DOMParser


class AITestGenerator:
    """Generates Playwright test scripts from web pages automatically."""
    
    def __init__(self, output_dir: str = "generated_tests"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        self.test_templates = {
            'basic_test': '''#!/usr/bin/env python3
"""
Auto-generated test for {page_title}
Generated on: {timestamp}
"""

from playwright.sync_api import sync_playwright

def test_{test_name}():
    """Auto-generated test for {page_title}."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to page
            page.goto("{url}")
            page.wait_for_load_state("networkidle")
            
{test_steps}
            
            print("✅ Test completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {{e}}")
            raise
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_{test_name}()
''',
            'form_test': '''#!/usr/bin/env python3
"""
Auto-generated form test for {page_title}
Generated on: {timestamp}
"""

from playwright.sync_api import sync_playwright

def test_{test_name}():
    """Auto-generated form test for {page_title}."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to page
            page.goto("{url}")
            page.wait_for_load_state("networkidle")
            
{form_steps}
            
            print("✅ Form test completed successfully!")
            
        except Exception as e:
            print(f"❌ Form test failed: {{e}}")
            raise
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_{test_name}()
'''
        }
    
    def generate_test_from_url(self, browser: Browser, url: str, test_name: Optional[str] = None) -> str:
        """Generate a test script from a URL."""
        page = browser.new_page()
        
        try:
            # Navigate to the page
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(2000)  # Wait for dynamic content
            
            # Get page content
            html_content = page.content()
            page_title = page.title()
            
            # Parse DOM
            parser = DOMParser(html_content, url)
            page_structure = parser.get_page_structure()
            testable_elements = parser.get_testable_elements()
            
            # Generate test name if not provided
            if not test_name:
                test_name = self._generate_test_name(url, page_title)
            
            # Generate test steps
            test_steps = self._generate_test_steps(testable_elements, parser)
            
            # Choose template and generate test
            template = self._choose_template(testable_elements)
            test_content = template.format(
                page_title=page_title,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                test_name=test_name,
                url=url,
                test_steps=test_steps,
                form_steps=test_steps  # Same for form template
            )
            
            # Save test file
            test_file = os.path.join(self.output_dir, f"{test_name}.py")
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            print(f"✅ Generated test: {test_file}")
            
            # Generate test metadata
            metadata = {
                'url': url,
                'page_title': page_title,
                'test_name': test_name,
                'generated_at': datetime.now().isoformat(),
                'elements_found': len(testable_elements),
                'page_structure': page_structure
            }
            
            metadata_file = os.path.join(self.output_dir, f"{test_name}_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return test_file
            
        finally:
            page.close()
    
    def _generate_test_name(self, url: str, page_title: str) -> str:
        """Generate a test name from URL and title."""
        # Extract domain from URL
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace('www.', '')
        # Replace dots with underscores to make valid function names
        domain = domain.replace('.', '_')
        
        # Clean title
        clean_title = ''.join(c for c in page_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_').replace('-', '_')
        
        # Combine domain and title
        test_name = f"{domain}_{clean_title}"
        
        # Limit length and ensure valid filename
        test_name = test_name[:50]
        if not test_name[0].isalpha():
            test_name = f"test_{test_name}"
        
        return test_name
    
    def _generate_test_steps(self, testable_elements: List[Dict[str, Any]], parser: DOMParser) -> str:
        """Generate test steps based on page elements."""
        steps = []
        indent = "            "
        
        for element in testable_elements[:10]:  # Limit to first 10 elements
            element_type = element['type']
            element_data = element['data']
            
            if element_type == 'form':
                steps.extend(self._generate_form_steps(element_data, indent))
            elif element_type == 'button':
                steps.append(self._generate_button_step(element_data, indent))
            elif element_type == 'link':
                steps.append(self._generate_link_step(element_data, indent))
        
        return '\n'.join(steps) if steps else f'{indent}print("No testable elements found")'
    
    def _generate_form_steps(self, form_data: Dict[str, Any], indent: str) -> List[str]:
        """Generate test steps for a form."""
        steps = []
        
        # Add form identification
        form_id = form_data.get('id', '')
        if form_id:
            steps.append(f'{indent}# Fill form: #{form_id}')
        else:
            steps.append(f'{indent}# Fill form')
        
        # Fill inputs
        for input_elem in form_data.get('inputs', []):
            if input_elem.get('type') != 'hidden':
                step = self._generate_input_step(input_elem, indent)
                steps.append(step)
        
        # Submit form
        submit_button = form_data.get('submit_button')
        if submit_button:
            step = self._generate_button_step(submit_button, indent, comment="Submit form")
            steps.append(step)
        elif form_data.get('action'):
            steps.append(f'{indent}# Form would submit to: {form_data["action"]}')
        
        steps.append('')  # Add blank line
        
        return steps
    
    def _generate_input_step(self, input_data: Dict[str, Any], indent: str) -> str:
        """Generate a test step for an input element."""
        input_type = input_data.get('type', 'text')
        selector = input_data.get('selector', '')
        test_value = input_data.get('test_value', 'test value')
        
        # Add comment
        comment = f"# Fill {input_type} input"
        if input_data.get('name'):
            comment += f" ({input_data['name']})"
        if input_data.get('placeholder'):
            comment += f" - {input_data['placeholder']}"
        
        step = f'{indent}{comment}\n'
        
        # Handle different input types
        if input_type in ['text', 'email', 'password', 'search', 'tel']:
            step += f'{indent}page.fill("{selector}", "{test_value}")'
        elif input_type == 'select':
            step += f'{indent}page.select_option("{selector}", "{test_value}")'
        elif input_type == 'textarea':
            step += f'{indent}page.fill("{selector}", "{test_value}")'
        elif input_type == 'checkbox':
            step += f'{indent}page.check("{selector}")'
        elif input_type == 'radio':
            step += f'{indent}page.check("{selector}")'
        elif input_type == 'file':
            step += f'{indent}page.set_input_files("{selector}", "{test_value}")'
        else:
            step += f'{indent}page.fill("{selector}", "{test_value}")'
        
        return step
    
    def _generate_button_step(self, button_data: Dict[str, Any], indent: str, comment: str = "") -> str:
        """Generate a test step for a button element."""
        selector = button_data.get('selector', '')
        button_text = button_data.get('text', '')
        action_type = button_data.get('action_type', 'click')
        
        # Add comment
        if comment:
            step = f'{indent}# {comment}\n'
        else:
            comment = f"# {action_type.title()} button"
            if button_text:
                comment += f" ({button_text})"
            step = f'{indent}{comment}\n'
        
        # Add waiting for button to be visible
        step += f'{indent}page.wait_for_selector("{selector}", state="visible")\n'
        
        # Click button
        step += f'{indent}page.click("{selector}")'
        
        # Add wait after click for navigation
        if action_type in ['submit', 'login', 'register']:
            step += f'\n{indent}page.wait_for_load_state("networkidle")'
        
        return step
    
    def _generate_link_step(self, link_data: Dict[str, Any], indent: str) -> str:
        """Generate a test step for a link element."""
        selector = link_data.get('selector', '')
        link_text = link_data.get('text', '')
        href = link_data.get('href', '')
        
        # Add comment
        comment = "# Click link"
        if link_text:
            comment += f" ({link_text})"
        if href:
            comment += f" - {href}"
        
        step = f'{indent}{comment}\n'
        step += f'{indent}page.wait_for_selector("{selector}", state="visible")\n'
        step += f'{indent}page.click("{selector}")'
        
        # Add wait for navigation if it's a real link
        if href and not href.startswith('#'):
            step += f'\n{indent}page.wait_for_load_state("networkidle")'
        
        return step
    
    def _choose_template(self, testable_elements: List[Dict[str, Any]]) -> str:
        """Choose the appropriate test template."""
        has_forms = any(elem['type'] == 'form' for elem in testable_elements)
        
        if has_forms:
            return self.test_templates['form_test']
        else:
            return self.test_templates['basic_test']
    
    def generate_test_suite(self, urls: List[str], browser: Browser) -> List[str]:
        """Generate a test suite for multiple URLs."""
        generated_tests = []
        
        for url in urls:
            try:
                test_file = asyncio.run(self.generate_test_from_url(browser, url))
                generated_tests.append(test_file)
            except Exception as e:
                print(f"❌ Failed to generate test for {url}: {e}")
        
        # Generate suite file
        if generated_tests:
            suite_content = self._generate_suite_content(generated_tests)
            suite_file = os.path.join(self.output_dir, "test_suite.py")
            
            with open(suite_file, 'w') as f:
                f.write(suite_content)
            
            print(f"✅ Generated test suite: {suite_file}")
            generated_tests.append(suite_file)
        
        return generated_tests
    
    def _generate_suite_content(self, test_files: List[str]) -> str:
        """Generate a test suite that runs all generated tests."""
        test_names = []
        
        for test_file in test_files:
            filename = os.path.basename(test_file).replace('.py', '')
            test_names.append(filename)
        
        suite_content = '''#!/usr/bin/env python3
"""
Auto-generated test suite
Generated on: {timestamp}
"""

import subprocess
import sys
from pathlib import Path

def run_test(test_name):
    """Run a single test and return the result."""
    try:
        result = subprocess.run([sys.executable, f"{test_name}.py"], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ {test_name}: PASSED")
            return True
        else:
            print(f"❌ {test_name}: FAILED")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {test_name}: ERROR - {e}")
        return False

def main():
    """Run all generated tests."""
    print("🚀 Running test suite...")
    print("=" * 50)
    
    test_names = {test_names}
    
    passed = 0
    failed = 0
    
    for test_name in test_names:
        if run_test(test_name):
            passed += 1
        else:
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 All tests passed!")

if __name__ == "__main__":
    main()
'''.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            test_names=', '.join(f'"{name}"' for name in test_names)
        )
        
        return suite_content
    
    def get_generation_report(self) -> Dict[str, Any]:
        """Get a report of all generated tests."""
        report = {
            'total_tests': 0,
            'tests': [],
            'generation_summary': {
                'by_type': {},
                'by_domain': {},
                'latest_generation': None
            }
        }
        
        if not os.path.exists(self.output_dir):
            return report
        
        # Find all test files
        test_files = []
        for file in os.listdir(self.output_dir):
            if file.endswith('.py') and not file.startswith('test_suite'):
                test_files.append(file)
        
        report['total_tests'] = len(test_files)
        
        # Parse metadata files
        for file in os.listdir(self.output_dir):
            if file.endswith('_metadata.json'):
                try:
                    with open(os.path.join(self.output_dir, file), 'r') as f:
                        metadata = json.load(f)
                        report['tests'].append(metadata)
                        
                        # Update summary
                        domain = metadata.get('url', '').split('//')[-1].split('/')[0]
                        report['generation_summary']['by_domain'][domain] = \
                            report['generation_summary']['by_domain'].get(domain, 0) + 1
                        
                        if not report['generation_summary']['latest_generation']:
                            report['generation_summary']['latest_generation'] = metadata['generated_at']
                        elif metadata['generated_at'] > report['generation_summary']['latest_generation']:
                            report['generation_summary']['latest_generation'] = metadata['generated_at']
                
                except (json.JSONDecodeError, IOError):
                    continue
        
        return report
