"""
Qastra Reporter - Generate professional HTML test reports.

Creates beautiful, shareable HTML reports with test results, timing,
and visual indicators for pass/fail status.
"""

import os
import subprocess
from datetime import datetime
from typing import List, Dict, Any


class QastraReporter:
    """Professional HTML report generator for Qastra."""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def add_result(self, name: str, status: str, duration: float, 
                   error: str = None, output: str = None):
        """Add a test result to the report.
        
        Args:
            name: Test name/file name
            status: 'passed', 'failed', 'timeout', 'error'
            duration: Test execution time in seconds
            error: Error message if failed
            output: Test output
        """
        self.results.append({
            "name": name,
            "status": status,
            "duration": duration,
            "error": error,
            "output": output,
            "timestamp": datetime.now()
        })
        
    def set_execution_times(self, start_time: float, end_time: float):
        """Set overall execution start and end times."""
        self.start_time = datetime.fromtimestamp(start_time)
        self.end_time = datetime.fromtimestamp(end_time)
        
    def generate_html_report(self, output_file: str = "reports/report.html"):
        """Generate a professional HTML report.
        
        Args:
            output_file: Path to output HTML file
        """
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r["status"] == "passed"])
        failed_tests = len([r for r in self.results if r["status"] in ["failed", "timeout", "error"]])
        total_duration = sum(r["duration"] for r in self.results)
        
        # Generate test rows
        rows = ""
        for i, result in enumerate(self.results, 1):
            status_icon = "✅" if result["status"] == "passed" else "❌"
            status_color = "#28a745" if result["status"] == "passed" else "#dc3545"
            status_text = result["status"].title()
            
            # Format duration
            duration_text = f"{result['duration']:.2f}s"
            
            # Create expandable error details
            error_details = ""
            if result["error"]:
                error_details = f'''
                <details>
                    <summary style="cursor: pointer; color: #dc3545;">Error Details</summary>
                    <pre style="background: #f8d7da; padding: 10px; border-radius: 4px; overflow-x: auto;">{result["error"]}</pre>
                </details>
                '''
            
            rows += f'''
            <tr>
                <td>{i}</td>
                <td>{result["name"]}</td>
                <td style="color: {status_color}; font-weight: bold;">
                    {status_icon} {status_text}
                </td>
                <td>{duration_text}</td>
                <td>{result["timestamp"].strftime("%H:%M:%S")}</td>
            </tr>
            '''
            if error_details:
                rows += f'''
                <tr>
                    <td colspan="5" style="padding: 0;">
                        {error_details}
                    </td>
                </tr>
                '''
        
        # Calculate execution time
        execution_time = ""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            execution_time = f"{duration.total_seconds():.2f}s"
        
        # Generate HTML
        html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Qastra Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .summary-card h3 {{
            font-size: 2em;
            margin-bottom: 5px;
            color: #2c3e50;
        }}
        
        .summary-card p {{
            color: #7f8c8d;
            font-weight: 500;
        }}
        
        .passed {{ color: #28a745 !important; }}
        .failed {{ color: #dc3545 !important; }}
        .duration {{ color: #17a2b8 !important; }}
        
        .table-container {{
            padding: 0 30px 30px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #34495e;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #ecf0f1;
            font-size: 0.95em;
        }}
        
        tr:last-child td {{
            border-bottom: none;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.9em;
        }}
        
        .footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        details {{
            margin-top: 10px;
        }}
        
        summary {{
            padding: 8px 12px;
            background: #f8d7da;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
        }}
        
        pre {{
            margin: 10px 0;
            padding: 15px;
            background: #2c3e50;
            color: #ecf0f1;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.9em;
            line-height: 1.4;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 8px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .summary {{
                padding: 20px;
                grid-template-columns: 1fr;
            }}
            
            .table-container {{
                padding: 0 20px 20px;
            }}
            
            table {{
                font-size: 0.85em;
            }}
            
            th, td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Qastra Report</h1>
            <div class="subtitle">AI-Powered Browser Automation Test Results</div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3 class="passed">{passed_tests}</h3>
                <p>Tests Passed</p>
            </div>
            <div class="summary-card">
                <h3 class="failed">{failed_tests}</h3>
                <p>Tests Failed</p>
            </div>
            <div class="summary-card">
                <h3>{total_tests}</h3>
                <p>Total Tests</p>
            </div>
            <div class="summary-card">
                <h3 class="duration">{total_duration:.1f}s</h3>
                <p>Total Duration</p>
            </div>
        </div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Qastra on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><a href="https://github.com/AbhishekPurohit1/qastra">Qastra - AI-Powered Browser Automation</a></p>
        </div>
    </div>
</body>
</html>
        '''
        
        # Create reports directory
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write HTML file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
            
        return output_file
    
    def open_report(self, report_file: str = "reports/report.html"):
        """Open the HTML report in the default browser.
        
        Args:
            report_file: Path to the HTML report file
        """
        try:
            subprocess.run(["open", report_file], check=True)
            print(f"🌐 Report opened in browser: {report_file}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Could not open report automatically. Please open manually: {report_file}")
        except FileNotFoundError:
            print(f"⚠️ 'open' command not available. Please open manually: {report_file}")


# Global reporter instance
reporter = QastraReporter()


def generate_report(results: List[Dict[str, Any]], 
                   start_time: float = None, 
                   end_time: float = None,
                   output_file: str = "reports/report.html",
                   auto_open: bool = True):
    """Generate HTML test report from results.
    
    Args:
        results: List of test result dictionaries
        start_time: Test execution start time
        end_time: Test execution end time
        output_file: Output HTML file path
        auto_open: Whether to open report automatically
    """
    global reporter
    
    # Create new reporter instance
    reporter = QastraReporter()
    
    # Add all results
    for result in results:
        reporter.add_result(
            name=result.get("name", "Unknown"),
            status=result.get("status", "unknown"),
            duration=result.get("duration", 0),
            error=result.get("error"),
            output=result.get("output")
        )
    
    # Set execution times
    if start_time and end_time:
        reporter.set_execution_times(start_time, end_time)
    
    # Generate report
    report_path = reporter.generate_html_report(output_file)
    
    print(f"📊 HTML report generated: {report_path}")
    
    # Open automatically if requested
    if auto_open:
        reporter.open_report(report_path)
    
    return report_path
