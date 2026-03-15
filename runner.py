#!/usr/bin/env python3
"""
Qastra test runner with self-healing capabilities.
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, Page

from qastra.ai.self_healing import SelfHealingLocator
from qastra.ai.ai_generator import AITestGenerator


class QastraRunner:
    """Main test runner for Qastra framework."""
    
    def __init__(self, cache_dir: str = ".qastra_cache", output_dir: str = "generated_tests"):
        self.cache_dir = cache_dir
        self.output_dir = output_dir
        self.self_healing = SelfHealingLocator(cache_dir)
        self.ai_generator = AITestGenerator(output_dir)
        self.test_results = []
        
        # Ensure directories exist
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
    
    def run_test_file(self, test_file: str, headless: bool = True) -> Dict[str, Any]:
        """Run a single test file with self-healing enabled."""
        test_name = Path(test_file).stem
        start_time = time.time()
        
        result = {
            'test_name': test_name,
            'test_file': test_file,
            'status': 'unknown',
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'error': None,
            'healing_events': 0
        }
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                page = browser.new_page()
                
                # Enable self-healing for this page
                self._setup_self_healing(page)
                
                try:
                    # Execute the test
                    exec(open(test_file).read(), {'page': page, 'browser': browser})
                    
                    result['status'] = 'passed'
                    result['healing_events'] = len(self.self_healing.healing_log)
                    
                except Exception as e:
                    result['status'] = 'failed'
                    result['error'] = str(e)
                
                finally:
                    browser.close()
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
        
        self.test_results.append(result)
        return result
    
    def run_test_directory(self, test_dir: str, headless: bool = True, parallel: bool = False) -> List[Dict[str, Any]]:
        """Run all tests in a directory."""
        test_files = []
        
        # Find all Python test files
        for file in os.listdir(test_dir):
            if file.endswith('.py') and not file.startswith('__'):
                test_files.append(os.path.join(test_dir, file))
        
        if not test_files:
            print(f"No test files found in {test_dir}")
            return []
        
        print(f"Found {len(test_files)} test files")
        
        results = []
        
        if parallel:
            # Run tests in parallel (simplified version)
            print("Running tests in parallel...")
            # Note: True parallel execution would require more complex async handling
            for test_file in test_files:
                result = self.run_test_file(test_file, headless)
                results.append(result)
                print(f"✅ {result['test_name']}: {result['status'].upper()}")
        else:
            # Run tests sequentially
            print("Running tests sequentially...")
            for test_file in test_files:
                result = self.run_test_file(test_file, headless)
                results.append(result)
                status_icon = "✅" if result['status'] == 'passed' else "❌"
                print(f"{status_icon} {result['test_name']}: {result['status'].upper()}")
                if result['error']:
                    print(f"   Error: {result['error']}")
        
        return results
    
    def generate_test_from_url(self, url: str, test_name: Optional[str] = None) -> str:
        """Generate a test from a URL."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            try:
                test_file = self.ai_generator.generate_test_from_url(browser, url, test_name)
                return test_file
            
            finally:
                browser.close()
    
    def generate_healing_report(self) -> Dict[str, Any]:
        """Generate a comprehensive healing report."""
        healing_report = self.self_healing.get_healing_report()
        
        # Add test execution statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'passed'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'failed'])
        
        report = {
            'healing_statistics': healing_report,
            'test_execution': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            'cache_statistics': self.self_healing.locator_store.get_cache_stats(),
            'recent_results': self.test_results[-10:] if self.test_results else []
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "qastra_report.json"):
        """Save a report to file."""
        report_file = os.path.join(self.output_dir, filename)
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📊 Report saved to: {report_file}")
            return report_file
        
        except IOError as e:
            print(f"❌ Failed to save report: {e}")
            return None
    
    def _setup_self_healing(self, page: Page):
        """Setup self-healing hooks for a page."""
        # Override page methods to add self-healing
        original_click = page.click
        
        def healing_click(selector: str, **kwargs):
            try:
                return original_click(selector, **kwargs)
            except Exception as e:
                # Try to heal the locator
                url = page.url
                healed_element = self.self_healing.find_element(page, url, selector)
                
                if healed_element:
                    print(f"🔧 Healed locator: {selector}")
                    return healed_element.click(**kwargs)
                else:
                    raise e
        
        page.click = healing_click
        
        # Similar overrides for other methods could be added here
        # fill, select_option, etc.
    
    def run_with_ai_assistance(self, url: str, headless: bool = True) -> Dict[str, Any]:
        """Run a test with AI assistance for element location."""
        start_time = time.time()
        
        result = {
            'url': url,
            'status': 'unknown',
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'error': None,
            'elements_found': 0,
            'actions_performed': []
        }
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                page = browser.new_page()
                
                # Navigate to page
                page.goto(url)
                page.wait_for_load_state("networkidle")
                
                # Get page content and analyze
                html_content = page.content()
                import sys
                sys.path.append('.')
                from utils.dom_parser import DOMParser
                parser = DOMParser(html_content, url)
                
                testable_elements = parser.get_testable_elements()
                result['elements_found'] = len(testable_elements)
                
                # Perform basic interactions
                for element in testable_elements[:5]:  # Limit to first 5 elements
                    element_type = element['type']
                    element_data = element['data']
                    
                    try:
                        if element_type == 'button':
                            selector = element_data.get('selector', '')
                            if selector:
                                page.click(selector)
                                result['actions_performed'].append(f"Clicked button: {element_data.get('text', 'N/A')}")
                        
                        elif element_type == 'input':
                            selector = element_data.get('selector', '')
                            test_value = element_data.get('test_value', '')
                            if selector and test_value:
                                page.fill(selector, test_value)
                                result['actions_performed'].append(f"Filled input: {element_data.get('name', 'N/A')}")
                        
                        elif element_type == 'link':
                            selector = element_data.get('selector', '')
                            if selector:
                                page.click(selector)
                                result['actions_performed'].append(f"Clicked link: {element_data.get('text', 'N/A')}")
                                page.wait_for_load_state("networkidle")
                    
                    except Exception as e:
                        result['actions_performed'].append(f"Failed to interact with {element_type}: {e}")
                
                result['status'] = 'completed'
                
                browser.close()
        
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
        
        finally:
            result['end_time'] = time.time()
            result['duration'] = result['end_time'] - result['start_time']
        
        return result


