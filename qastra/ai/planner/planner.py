"""
AI Test Planner - Intelligent test planning and suggestion engine.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from playwright.sync_api import sync_playwright

from .dom_analyzer import DOMAnalyzer
from .test_suggester import TestSuggester


class TestPlanner:
    """AI-powered test planner that analyzes websites and suggests comprehensive test plans."""
    
    def __init__(self, output_dir: str = "generated_tests"):
        self.output_dir = output_dir
        self.dom_analyzer = DOMAnalyzer()
        self.test_suggester = TestSuggester()
        os.makedirs(output_dir, exist_ok=True)
    
    def plan_tests(self, url: str, save_report: bool = True) -> Dict[str, Any]:
        """
        Analyze a website and generate a comprehensive test plan.
        
        Args:
            url: URL to analyze
            save_report: Whether to save the analysis report
            
        Returns:
            Comprehensive test plan
        """
        print(f"🧠 Qastra AI Test Planner")
        print(f"🌐 Analyzing: {url}")
        print("=" * 50)
        
        analysis_result = None
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                # Navigate to the page
                print("📄 Loading page...")
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(3000)  # Wait for dynamic content
                
                print("🔍 Analyzing page structure...")
                
                # Analyze the page
                analysis_result = self.dom_analyzer.analyze_page(page)
                
                print("📋 Generating test suggestions...")
                
                # Generate test suggestions
                test_plan = self.test_suggester.generate_test_plan(analysis_result)
                
                # Add metadata
                test_plan['metadata'] = {
                    'generated_at': datetime.now().isoformat(),
                    'url': url,
                    'planner_version': '1.0',
                    'analysis_duration': 'N/A'  # Could be measured if needed
                }
                
                # Display results
                self._display_results(test_plan)
                
                # Save report if requested
                if save_report:
                    self._save_report(test_plan, url)
                
                return test_plan
            
            except Exception as e:
                print(f"❌ Error during analysis: {e}")
                return {
                    'error': str(e),
                    'url': url,
                    'generated_at': datetime.now().isoformat()
                }
            
            finally:
                browser.close()
    
    def _display_results(self, test_plan: Dict[str, Any]):
        """Display the test plan results."""
        if 'error' in test_plan:
            print(f"\n❌ Analysis failed: {test_plan['error']}")
            return
        
        # Use the formatter from test_suggester
        formatted_plan = self.test_suggester.format_test_plan(test_plan)
        print(formatted_plan)
        
        # Additional detailed information
        page_info = test_plan['page_info']
        categorized = test_plan['categorized_suggestions']
        
        print("📂 Detailed Test Categories")
        print("-" * 30)
        
        for category, tests in categorized.items():
            if tests:
                print(f"\n{category.title()} ({len(tests)} tests):")
                for i, test in enumerate(tests[:3], 1):  # Show first 3
                    priority_icon = self._get_priority_icon(test.get('priority', 'medium'))
                    print(f"  {priority_icon} {i}. {test['name']}")
                
                if len(tests) > 3:
                    print(f"  ... and {len(tests) - 3} more {category} tests")
        
        print(f"\n🎯 Next Steps:")
        print(f"1. Run critical tests first")
        print(f"2. Use 'qastra generate {page_info['url']}' to create automated tests")
        print(f"3. Use 'qastra record {page_info['url']}' to record user interactions")
        print(f"4. Use 'qastra test \"<natural language command>\" for quick testing")
    
    def _get_priority_icon(self, priority: str) -> str:
        """Get icon for priority level."""
        icons = {
            'critical': '🔥',
            'high': '⚡',
            'medium': '📋',
            'low': '📝'
        }
        return icons.get(priority, '📝')
    
    def _save_report(self, test_plan: Dict[str, Any], url: str):
        """Save the analysis report to file."""
        try:
            # Generate filename
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')
            clean_domain = ''.join(c for c in domain if c.isalnum() or c in ('-', '_'))
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_plan_{clean_domain}_{timestamp}.json"
            
            report_path = os.path.join(self.output_dir, filename)
            
            with open(report_path, 'w') as f:
                json.dump(test_plan, f, indent=2, default=str)
            
            print(f"\n💾 Report saved: {report_path}")
            
            # Also save a human-readable version
            txt_filename = f"test_plan_{clean_domain}_{timestamp}.txt"
            txt_path = os.path.join(self.output_dir, txt_filename)
            
            with open(txt_path, 'w') as f:
                f.write(self.test_suggester.format_test_plan(test_plan))
            
            print(f"📄 Text report saved: {txt_path}")
            
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
    
    def plan_multiple_pages(self, urls: List[str]) -> Dict[str, Any]:
        """
        Plan tests for multiple URLs.
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            Combined analysis results
        """
        print(f"🧠 Qastra AI Test Planner - Multi-Site Analysis")
        print(f"📊 Analyzing {len(urls)} URLs")
        print("=" * 50)
        
        combined_results = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_urls': len(urls),
                'planner_version': '1.0'
            },
            'site_analyses': {},
            'combined_statistics': {},
            'cross_site_recommendations': []
        }
        
        total_tests = 0
        all_categories = set()
        
        for i, url in enumerate(urls, 1):
            print(f"\n--- Site {i}/{len(urls)} ---")
            
            try:
                test_plan = self.plan_tests(url, save_report=False)
                
                if 'error' not in test_plan:
                    combined_results['site_analyses'][url] = test_plan
                    
                    # Accumulate statistics
                    stats = test_plan.get('test_statistics', {})
                    total_tests += stats.get('total_suggestions', 0)
                    
                    categories = test_plan.get('categorized_suggestions', {}).keys()
                    all_categories.update(categories)
                
                else:
                    combined_results['site_analyses'][url] = test_plan
            
            except Exception as e:
                print(f"❌ Failed to analyze {url}: {e}")
                combined_results['site_analyses'][url] = {'error': str(e)}
        
        # Generate combined statistics
        combined_results['combined_statistics'] = {
            'total_tests_across_sites': total_tests,
            'unique_categories': len(all_categories),
            'successful_analyses': len([s for s in combined_results['site_analyses'].values() if 'error' not in s])
        }
        
        # Generate cross-site recommendations
        combined_results['cross_site_recommendations'] = self._generate_cross_site_recommendations(combined_results)
        
        # Display summary
        self._display_multi_site_summary(combined_results)
        
        # Save combined report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = f"multi_site_test_plan_{timestamp}.json"
        combined_path = os.path.join(self.output_dir, combined_filename)
        
        with open(combined_path, 'w') as f:
            json.dump(combined_results, f, indent=2, default=str)
        
        print(f"\n💾 Combined report saved: {combined_path}")
        
        return combined_results
    
    def _generate_cross_site_recommendations(self, combined_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations across multiple sites."""
        recommendations = []
        
        successful_analyses = [s for s in combined_results['site_analyses'].values() if 'error' not in s]
        
        if not successful_analyses:
            return ["No successful analyses to generate recommendations"]
        
        # Common patterns
        all_page_types = [s.get('page_info', {}).get('page_type', 'unknown') for s in successful_analyses]
        common_types = list(set(all_page_types))
        
        if len(common_types) == 1:
            recommendations.append(f"All sites are {common_types[0]} type - focus on domain-specific testing")
        else:
            recommendations.append(f"Multiple site types detected: {', '.join(common_types)}")
        
        # Complexity analysis
        complexities = [s.get('page_info', {}).get('complexity_score', 0) for s in successful_analyses]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        
        if avg_complexity > 100:
            recommendations.append("High complexity sites detected - prioritize comprehensive testing")
        elif avg_complexity < 50:
            recommendations.append("Low complexity sites - focus on core functionality")
        
        # Common critical tests
        critical_tests = set()
        for analysis in successful_analyses:
            for suggestion in analysis.get('all_suggestions', []):
                if suggestion.get('priority') == 'critical':
                    critical_tests.add(suggestion.get('name', ''))
        
        if critical_tests:
            recommendations.append(f"Common critical tests across sites: {', '.join(list(critical_tests)[:3])}")
        
        return recommendations
    
    def _display_multi_site_summary(self, combined_results: Dict[str, Any]):
        """Display summary for multi-site analysis."""
        print(f"\n📊 Multi-Site Analysis Summary")
        print("=" * 40)
        
        stats = combined_results['combined_statistics']
        print(f"Total URLs analyzed: {combined_results['metadata']['total_urls']}")
        print(f"Successful analyses: {stats['successful_analyses']}")
        print(f"Total tests suggested: {stats['total_tests_across_sites']}")
        print(f"Unique test categories: {stats['unique_categories']}")
        
        if combined_results.get('cross_site_recommendations'):
            print(f"\n💡 Cross-Site Recommendations:")
            for rec in combined_results['cross_site_recommendations']:
                print(f"  • {rec}")
        
        print(f"\n📂 Individual Site Reports:")
        for url, analysis in combined_results['site_analyses'].items():
            if 'error' not in analysis:
                page_info = analysis.get('page_info', {})
                stats = analysis.get('test_statistics', {})
                print(f"  📄 {page_info.get('title', 'Unknown')}")
                print(f"     Tests: {stats.get('total_suggestions', 0)} | Type: {page_info.get('page_type', 'unknown')}")
            else:
                print(f"  ❌ {url} - Analysis failed")
    
    def get_quick_analysis(self, url: str) -> Dict[str, Any]:
        """Get a quick analysis without detailed test suggestions."""
        print(f"⚡ Quick Analysis: {url}")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(2000)
                
                analysis = self.dom_analyzer.analyze_page(page)
                
                # Quick summary
                print(f"📄 Page Type: {analysis.get('page_type', 'unknown').title()}")
                print(f"🔍 Features: {', '.join([k for k, v in analysis.get('features', {}).items() if v])}")
                print(f"📊 Complexity: {analysis.get('complexity_score', 0)}")
                print(f"🔗 Forms: {len(analysis.get('forms', []))}")
                print(f"🔘 Buttons: {len(analysis.get('buttons', []))}")
                
                return analysis
            
            except Exception as e:
                print(f"❌ Quick analysis failed: {e}")
                return {'error': str(e)}
            
            finally:
                browser.close()


# Convenience functions
def plan_tests(url: str, output_dir: str = "generated_tests") -> Dict[str, Any]:
    """Quick function to plan tests for a single URL."""
    planner = TestPlanner(output_dir)
    return planner.plan_tests(url)


def plan_multiple_pages(urls: List[str], output_dir: str = "generated_tests") -> Dict[str, Any]:
    """Quick function to plan tests for multiple URLs."""
    planner = TestPlanner(output_dir)
    return planner.plan_multiple_pages(urls)


def get_quick_analysis(url: str) -> Dict[str, Any]:
    """Quick function for basic page analysis."""
    planner = TestPlanner()
    return planner.get_quick_analysis(url)
