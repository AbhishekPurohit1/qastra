"""
Report Builder - Collects and processes test results for HTML dashboard generation.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict


class ReportBuilder:
    """Builds comprehensive test reports with statistics and visualizations."""
    
    def __init__(self, report_dir: str = ".qastra_reports"):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
        os.makedirs(os.path.join(report_dir, "screenshots"), exist_ok=True)
        os.makedirs(os.path.join(report_dir, "visual_diffs"), exist_ok=True)
        
        # Test status classifications
        self.status_order = ['PASS', 'FAIL', 'FLAKY', 'SKIP', 'ERROR']
        self.status_colors = {
            'PASS': '#10b981',
            'FAIL': '#ef4444', 
            'FLAKY': '#f59e0b',
            'SKIP': '#6b7280',
            'ERROR': '#dc2626'
        }
        
        # Test categories
        self.categories = {
            'authentication': 'Authentication',
            'navigation': 'Navigation', 
            'forms': 'Forms',
            'search': 'Search',
            'ecommerce': 'E-commerce',
            'visual': 'Visual',
            'api': 'API',
            'performance': 'Performance',
            'other': 'Other'
        }
    
    def collect_results(self, test_results: List[Dict[str, Any]], 
                       session_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Collect and process test results into a comprehensive report.
        
        Args:
            test_results: List of test result dictionaries
            session_info: Optional session metadata
            
        Returns:
            Comprehensive report data
        """
        # Initialize report structure
        report = {
            'metadata': self._build_metadata(session_info),
            'summary': self._build_summary(test_results),
            'tests': self._process_test_results(test_results),
            'categories': self._categorize_tests(test_results),
            'timeline': self._build_timeline(test_results),
            'performance': self._analyze_performance(test_results),
            'failures': self._analyze_failures(test_results),
            'visual_results': self._collect_visual_results(test_results)
        }
        
        return report
    
    def _build_metadata(self, session_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build report metadata."""
        metadata = {
            'generated_at': datetime.now().isoformat(),
            'generator': 'Qastra Report Builder v1.0',
            'report_version': '1.0'
        }
        
        if session_info:
            metadata.update(session_info)
        
        return metadata
    
    def _build_summary(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build test summary statistics."""
        total_tests = len(test_results)
        
        summary = {
            'total': total_tests,
            'passed': 0,
            'failed': 0,
            'flaky': 0,
            'skip': 0,
            'error': 0,
            'pass_rate': 0.0,
            'fail_rate': 0.0,
            'flaky_rate': 0.0,
            'total_duration': 0.0,
            'average_duration': 0.0,
            'slowest_test': None,
            'fastest_test': None,
            'browsers': defaultdict(int),
            'categories': defaultdict(int)
        }
        
        durations = []
        
        for result in test_results:
            status = result.get('status', 'UNKNOWN').upper()
            
            # Count by status
            if status in summary:
                summary[status.lower()] += 1
            
            # Track duration
            duration = result.get('duration', 0)
            if duration > 0:
                durations.append(duration)
                summary['total_duration'] += duration
            
            # Track browsers
            browser = result.get('browser', 'unknown')
            summary['browsers'][browser] += 1
            
            # Track categories
            category = result.get('category', 'other')
            summary['categories'][category] += 1
        
        # Calculate rates
        if total_tests > 0:
            summary['pass_rate'] = (summary['passed'] / total_tests) * 100
            summary['fail_rate'] = (summary['failed'] / total_tests) * 100
            summary['flaky_rate'] = (summary['flaky'] / total_tests) * 100
            summary['average_duration'] = summary['total_duration'] / total_tests
        
        # Find slowest and fastest tests
        if durations:
            summary['slowest_test'] = max(test_results, key=lambda x: x.get('duration', 0))
            summary['fastest_test'] = min(test_results, key=lambda x: x.get('duration', 0))
        
        return summary
    
    def _process_test_results(self, test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process individual test results for display."""
        processed = []
        
        for result in test_results:
            processed_result = {
                'name': result.get('name', 'Unknown Test'),
                'status': result.get('status', 'UNKNOWN').upper(),
                'duration': result.get('duration', 0),
                'browser': result.get('browser', 'unknown'),
                'category': result.get('category', 'other'),
                'error_message': result.get('error_message', ''),
                'screenshot': result.get('screenshot', ''),
                'visual_diff': result.get('visual_diff', ''),
                'retries': result.get('retries', 0),
                'timestamp': result.get('timestamp', datetime.now().isoformat()),
                'tags': result.get('tags', []),
                'assertions': result.get('assertions', [])
            }
            
            # Add status-specific information
            if processed_result['status'] == 'FAIL':
                processed_result['failure_details'] = self._extract_failure_details(result)
            elif processed_result['status'] == 'FLAKY':
                processed_result['flakiness_details'] = self._extract_flakiness_details(result)
            
            processed.append(processed_result)
        
        # Sort by status and then by duration
        processed.sort(key=lambda x: (
            self.status_order.index(x['status']) if x['status'] in self.status_order else 999,
            -x['duration']
        ))
        
        return processed
    
    def _categorize_tests(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Categorize tests and calculate category statistics."""
        categories = {}
        
        for category_name, display_name in self.categories.items():
            category_tests = [t for t in test_results if t.get('category') == category_name]
            
            if category_tests:
                passed = len([t for t in category_tests if t.get('status') == 'PASS'])
                total = len(category_tests)
                
                categories[category_name] = {
                    'display_name': display_name,
                    'total': total,
                    'passed': passed,
                    'failed': total - passed,
                    'pass_rate': (passed / total) * 100 if total > 0 else 0,
                    'tests': category_tests
                }
        
        return categories
    
    def _build_timeline(self, test_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build execution timeline."""
        timeline = []
        
        for result in test_results:
            timeline.append({
                'name': result.get('name', 'Unknown'),
                'status': result.get('status', 'UNKNOWN').upper(),
                'timestamp': result.get('timestamp', datetime.now().isoformat()),
                'duration': result.get('duration', 0)
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        
        return timeline
    
    def _analyze_performance(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test performance metrics."""
        durations = [r.get('duration', 0) for r in test_results if r.get('duration', 0) > 0]
        
        if not durations:
            return {
                'total_duration': 0,
                'average_duration': 0,
                'median_duration': 0,
                'slow_tests': [],
                'fast_tests': [],
                'duration_distribution': {}
            }
        
        # Calculate statistics
        total_duration = sum(durations)
        average_duration = total_duration / len(durations)
        
        # Calculate median
        sorted_durations = sorted(durations)
        median_duration = sorted_durations[len(sorted_durations) // 2]
        
        # Find slow and fast tests
        slow_threshold = average_duration * 2
        fast_threshold = average_duration * 0.5
        
        slow_tests = [r for r in test_results if r.get('duration', 0) > slow_threshold]
        fast_tests = [r for r in test_results if 0 < r.get('duration', 0) < fast_threshold]
        
        # Duration distribution
        distribution = {
            'under_1s': len([d for d in durations if d < 1]),
            '1_to_5s': len([d for d in durations if 1 <= d < 5]),
            '5_to_10s': len([d for d in durations if 5 <= d < 10]),
            'over_10s': len([d for d in durations if d >= 10])
        }
        
        return {
            'total_duration': total_duration,
            'average_duration': average_duration,
            'median_duration': median_duration,
            'slow_tests': slow_tests[:5],  # Top 5 slowest
            'fast_tests': fast_tests[:5],   # Top 5 fastest
            'duration_distribution': distribution
        }
    
    def _analyze_failures(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze test failures and patterns."""
        failed_tests = [r for r in test_results if r.get('status') == 'FAIL']
        
        if not failed_tests:
            return {
                'total_failures': 0,
                'failure_rate': 0,
                'common_errors': {},
                'failure_by_category': {},
                'failure_by_browser': {}
            }
        
        # Extract error patterns
        error_patterns = defaultdict(int)
        failure_by_category = defaultdict(int)
        failure_by_browser = defaultdict(int)
        
        for test in failed_tests:
            # Count by category
            category = test.get('category', 'other')
            failure_by_category[category] += 1
            
            # Count by browser
            browser = test.get('browser', 'unknown')
            failure_by_browser[browser] += 1
            
            # Extract error patterns
            error_msg = test.get('error_message', '')
            if error_msg:
                # Simple pattern extraction - look for common error keywords
                common_errors = ['timeout', 'not found', 'permission', 'network', 'assertion']
                for error in common_errors:
                    if error.lower() in error_msg.lower():
                        error_patterns[error] += 1
        
        return {
            'total_failures': len(failed_tests),
            'failure_rate': (len(failed_tests) / len(test_results)) * 100,
            'common_errors': dict(error_patterns),
            'failure_by_category': dict(failure_by_category),
            'failure_by_browser': dict(failure_by_browser),
            'failed_tests': failed_tests
        }
    
    def _collect_visual_results(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Collect visual test results and diffs."""
        visual_tests = [r for r in test_results if r.get('category') == 'visual']
        
        if not visual_tests:
            return {
                'total_visual_tests': 0,
                'passed_visual': 0,
                'failed_visual': 0,
                'visual_diffs': [],
                'screenshots': []
            }
        
        passed_visual = len([t for t in visual_tests if t.get('status') == 'PASS'])
        failed_visual = len(visual_tests) - passed_visual
        
        # Collect visual diffs and screenshots
        visual_diffs = []
        screenshots = []
        
        for test in visual_tests:
            if test.get('visual_diff'):
                visual_diffs.append({
                    'test_name': test.get('name'),
                    'diff_path': test.get('visual_diff'),
                    'difference_score': test.get('difference_score', 0)
                })
            
            if test.get('screenshot'):
                screenshots.append({
                    'test_name': test.get('name'),
                    'screenshot_path': test.get('screenshot'),
                    'status': test.get('status')
                })
        
        return {
            'total_visual_tests': len(visual_tests),
            'passed_visual': passed_visual,
            'failed_visual': failed_visual,
            'visual_diffs': visual_diffs,
            'screenshots': screenshots
        }
    
    def _extract_failure_details(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed failure information."""
        return {
            'error_type': self._classify_error(result.get('error_message', '')),
            'stack_trace': result.get('stack_trace', ''),
            'failed_assertions': result.get('failed_assertions', []),
            'reproduction_steps': result.get('reproduction_steps', [])
        }
    
    def _extract_flakiness_details(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract flakiness details."""
        return {
            'retries': result.get('retries', 0),
            'inconsistent_results': result.get('inconsistent_results', []),
            'environment_factors': result.get('environment_factors', [])
        }
    
    def _classify_error(self, error_message: str) -> str:
        """Classify error type from message."""
        error_lower = error_message.lower()
        
        if 'timeout' in error_lower:
            return 'timeout'
        elif 'not found' in error_lower or 'selector' in error_lower:
            return 'element_not_found'
        elif 'permission' in error_lower or 'forbidden' in error_lower:
            return 'permission'
        elif 'network' in error_lower or 'connection' in error_lower:
            return 'network'
        elif 'assertion' in error_lower:
            return 'assertion'
        else:
            return 'unknown'
    
    def build_test_rows(self, test_results: List[Dict[str, Any]]) -> str:
        """Build HTML rows for test results table."""
        rows = []
        
        for result in test_results:
            status_class = result['status'].lower()
            status_color = self.status_colors.get(result['status'], '#6b7280')
            
            # Format duration
            duration = result.get('duration', 0)
            duration_str = f"{duration:.2f}s" if duration > 0 else "N/A"
            
            # Build tags HTML
            tags_html = ""
            if result.get('tags'):
                tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in result['tags']])
            
            # Build action buttons
            actions_html = ""
            if result.get('screenshot'):
                actions_html += f'<button onclick="showScreenshot(\'{result["screenshot"]}\')" class="action-btn">📷</button>'
            
            if result.get('visual_diff'):
                actions_html += f'<button onclick="showDiff(\'{result["visual_diff"]}\')" class="action-btn">🔍</button>'
            
            row = f"""
            <tr class="test-row {status_class}">
                <td class="test-name">
                    <div class="test-name-content">
                        <span class="test-name-text">{result['name']}</span>
                        {tags_html}
                    </div>
                </td>
                <td class="test-status">
                    <span class="status-badge" style="background-color: {status_color}">
                        {result['status']}
                    </span>
                </td>
                <td class="test-duration">{duration_str}</td>
                <td class="test-browser">{result.get('browser', 'N/A')}</td>
                <td class="test-category">{self.categories.get(result.get('category', 'other'), result.get('category', 'Other'))}</td>
                <td class="test-actions">{actions_html}</td>
            </tr>
            """
            
            # Add error details row if failed
            if result['status'] == 'FAIL' and result.get('error_message'):
                row += f"""
                <tr class="error-details" style="display: none;">
                    <td colspan="6">
                        <div class="error-content">
                            <h4>Error Details:</h4>
                            <pre class="error-message">{self._escape_html(result['error_message'])}</pre>
                        </div>
                    </td>
                </tr>
                """
            
            rows.append(row)
        
        return "".join(rows)
    
    def build_category_cards(self, categories: Dict[str, Any]) -> str:
        """Build HTML cards for test categories."""
        cards = []
        
        for category_id, category_data in categories.items():
            pass_rate = category_data['pass_rate']
            color = self._get_performance_color(pass_rate)
            
            card = f"""
            <div class="category-card" style="border-left: 4px solid {color};">
                <h3>{category_data['display_name']}</h3>
                <div class="category-stats">
                    <div class="stat">
                        <span class="stat-label">Total:</span>
                        <span class="stat-value">{category_data['total']}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Passed:</span>
                        <span class="stat-value pass">{category_data['passed']}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Failed:</span>
                        <span class="stat-value fail">{category_data['failed']}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Pass Rate:</span>
                        <span class="stat-value" style="color: {color};">{pass_rate:.1f}%</span>
                    </div>
                </div>
            </div>
            """
            cards.append(card)
        
        return "".join(cards)
    
    def _get_performance_color(self, pass_rate: float) -> str:
        """Get color based on pass rate."""
        if pass_rate >= 90:
            return '#10b981'  # Green
        elif pass_rate >= 70:
            return '#f59e0b'  # Yellow
        else:
            return '#ef4444'  # Red
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def save_report_data(self, report_data: Dict[str, Any], filename: str = "report_data.json"):
        """Save raw report data as JSON."""
        report_path = os.path.join(self.report_dir, filename)
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        return report_path


# Convenience functions
def collect_results(test_results: List[Dict[str, Any]], 
                   session_info: Optional[Dict[str, Any]] = None,
                   report_dir: str = ".qastra_reports") -> Dict[str, Any]:
    """Quick function to collect test results."""
    builder = ReportBuilder(report_dir)
    return builder.collect_results(test_results, session_info)
