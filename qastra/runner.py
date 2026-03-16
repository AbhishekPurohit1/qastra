"""
Qastra Test Runner - Execute all tests in the tests directory.

This module provides a test runner that can discover and execute
all Qastra tests in a directory, providing a summary of results.
"""

import os
import sys
import time
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .api.test_api import get_results, clear_results, teardown


@dataclass
class TestResult:
    """Represents a single test result."""
    name: str
    status: str
    duration: float
    error: Optional[str] = None
    actions: List[str] = None
    
    def __post_init__(self):
        if self.actions is None:
            self.actions = []


@dataclass
class TestSuite:
    """Represents a test suite with multiple tests."""
    name: str
    tests: List[TestResult]
    total_duration: float
    
    @property
    def passed_count(self) -> int:
        return len([t for t in self.tests if t.status == 'PASS'])
    
    @property
    def failed_count(self) -> int:
        return len([t for t in self.tests if t.status == 'FAIL'])
    
    @property
    def total_count(self) -> int:
        return len(self.tests)


class TestRunner:
    """Test runner for Qastra tests."""
    
    def __init__(self, test_dir: str = "tests", pattern: str = "*_test.py"):
        self.test_dir = Path(test_dir)
        self.pattern = pattern
        self.test_suites: List[TestSuite] = []
        
    def discover_tests(self) -> List[Path]:
        """Discover test files in the test directory."""
        if not self.test_dir.exists():
            print(f"❌ Test directory '{self.test_dir}' not found")
            return []
        
        test_files = list(self.test_dir.glob(self.pattern))
        print(f"🔍 Found {len(test_files)} test files")
        
        return test_files
    
    def run_test_file(self, test_file: Path) -> TestSuite:
        """Run a single test file."""
        print(f"\n🧪 Running {test_file.name}")
        
        # Clear previous results
        clear_results()
        
        start_time = time.time()
        test_results = []
        
        try:
            # Load the test module
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Look for test functions
            for attr_name in dir(test_module):
                attr = getattr(test_module, attr_name)
                if callable(attr) and attr_name.startswith('test_'):
                    try:
                        print(f"  🔄 {attr_name}")
                        test_start = time.time()
                        
                        # Run the test function
                        attr()
                        
                        test_duration = time.time() - test_start
                        
                        # Get results from the test API
                        api_results = get_results()
                        
                        if api_results:
                            # Use the last result
                            last_result = api_results[-1]
                            test_result = TestResult(
                                name=attr_name,
                                status=last_result.get('status', 'PASS'),
                                duration=test_duration * 1000,
                                actions=last_result.get('actions', [])
                            )
                        else:
                            test_result = TestResult(
                                name=attr_name,
                                status='PASS',
                                duration=test_duration * 1000
                            )
                        
                        test_results.append(test_result)
                        
                        if test_result.status == 'PASS':
                            print(f"    ✅ {attr_name} ({test_result.duration:.0f}ms)")
                        else:
                            print(f"    ❌ {attr_name} ({test_result.duration:.0f}ms)")
                    
                    except Exception as e:
                        test_duration = time.time() - test_start
                        test_result = TestResult(
                            name=attr_name,
                            status='FAIL',
                            duration=test_duration * 1000,
                            error=str(e)
                        )
                        test_results.append(test_result)
                        print(f"    ❌ {attr_name} ({test_result.duration:.0f}ms) - {e}")
            
            # Also look for main execution
            if hasattr(test_module, '__main__') or hasattr(test_module, 'main'):
                try:
                    print(f"  🔄 Running main")
                    main_start = time.time()
                    
                    if hasattr(test_module, 'main'):
                        test_module.main()
                    else:
                        # Execute the module
                        exec(open(test_file).read())
                    
                    main_duration = time.time() - main_start
                    
                    # Get results from the test API
                    api_results = get_results()
                    
                    if api_results:
                        for result in api_results:
                            test_result = TestResult(
                                name=result.get('instruction', 'main'),
                                status=result.get('status', 'PASS'),
                                duration=result.get('execution_time', main_duration * 1000),
                                actions=result.get('actions', []),
                                error=', '.join(result.get('errors', [])) if result.get('errors') else None
                            )
                            test_results.append(test_result)
                    
                    print(f"    ✅ Main ({main_duration * 1000:.0f}ms)")
                
                except Exception as e:
                    main_duration = time.time() - main_start
                    test_result = TestResult(
                        name='main',
                        status='FAIL',
                        duration=main_duration * 1000,
                        error=str(e)
                    )
                    test_results.append(test_result)
                    print(f"    ❌ Main ({main_duration * 1000:.0f}ms) - {e}")
        
        except Exception as e:
            print(f"❌ Failed to run {test_file.name}: {e}")
            test_result = TestResult(
                name=test_file.stem,
                status='FAIL',
                duration=0,
                error=str(e)
            )
            test_results.append(test_result)
        
        finally:
            # Cleanup
            try:
                teardown()
            except:
                pass
        
        total_duration = time.time() - start_time
        
        return TestSuite(
            name=test_file.stem,
            tests=test_results,
            total_duration=total_duration
        )
    
    def run_all_tests(self) -> List[TestSuite]:
        """Run all discovered tests."""
        print("🚀 Starting Qastra Test Runner")
        print("=" * 50)
        
        test_files = self.discover_tests()
        
        if not test_files:
            print("❌ No test files found")
            return []
        
        self.test_suites = []
        total_start_time = time.time()
        
        for test_file in test_files:
            suite = self.run_test_file(test_file)
            self.test_suites.append(suite)
        
        total_duration = time.time() - total_start_time
        
        # Print summary
        self.print_summary(total_duration)
        
        return self.test_suites
    
    def print_summary(self, total_duration: float):
        """Print test summary."""
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        total_tests = sum(suite.total_count for suite in self.test_suites)
        total_passed = sum(suite.passed_count for suite in self.test_suites)
        total_failed = sum(suite.failed_count for suite in self.test_suites)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_failed}")
        print(f"Success Rate: {(total_passed / total_tests * 100):.1f}%" if total_tests > 0 else "N/A")
        print(f"Total Duration: {total_duration:.2f}s")
        
        if total_failed > 0:
            print("\n❌ Failed Tests:")
            for suite in self.test_suites:
                for test in suite.tests:
                    if test.status == 'FAIL':
                        print(f"  • {suite.name}.{test.name}")
                        if test.error:
                            print(f"    Error: {test.error}")
        
        print("\n✅ Test runner completed!")
    
    def generate_report(self, output_file: str = "test_report.json"):
        """Generate JSON test report."""
        import json
        
        report_data = {
            'timestamp': time.time(),
            'total_duration': sum(suite.total_duration for suite in self.test_suites),
            'suites': []
        }
        
        for suite in self.test_suites:
            suite_data = {
                'name': suite.name,
                'total_tests': suite.total_count,
                'passed': suite.passed_count,
                'failed': suite.failed_count,
                'duration': suite.total_duration,
                'tests': []
            }
            
            for test in suite.tests:
                test_data = {
                    'name': test.name,
                    'status': test.status,
                    'duration': test.duration,
                    'actions': test.actions
                }
                if test.error:
                    test_data['error'] = test.error
                
                suite_data['tests'].append(test_data)
            
            report_data['suites'].append(suite_data)
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Test report saved: {output_file}")


def run_tests(test_dir: str = "tests", pattern: str = "*_test.py", report: bool = True):
    """
    Run all tests in the specified directory.
    
    Args:
        test_dir: Directory containing test files
        pattern: Pattern for test files
        report: Whether to generate a report
        
    Example:
        run_tests()
        run_tests("tests", "*_test.py")
        run_tests("integration_tests", "*_test.py", report=False)
    """
    runner = TestRunner(test_dir, pattern)
    suites = runner.run_all_tests()
    
    if report and suites:
        runner.generate_report()
    
    return suites


def main():
    """Main entry point for the test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Qastra Test Runner")
    parser.add_argument("--test-dir", default="tests", help="Test directory")
    parser.add_argument("--pattern", default="*test*.py", help="Test file pattern")
    parser.add_argument("--no-report", action="store_true", help="Don't generate report")
    
    args = parser.parse_args()
    
    run_tests(args.test_dir, args.pattern, not args.no_report)


if __name__ == "__main__":
    main()