def main():
    """Main entry point for the runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Qastra Test Runner")
    parser.add_argument("command", choices=["run", "generate", "heal-report"], 
                       help="Command to execute")
    parser.add_argument("--target", help="Target (test file, directory, or URL)")
    parser.add_argument("--headless", action="store_true", default=True,
                       help="Run tests in headless mode")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tests in parallel")
    parser.add_argument("--output", default="generated_tests",
                       help="Output directory for generated tests")
    
    args = parser.parse_args()
    
    runner = QastraRunner(output_dir=args.output)
    
    if args.command == "run":
        if not args.target:
            print("❌ Please specify a target (test file or directory)")
            sys.exit(1)
        
        if os.path.isfile(args.target):
            # Run single test file
            result = runner.run_test_file(args.target, args.headless)
            print(f"\nTest completed: {result['status']}")
            if result['error']:
                print(f"Error: {result['error']}")
        
        elif os.path.isdir(args.target):
            # Run test directory
            results = runner.run_test_directory(args.target, args.headless, args.parallel)
            
            # Print summary
            passed = len([r for r in results if r['status'] == 'passed'])
            failed = len([r for r in results if r['status'] == 'failed'])
            
            print(f"\n{'='*50}")
            print(f"Results: {passed} passed, {failed} failed")
            
            if failed > 0:
                sys.exit(1)
        
        else:
            print(f"❌ Target not found: {args.target}")
            sys.exit(1)
    
    elif args.command == "generate":
        if not args.target:
            print("❌ Please specify a URL to generate test from")
            sys.exit(1)
        
        print(f"🚀 Generating test from: {args.target}")
        
        try:
            test_file = asyncio.run(runner.generate_test_from_url(args.target))
            print(f"✅ Test generated: {test_file}")
        except Exception as e:
            print(f"❌ Failed to generate test: {e}")
            sys.exit(1)
    
    elif args.command == "heal-report":
        report = runner.generate_healing_report()
        
        print("\n🔧 Self-Healing Report")
        print("=" * 50)
        print(f"Total healings: {report['healing_statistics']['total_healings']}")
        print(f"Average similarity: {report['healing_statistics']['average_similarity']:.2f}")
        
        if report['healing_statistics']['healing_by_url']:
            print("\nHealings by URL:")
            for url, count in report['healing_statistics']['healing_by_url'].items():
                print(f"  {url}: {count}")
        
        print(f"\nCache statistics:")
        cache_stats = report['cache_statistics']
        print(f"  Total locators: {cache_stats['total_locators']}")
        
        if cache_stats['urls']:
            print("  Locators by URL:")
            for url, count in cache_stats['urls'].items():
                print(f"    {url}: {count}")
        
        # Save detailed report
        runner.save_report(report)


if __name__ == "__main__":
    main()
