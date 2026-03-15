"""
Visual Testing Engine for Qastra - Screenshot capture and comparison.
"""

import os
import time
from typing import Optional, Dict, Any
from playwright.sync_api import Page

from .image_diff import ImageDiff, get_visual_report


class VisualEngine:
    """Visual testing engine for screenshot capture and comparison."""
    
    def __init__(self, visual_dir: str = ".qastra_visual", threshold: float = 10.0):
        self.visual_dir = visual_dir
        self.threshold = threshold
        self.diff_engine = ImageDiff(threshold)
        
        # Create directory structure
        self.baseline_dir = os.path.join(visual_dir, "baseline")
        self.current_dir = os.path.join(visual_dir, "current")
        self.diff_dir = os.path.join(visual_dir, "diff")
        
        os.makedirs(self.baseline_dir, exist_ok=True)
        os.makedirs(self.current_dir, exist_ok=True)
        os.makedirs(self.diff_dir, exist_ok=True)
    
    def capture_baseline(self, page: Page, name: str, full_page: bool = True) -> str:
        """
        Capture a baseline screenshot for visual comparison.
        
        Args:
            page: Playwright page object
            name: Name for the screenshot
            full_page: Whether to capture full page
            
        Returns:
            Path to saved baseline image
        """
        path = os.path.join(self.baseline_dir, f"{name}.png")
        
        try:
            page.screenshot(path=path, full_page=full_page)
            print(f"✅ Baseline saved: {path}")
            return path
        
        except Exception as e:
            print(f"❌ Failed to capture baseline: {e}")
            raise
    
    def capture_current(self, page: Page, name: str, full_page: bool = True) -> str:
        """
        Capture a current screenshot for comparison.
        
        Args:
            page: Playwright page object
            name: Name for the screenshot
            full_page: Whether to capture full page
            
        Returns:
            Path to saved current image
        """
        path = os.path.join(self.current_dir, f"{name}.png")
        
        try:
            page.screenshot(path=path, full_page=full_page)
            return path
        
        except Exception as e:
            print(f"❌ Failed to capture current screenshot: {e}")
            raise
    
    def run_visual_test(self, page: Page, name: str, full_page: bool = True) -> Dict[str, Any]:
        """
        Run a visual test comparing current page with baseline.
        
        Args:
            page: Playwright page object
            name: Name for the test
            full_page: Whether to capture full page
            
        Returns:
            Test result dictionary
        """
        baseline_path = os.path.join(self.baseline_dir, f"{name}.png")
        
        # Check if baseline exists
        if not os.path.exists(baseline_path):
            print(f"⚠️  No baseline found for '{name}'. Capturing new baseline...")
            self.capture_baseline(page, name, full_page)
            return {
                'status': 'baseline_created',
                'name': name,
                'message': f'Baseline created for {name}',
                'baseline_path': baseline_path
            }
        
        try:
            # Capture current screenshot
            current_path = self.capture_current(page, name, full_page)
            
            # Generate comprehensive report
            report = self.diff_engine.save_diff_report(
                baseline_path, current_path, self.diff_dir, name
            )
            
            # Determine test result
            if report['passed']:
                print(f"✅ Visual test passed: {name}")
                print(f"   Difference score: {report['difference_score']:.2f}")
                print(f"   Pixel difference: {report['pixel_difference_percentage']:.2f}%")
            else:
                print(f"❌ Visual regression detected: {name}")
                print(f"   Difference score: {report['difference_score']:.2f} (threshold: {self.threshold})")
                print(f"   Pixel difference: {report['pixel_difference_percentage']:.2f}%")
                print(f"   Layout changes: {report['layout_analysis']['layout_change_percentage']:.2f}%")
                print(f"   Color changes: {report['layout_analysis']['color_change_percentage']:.2f}%")
                print(f"   Diff image: {report['files']['highlighted']}")
            
            report['status'] = 'passed' if report['passed'] else 'failed'
            return report
        
        except Exception as e:
            error_result = {
                'status': 'error',
                'name': name,
                'error': str(e),
                'message': f'Visual test error for {name}: {e}'
            }
            print(f"❌ Visual test error: {e}")
            return error_result
    
    def update_baseline(self, page: Page, name: str, full_page: bool = True) -> str:
        """
        Update an existing baseline screenshot.
        
        Args:
            page: Playwright page object
            name: Name for the screenshot
            full_page: Whether to capture full page
            
        Returns:
            Path to updated baseline image
        """
        print(f"🔄 Updating baseline for '{name}'...")
        return self.capture_baseline(page, name, full_page)
    
    def capture_element_screenshot(self, page: Page, selector: str, name: str) -> str:
        """
        Capture screenshot of a specific element.
        
        Args:
            page: Playwright page object
            selector: CSS selector for the element
            name: Name for the screenshot
            
        Returns:
            Path to saved screenshot
        """
        path = os.path.join(self.current_dir, f"{name}_element.png")
        
        try:
            element = page.query_selector(selector)
            if element:
                element.screenshot(path=path)
                print(f"✅ Element screenshot saved: {path}")
                return path
            else:
                raise ValueError(f"Element not found: {selector}")
        
        except Exception as e:
            print(f"❌ Failed to capture element screenshot: {e}")
            raise
    
    def run_element_visual_test(self, page: Page, selector: str, name: str) -> Dict[str, Any]:
        """
        Run visual test on a specific element.
        
        Args:
            page: Playwright page object
            selector: CSS selector for the element
            name: Name for the test
            
        Returns:
            Test result dictionary
        """
        baseline_path = os.path.join(self.baseline_dir, f"{name}_element.png")
        
        # Check if baseline exists
        if not os.path.exists(baseline_path):
            print(f"⚠️  No element baseline found for '{name}'. Capturing new baseline...")
            self.capture_element_screenshot(page, selector, name)
            return {
                'status': 'baseline_created',
                'name': name,
                'selector': selector,
                'message': f'Element baseline created for {name}',
                'baseline_path': baseline_path
            }
        
        try:
            # Capture current element screenshot
            current_path = self.capture_element_screenshot(page, selector, name)
            
            # Generate report
            element_name = f"{name}_element"
            report = self.diff_engine.save_diff_report(
                baseline_path, current_path, self.diff_dir, element_name
            )
            
            # Determine result
            if report['passed']:
                print(f"✅ Element visual test passed: {name}")
            else:
                print(f"❌ Element visual regression detected: {name}")
                print(f"   Selector: {selector}")
                print(f"   Difference score: {report['difference_score']:.2f}")
                print(f"   Diff image: {report['files']['highlighted']}")
            
            report['status'] = 'passed' if report['passed'] else 'failed'
            report['selector'] = selector
            return report
        
        except Exception as e:
            error_result = {
                'status': 'error',
                'name': name,
                'selector': selector,
                'error': str(e),
                'message': f'Element visual test error for {name}: {e}'
            }
            print(f"❌ Element visual test error: {e}")
            return error_result
    
    def get_visual_summary(self) -> Dict[str, Any]:
        """
        Get summary of all visual tests in the directory.
        
        Returns:
            Summary dictionary
        """
        summary = {
            'total_baselines': 0,
            'total_diffs': 0,
            'recent_tests': [],
            'test_names': []
        }
        
        # Count baselines
        if os.path.exists(self.baseline_dir):
            baseline_files = [f for f in os.listdir(self.baseline_dir) if f.endswith('.png')]
            summary['total_baselines'] = len(baseline_files)
            summary['test_names'] = [f.replace('.png', '') for f in baseline_files]
        
        # Count diffs and get recent reports
        if os.path.exists(self.diff_dir):
            diff_files = [f for f in os.listdir(self.diff_dir) if f.endswith('.png')]
            summary['total_diffs'] = len(diff_files)
            
            # Get recent JSON reports
            report_files = [f for f in os.listdir(self.diff_dir) if f.endswith('_report.json')]
            for report_file in report_files[-5:]:  # Last 5 reports
                try:
                    import json
                    report_path = os.path.join(self.diff_dir, report_file)
                    with open(report_path, 'r') as f:
                        report_data = json.load(f)
                        summary['recent_tests'].append({
                            'name': report_data.get('name'),
                            'status': report_data.get('status'),
                            'difference_score': report_data.get('difference_score'),
                            'passed': report_data.get('passed')
                        })
                except:
                    continue
        
        return summary
    
    def cleanup_old_screenshots(self, keep_days: int = 7):
        """
        Clean up old screenshots to save disk space.
        
        Args:
            keep_days: Number of days to keep screenshots
        """
        import datetime
        
        cutoff_time = time.time() - (keep_days * 24 * 3600)
        cleaned_files = 0
        
        for directory in [self.current_dir, self.diff_dir]:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    file_path = os.path.join(directory, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        try:
                            os.remove(file_path)
                            cleaned_files += 1
                        except:
                            continue
        
        if cleaned_files > 0:
            print(f"🧹 Cleaned up {cleaned_files} old screenshot files")


# Convenience functions for quick usage
def capture_baseline(page: Page, name: str, visual_dir: str = ".qastra_visual"):
    """Quick baseline capture function."""
    engine = VisualEngine(visual_dir)
    return engine.capture_baseline(page, name)


def run_visual_test(page: Page, name: str, visual_dir: str = ".qastra_visual", threshold: float = 10.0):
    """Quick visual test function."""
    engine = VisualEngine(visual_dir, threshold)
    return engine.run_visual_test(page, name)


def update_baseline(page: Page, name: str, visual_dir: str = ".qastra_visual"):
    """Quick baseline update function."""
    engine = VisualEngine(visual_dir)
    return engine.update_baseline(page, name)
