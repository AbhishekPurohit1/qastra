"""
Report Writer - Generates HTML reports and various output formats for Qastra test results.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from .templates import HTML_TEMPLATE, SIMPLE_TEMPLATE, EMAIL_TEMPLATE, API_TEMPLATE


class ReportWriter:
    """Writes test reports in various formats (HTML, JSON, email, etc.)."""
    
    def __init__(self, report_dir: str = ".qastra_reports"):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
        os.makedirs(os.path.join(report_dir, "screenshots"), exist_ok=True)
        os.makedirs(os.path.join(report_dir, "visual_diffs"), exist_ok=True)
    
    def write_html_report(self, report_data: Dict[str, Any], template: str = HTML_TEMPLATE) -> str:
        """
        Write comprehensive HTML report.
        
        Args:
            report_data: Processed report data from ReportBuilder
            template: HTML template to use
            
        Returns:
            Path to generated HTML report
        """
        # Prepare template variables
        summary = report_data.get('summary', {})
        metadata = report_data.get('metadata', {})
        tests = report_data.get('tests', [])
        categories = report_data.get('categories', {})
        
        # Build template data
        template_vars = {
            'generated_at': self._format_timestamp(metadata.get('generated_at')),
            'total': summary.get('total', 0),
            'passed': summary.get('passed', 0),
            'failed': summary.get('failed', 0),
            'flaky': summary.get('flaky', 0),
            'skip': summary.get('skip', 0),
            'pass_rate': summary.get('pass_rate', 0),
            'total_duration': summary.get('total_duration', 0),
            'test_rows': self._build_test_rows(tests),
            'category_cards': self._build_category_cards(categories),
            'status_chart_data': self._prepare_status_chart_data(summary),
            'category_chart_data': self._prepare_category_chart_data(categories)
        }
        
        # Generate HTML
        html_content = template.format(**template_vars)
        
        # Write to file
        report_path = os.path.join(self.report_dir, "report.html")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Copy assets (CSS, JS, images)
        self._copy_assets()
        
        return report_path
    
    def write_simple_report(self, report_data: Dict[str, Any]) -> str:
        """Write a simple HTML report."""
        summary = report_data.get('summary', {})
        metadata = report_data.get('metadata', {})
        tests = report_data.get('tests', [])
        
        template_vars = {
            'generated_at': self._format_timestamp(metadata.get('generated_at')),
            'total': summary.get('total', 0),
            'passed': summary.get('passed', 0),
            'failed': summary.get('failed', 0),
            'flaky': summary.get('flaky', 0),
            'test_rows': self._build_simple_test_rows(tests)
        }
        
        html_content = SIMPLE_TEMPLATE.format(**template_vars)
        
        report_path = os.path.join(self.report_dir, "simple_report.html")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def write_json_report(self, report_data: Dict[str, Any]) -> str:
        """Write JSON report for API consumption."""
        summary = report_data.get('summary', {})
        metadata = report_data.get('metadata', {})
        tests = report_data.get('tests', [])
        categories = report_data.get('categories', {})
        performance = report_data.get('performance', {})
        failures = report_data.get('failures', {})
        
        # Prepare API response data
        api_data = {
            'generated_at': self._format_timestamp(metadata.get('generated_at')),
            'generator': metadata.get('generator', 'Qastra Report Builder'),
            'version': metadata.get('report_version', '1.0'),
            'summary': {
                'total': summary.get('total', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'flaky': summary.get('flaky', 0),
                'skip': summary.get('skip', 0),
                'pass_rate': summary.get('pass_rate', 0),
                'total_duration': summary.get('total_duration', 0),
                'average_duration': summary.get('average_duration', 0)
            },
            'tests': tests,
            'categories': categories,
            'performance': performance,
            'failures': failures
        }
        
        report_path = os.path.join(self.report_dir, "report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(api_data, f, indent=2, default=str)
        
        return report_path
    
    def write_email_report(self, report_data: Dict[str, Any]) -> str:
        """Generate email-friendly report."""
        summary = report_data.get('summary', {})
        metadata = report_data.get('metadata', {})
        tests = report_data.get('tests', [])
        
        # Build test summary
        test_summary_lines = []
        for test in tests[:10]:  # Limit to first 10 tests
            status = test.get('status', 'UNKNOWN')
            duration = test.get('duration', 0)
            test_summary_lines.append(f"  {test.get('name', 'Unknown')}: {status} ({duration:.2f}s)")
        
        if len(tests) > 10:
            test_summary_lines.append(f"  ... and {len(tests) - 10} more tests")
        
        # Build failed tests list
        failed_tests_lines = []
        for test in tests:
            if test.get('status') == 'FAIL':
                failed_tests_lines.append(f"  • {test.get('name', 'Unknown')}")
                if test.get('error_message'):
                    failed_tests_lines.append(f"    Error: {test['error_message'][:100]}...")
        
        template_vars = {
            'generated_at': self._format_timestamp(metadata.get('generated_at')),
            'total': summary.get('total', 0),
            'passed': summary.get('passed', 0),
            'failed': summary.get('failed', 0),
            'flaky': summary.get('flaky', 0),
            'pass_rate': summary.get('pass_rate', 0),
            'total_duration': summary.get('total_duration', 0),
            'test_summary': '\n'.join(test_summary_lines),
            'failed_tests': '\n'.join(failed_tests_lines) if failed_tests_lines else 'None',
            'report_url': f"file://{os.path.abspath(os.path.join(self.report_dir, 'report.html'))}"
        }
        
        email_content = EMAIL_TEMPLATE.format(**template_vars)
        
        report_path = os.path.join(self.report_dir, "email_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        return report_path
    
    def write_junit_report(self, report_data: Dict[str, Any]) -> str:
        """Write JUnit XML report for CI/CD integration."""
        tests = report_data.get('tests', [])
        summary = report_data.get('summary', {})
        
        # JUnit XML structure
        junit_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Qastra Test Suite" tests="{summary.get('total', 0)}" failures="{summary.get('failed', 0)} skipped="{summary.get('skip', 0)}" time="{summary.get('total_duration', 0)}">
"""
        
        for test in tests:
            name = test.get('name', 'unknown')
            status = test.get('status', 'UNKNOWN')
            duration = test.get('duration', 0)
            classname = test.get('category', 'test')
            
            if status == 'PASS':
                junit_xml += f'  <testcase name="{name}" classname="{classname}" time="{duration}" />\n'
            elif status == 'FAIL':
                error_msg = test.get('error_message', 'Test failed')
                junit_xml += f'''  <testcase name="{name}" classname="{classname}" time="{duration}">
    <failure message="{self._escape_xml(error_msg)}">{self._escape_xml(error_msg)}</failure>
  </testcase>
'''
            elif status == 'SKIP':
                junit_xml += f'  <testcase name="{name}" classname="{classname}" time="{duration}">\n    <skipped />\n  </testcase>\n'
        
        junit_xml += '</testsuite>'
        
        report_path = os.path.join(self.report_dir, "junit.xml")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(junit_xml)
        
        return report_path
    
    def write_all_formats(self, report_data: Dict[str, Any]) -> Dict[str, str]:
        """Write reports in all available formats."""
        reports = {}
        
        try:
            reports['html'] = self.write_html_report(report_data)
        except Exception as e:
            print(f"⚠️  Failed to write HTML report: {e}")
        
        try:
            reports['json'] = self.write_json_report(report_data)
        except Exception as e:
            print(f"⚠️  Failed to write JSON report: {e}")
        
        try:
            reports['simple'] = self.write_simple_report(report_data)
        except Exception as e:
            print(f"⚠️  Failed to write simple report: {e}")
        
        try:
            reports['email'] = self.write_email_report(report_data)
        except Exception as e:
            print(f"⚠️  Failed to write email report: {e}")
        
        try:
            reports['junit'] = self.write_junit_report(report_data)
        except Exception as e:
            print(f"⚠️  Failed to write JUnit report: {e}")
        
        return reports
    
    def _format_timestamp(self, timestamp: Optional[str]) -> str:
        """Format timestamp for display."""
        if not timestamp:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp
    
    def _build_test_rows(self, tests: List[Dict[str, Any]]) -> str:
        """Build HTML table rows for tests."""
        rows = []
        
        for test in tests:
            status = test.get('status', 'UNKNOWN').lower()
            status_class = f"status-{status}"
            
            # Build tags
            tags_html = ""
            if test.get('tags'):
                tags_html = " ".join([f'<span class="tag">{tag}</span>' for tag in test['tags']])
            
            # Build action buttons
            actions_html = ""
            if test.get('screenshot'):
                actions_html += f'<button onclick="showScreenshot(\'{test["screenshot"]}\')" class="action-btn">📷</button>'
            
            if test.get('visual_diff'):
                actions_html += f'<button onclick="showDiff(\'{test["visual_diff"]}\')" class="action-btn">🔍</button>'
            
            # Duration formatting
            duration = test.get('duration', 0)
            duration_str = f"{duration:.2f}s" if duration > 0 else "N/A"
            
            row = f"""
            <tr class="test-row {status}">
                <td class="test-name">
                    <div class="test-name-content">
                        <span class="test-name-text">{test.get('name', 'Unknown')}</span>
                        {tags_html}
                    </div>
                </td>
                <td class="test-status">
                    <span class="status-badge {status_class}">{test.get('status', 'UNKNOWN')}</span>
                </td>
                <td class="test-duration">{duration_str}</td>
                <td class="test-browser">{test.get('browser', 'N/A')}</td>
                <td class="test-category">{test.get('category', 'Other')}</td>
                <td class="test-actions">{actions_html}</td>
            </tr>
            """
            
            # Add error details if failed
            if test.get('status') == 'FAIL' and test.get('error_message'):
                row += f"""
                <tr class="error-details" style="display: none;">
                    <td colspan="6">
                        <div class="error-content">
                            <h4>Error Details:</h4>
                            <pre class="error-message">{self._escape_html(test['error_message'])}</pre>
                        </div>
                    </td>
                </tr>
                """
            
            rows.append(row)
        
        return "".join(rows)
    
    def _build_simple_test_rows(self, tests: List[Dict[str, Any]]) -> str:
        """Build simple HTML table rows."""
        rows = []
        
        for test in tests:
            status = test.get('status', 'UNKNOWN').lower()
            status_class = f"status-{status}"
            
            duration = test.get('duration', 0)
            duration_str = f"{duration:.2f}s" if duration > 0 else "N/A"
            
            row = f"""
            <tr class="{status_class}">
                <td>{test.get('name', 'Unknown')}</td>
                <td>{test.get('status', 'UNKNOWN')}</td>
                <td>{duration_str}</td>
                <td>{test.get('browser', 'N/A')}</td>
            </tr>
            """
            
            rows.append(row)
        
        return "".join(rows)
    
    def _build_category_cards(self, categories: Dict[str, Any]) -> str:
        """Build HTML cards for test categories."""
        cards = []
        
        for category_id, category_data in categories.items():
            display_name = category_data.get('display_name', category_id)
            total = category_data.get('total', 0)
            passed = category_data.get('passed', 0)
            failed = category_data.get('failed', 0)
            pass_rate = category_data.get('pass_rate', 0)
            
            # Color based on pass rate
            if pass_rate >= 90:
                color = '#10b981'
            elif pass_rate >= 70:
                color = '#f59e0b'
            else:
                color = '#ef4444'
            
            card = f"""
            <div class="category-card" style="border-left: 4px solid {color};">
                <h3>{display_name}</h3>
                <div class="category-stats">
                    <div class="stat">
                        <span class="stat-label">Total:</span>
                        <span class="stat-value">{total}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Passed:</span>
                        <span class="stat-value pass">{passed}</span>
                    </div>
                    <div class="stat">
                        <span class="stat-label">Failed:</span>
                        <span class="stat-value fail">{failed}</span>
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
    
    def _prepare_status_chart_data(self, summary: Dict[str, Any]) -> str:
        """Prepare data for status chart."""
        data = {
            'Passed': summary.get('passed', 0),
            'Failed': summary.get('failed', 0),
            'Flaky': summary.get('flaky', 0),
            'Skipped': summary.get('skip', 0)
        }
        
        # Remove empty categories
        return {k: v for k, v in data.items() if v > 0}
    
    def _prepare_category_chart_data(self, categories: Dict[str, Any]) -> str:
        """Prepare data for category chart."""
        data = {}
        
        for category_id, category_data in categories.items():
            display_name = category_data.get('display_name', category_id)
            pass_rate = category_data.get('pass_rate', 0)
            data[display_name] = pass_rate
        
        return data
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#x27;'))
    
    def _escape_xml(self, text: str) -> str:
        """Escape XML special characters."""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    def _copy_assets(self):
        """Copy static assets (CSS, JS, images) to report directory."""
        assets_dir = os.path.join(self.report_dir, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        
        # For now, we're using CDN resources, so no need to copy assets
        # In the future, we could copy local CSS/JS files here
        pass
    
    def open_report(self, report_path: Optional[str] = None) -> bool:
        """Open the HTML report in the default browser."""
        if report_path is None:
            report_path = os.path.join(self.report_dir, "report.html")
        
        if not os.path.exists(report_path):
            print(f"❌ Report not found: {report_path}")
            return False
        
        try:
            import webbrowser
            file_url = f"file://{os.path.abspath(report_path)}"
            webbrowser.open(file_url)
            print(f"🌐 Opened report: {file_url}")
            return True
        except Exception as e:
            print(f"❌ Failed to open report: {e}")
            return False
    
    def get_report_summary(self) -> Dict[str, Any]:
        """Get summary of generated reports."""
        reports = {}
        
        # Check for different report formats
        report_files = {
            'html': 'report.html',
            'simple': 'simple_report.html',
            'json': 'report.json',
            'email': 'email_report.txt',
            'junit': 'junit.xml'
        }
        
        for format_name, filename in report_files.items():
            file_path = os.path.join(self.report_dir, filename)
            if os.path.exists(file_path):
                reports[format_name] = {
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
        
        return reports


# Convenience functions
def write_html_report(report_data: Dict[str, Any], report_dir: str = ".qastra_reports") -> str:
    """Quick function to write HTML report."""
    writer = ReportWriter(report_dir)
    return writer.write_html_report(report_data)


def write_all_reports(report_data: Dict[str, Any], report_dir: str = ".qastra_reports") -> Dict[str, str]:
    """Quick function to write all report formats."""
    writer = ReportWriter(report_dir)
    return writer.write_all_formats(report_data)


def open_report(report_dir: str = ".qastra_reports") -> bool:
    """Quick function to open HTML report."""
    writer = ReportWriter(report_dir)
    return writer.open_report()
