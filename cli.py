#!/usr/bin/env python3
"""
Qastra CLI - Command line interface for the AI-powered test automation framework.
"""

import argparse
import os
import sys
import asyncio
from pathlib import Path

from runner import QastraRunner


def create_parser():
    """Create the argument parser for Qastra CLI."""
    parser = argparse.ArgumentParser(
        description="Qastra - AI-powered test automation framework",
        epilog="Example: qastra generate https://example.com"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run tests')
    run_parser.add_argument('target', help='Test file or directory to run')
    run_parser.add_argument('--headless', action='store_true', default=True,
                           help='Run tests in headless mode (default: True)')
    run_parser.add_argument('--no-headless', dest='headless', action='store_false',
                           help='Run tests with visible browser')
    run_parser.add_argument('--parallel', action='store_true',
                           help='Run tests in parallel')
    run_parser.add_argument('--output', default='generated_tests',
                           help='Output directory for reports (default: generated_tests)')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate tests from URL')
    gen_parser.add_argument('url', help='URL to generate test from')
    gen_parser.add_argument('--name', help='Custom test name')
    gen_parser.add_argument('--output', default='generated_tests',
                           help='Output directory for generated tests (default: generated_tests)')
    
    # Heal report command
    heal_parser = subparsers.add_parser('heal-report', help='Show self-healing report')
    heal_parser.add_argument('--output', default='generated_tests',
                            help='Output directory for reports (default: generated_tests)')
    heal_parser.add_argument('--save', action='store_true',
                            help='Save report to file')
    
    # AI assist command
    ai_parser = subparsers.add_parser('ai-assist', help='Run AI-assisted test on URL')
    ai_parser.add_argument('url', help='URL to test with AI assistance')
    ai_parser.add_argument('--headless', action='store_true', default=True,
                          help='Run in headless mode (default: True)')
    ai_parser.add_argument('--no-headless', dest='headless', action='store_false',
                          help='Run with visible browser')
    ai_parser.add_argument('--output', default='generated_tests',
                          help='Output directory for reports (default: generated_tests)')
    
    # Natural language test command
    nlp_parser = subparsers.add_parser('test', help='Run natural language test')
    nlp_parser.add_argument('sentence', help='Natural language test sentence')
    nlp_parser.add_argument('--url', help='URL to test on (optional)')
    nlp_parser.add_argument('--headless', action='store_true', default=True,
                           help='Run in headless mode (default: True)')
    nlp_parser.add_argument('--no-headless', dest='headless', action='store_false',
                           help='Run with visible browser')
    nlp_parser.add_argument('--output', default='generated_tests',
                           help='Output directory for reports (default: generated_tests)')
    
    # Visual test command
    visual_parser = subparsers.add_parser('visual', help='Run visual regression test')
    visual_parser.add_argument('url', help='URL to test visually')
    visual_parser.add_argument('--name', default='visual_test', help='Test name (default: visual_test)')
    visual_parser.add_argument('--baseline', action='store_true', help='Create baseline instead of comparing')
    visual_parser.add_argument('--update', action='store_true', help='Update existing baseline')
    visual_parser.add_argument('--headless', action='store_true', default=True,
                              help='Run in headless mode (default: True)')
    visual_parser.add_argument('--no-headless', dest='headless', action='store_false',
                              help='Run with visible browser')
    visual_parser.add_argument('--threshold', type=float, default=10.0,
                              help='Visual difference threshold (default: 10.0)')
    visual_parser.add_argument('--output', default='.qastra_visual',
                              help='Visual test directory (default: .qastra_visual)')
    
    # Smart test command
    smart_parser = subparsers.add_parser('smart', help='Run smart locator test')
    smart_parser.add_argument('url', help='URL to test with smart locators')
    smart_parser.add_argument('--headless', action='store_true', default=True,
                            help='Run in headless mode (default: True)')
    smart_parser.add_argument('--no-headless', dest='headless', action='store_false',
                            help='Run with visible browser')
    
    # Record command
    record_parser = subparsers.add_parser('record', help='Record browser actions to generate tests')
    record_parser.add_argument('url', help='URL to start recording from')
    record_parser.add_argument('--duration', type=int, default=60,
                              help='Recording duration in seconds (default: 60)')
    record_parser.add_argument('--output', help='Output test file name')
    record_parser.add_argument('--output-dir', default='generated_tests',
                              help='Output directory for tests (default: generated_tests)')
    record_parser.add_argument('--interactive', action='store_true',
                              help='Interactive recording mode')
    record_parser.add_argument('--guided', action='store_true',
                              help='Guided recording mode')
    
    # Plan command
    plan_parser = subparsers.add_parser('plan', help='Generate AI test plan for website')
    plan_parser.add_argument('url', help='URL to analyze and plan tests for')
    plan_parser.add_argument('--multi', action='store_true',
                           help='Multi-site planning mode (read URLs from file)')
    plan_parser.add_argument('--quick', action='store_true',
                           help='Quick analysis only')
    plan_parser.add_argument('--output-dir', default='generated_tests',
                           help='Output directory for reports (default: generated_tests)')
    
    # Auto-fix command
    autofix_parser = subparsers.add_parser('auto-fix', help='Run maintenance bot to fix broken tests')
    autofix_parser.add_argument('--status', action='store_true',
                               help='Show maintenance bot status')
    autofix_parser.add_argument('--dry-run', action='store_true',
                               help='Apply fixes without committing')
    autofix_parser.add_argument('--no-commit', action='store_true',
                               help='Apply fixes but don\'t commit')
    autofix_parser.add_argument('--no-pr', action='store_true',
                               help='Commit changes but don\'t create PR')
    autofix_parser.add_argument('--cleanup', type=int, metavar='DAYS',
                               help='Clean up backups older than DAYS days')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate HTML test report')
    report_parser.add_argument('--format', choices=['html', 'json', 'simple', 'email', 'junit', 'all'],
                               default='html', help='Report format (default: html)')
    report_parser.add_argument('--open', action='store_true',
                              help='Open report in browser after generation')
    report_parser.add_argument('--input', help='Input JSON file with test results')
    report_parser.add_argument('--output-dir', default='.qastra_reports',
                              help='Output directory for reports (default: .qastra_reports)')
    
    # Version command
    subparsers.add_parser('version', help='Show version information')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize Qastra project')
    init_parser.add_argument('directory', nargs='?', default='.',
                           help='Directory to initialize (default: current directory)')
    
    return parser


def cmd_run(args):
    """Handle the run command."""
    runner = QastraRunner(output_dir=args.output)
    
    if not os.path.exists(args.target):
        print(f"❌ Target not found: {args.target}")
        return 1
    
    print(f"🚀 Running tests from: {args.target}")
    
    if os.path.isfile(args.target):
        # Run single test file
        result = runner.run_test_file(args.target, args.headless)
        
        print(f"\n{'='*50}")
        print(f"Test: {result['test_name']}")
        print(f"Status: {result['status'].upper()}")
        print(f"Duration: {result['duration']:.2f}s")
        
        if result['healing_events'] > 0:
            print(f"Healing events: {result['healing_events']}")
        
        if result['error']:
            print(f"Error: {result['error']}")
            return 1
    
    elif os.path.isdir(args.target):
        # Run test directory
        results = runner.run_test_directory(args.target, args.headless, args.parallel)
        
        if not results:
            print("❌ No test files found")
            return 1
        
        # Print summary
        passed = len([r for r in results if r['status'] == 'passed'])
        failed = len([r for r in results if r['status'] == 'failed'])
        total_time = sum(r['duration'] for r in results)
        
        print(f"\n{'='*50}")
        print(f"Total tests: {len(results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Success rate: {(passed/len(results)*100):.1f}%")
        
        # Show failed tests
        if failed > 0:
            print(f"\n❌ Failed tests:")
            for result in results:
                if result['status'] == 'failed':
                    print(f"  - {result['test_name']}: {result['error']}")
        
        return 1 if failed > 0 else 0
    
    return 0


def cmd_generate(args):
    """Handle the generate command."""
    runner = QastraRunner(output_dir=args.output)
    
    print(f"🚀 Generating test from: {args.url}")
    
    try:
        test_file = runner.generate_test_from_url(args.url, args.name)
        print(f"✅ Test generated: {test_file}")
        
        # Show next steps
        print(f"\nNext steps:")
        print(f"  Run the test: python {test_file}")
        print(f"  Or use Qastra: qastra run {test_file}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Failed to generate test: {e}")
        return 1


def cmd_heal_report(args):
    """Handle the heal-report command."""
    runner = QastraRunner(output_dir=args.output)
    report = runner.generate_healing_report()
    
    print(f"\n🔧 Self-Healing Report")
    print(f"{'='*50}")
    
    healing_stats = report['healing_statistics']
    test_stats = report['test_execution']
    cache_stats = report['cache_statistics']
    
    print(f"📊 Healing Statistics:")
    print(f"  Total healings: {healing_stats['total_healings']}")
    print(f"  Average similarity: {healing_stats['average_similarity']:.2f}")
    
    if healing_stats['healing_by_url']:
        print(f"\n  Healings by URL:")
        for url, count in healing_stats['healing_by_url'].items():
            print(f"    {url}: {count}")
    
    print(f"\n📋 Test Execution:")
    print(f"  Total tests: {test_stats['total_tests']}")
    print(f"  Passed: {test_stats['passed_tests']}")
    print(f"  Failed: {test_stats['failed_tests']}")
    print(f"  Success rate: {test_stats['success_rate']:.1f}%")
    
    print(f"\n💾 Cache Statistics:")
    print(f"  Total locators: {cache_stats['total_locators']}")
    
    if cache_stats['urls']:
        print(f"  Locators by URL:")
        for url, count in cache_stats['urls'].items():
            print(f"    {url}: {count}")
    
    if cache_stats['most_used']:
        most_used = cache_stats['most_used']
        print(f"  Most used locator: {most_used['description']} (used {most_used['usage_count']} times)")
    
    if healing_stats['recent_healings']:
        print(f"\n🕐 Recent Healings:")
        for healing in healing_stats['recent_healings'][-5:]:
            print(f"  {healing['description']} - similarity: {healing['similarity_score']:.2f}")
    
    if args.save:
        report_file = runner.save_report(report)
        if report_file:
            print(f"\n📄 Detailed report saved: {report_file}")
    
    return 0


def cmd_ai_assist(args):
    """Handle the ai-assist command."""
    runner = QastraRunner(output_dir=args.output)
    
    print(f"🤖 Running AI-assisted test on: {args.url}")
    
    result = runner.run_with_ai_assistance(args.url, args.headless)
    
    print(f"\n{'='*50}")
    print(f"Status: {result['status'].upper()}")
    print(f"Duration: {result['duration']:.2f}s")
    print(f"Elements found: {result['elements_found']}")
    
    if result['actions_performed']:
        print(f"\nActions performed:")
        for action in result['actions_performed']:
            print(f"  ✅ {action}")
    
    if result['error']:
        print(f"\n❌ Error: {result['error']}")
        return 1
    
    # Save report
    report_file = runner.save_report({'ai_assist_result': result}, 'ai_assist_report.json')
    if report_file:
        print(f"\n📄 Report saved: {report_file}")
    
    return 0


def cmd_nlp_test(args):
    """Handle the natural language test command."""
    import sys
    sys.path.append('.')
    
    from qastra.ai.nlp.executor import NLPExecutor
    
    print(f"🧠 Running Natural Language Test")
    print(f"Sentence: \"{args.sentence}\"")
    
    if args.url:
        print(f"URL: {args.url}")
    
    executor = NLPExecutor(headless=args.headless)
    result = executor.execute_test(args.sentence, args.url)
    
    executor.print_execution_result(result)
    
    # Save execution report
    if args.output:
        import json
        report_file = os.path.join(args.output, "nlp_test_report.json")
        
        try:
            with open(report_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"\n📄 Report saved: {report_file}")
        except IOError as e:
            print(f"❌ Failed to save report: {e}")
    
    return 0 if result['status'] == 'completed' else 1


def cmd_visual_test(args):
    """Handle the visual test command."""
    import sys
    sys.path.append('.')
    
    from qastra.ai.visual.visual_engine import VisualEngine
    from playwright.sync_api import sync_playwright
    
    print(f"👁️  Running Visual Regression Test")
    print(f"URL: {args.url}")
    print(f"Test name: {args.name}")
    print(f"Threshold: {args.threshold}")
    
    engine = VisualEngine(args.output, args.threshold)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        page = browser.new_page()
        
        try:
            # Navigate to URL
            page.goto(args.url, wait_until="networkidle")
            page.wait_for_timeout(2000)  # Wait for dynamic content
            
            if args.baseline:
                # Create baseline
                baseline_path = engine.capture_baseline(page, args.name)
                print(f"\n✅ Baseline created: {baseline_path}")
                
            elif args.update:
                # Update baseline
                baseline_path = engine.update_baseline(page, args.name)
                print(f"\n✅ Baseline updated: {baseline_path}")
                
            else:
                # Run visual test
                result = engine.run_visual_test(page, args.name)
                
                print(f"\n{'='*50}")
                print(f"Visual Test Results:")
                print(f"Status: {result['status'].upper()}")
                
                if result['status'] == 'baseline_created':
                    print(f"✅ New baseline created for {args.name}")
                    
                elif result['status'] == 'passed':
                    print(f"✅ No visual regressions detected")
                    print(f"Difference score: {result.get('difference_score', 'N/A')}")
                    print(f"Pixel difference: {result.get('pixel_difference_percentage', 'N/A')}%")
                    
                elif result['status'] == 'failed':
                    print(f"❌ Visual regression detected!")
                    print(f"Difference score: {result.get('difference_score', 'N/A')}")
                    print(f"Pixel difference: {result.get('pixel_difference_percentage', 'N/A')}%")
                    
                    layout_analysis = result.get('layout_analysis', {})
                    if layout_analysis:
                        print(f"Layout changes: {layout_analysis.get('layout_change_percentage', 'N/A')}%")
                        print(f"Color changes: {layout_analysis.get('color_change_percentage', 'N/A')}%")
                    
                    files = result.get('files', {})
                    if files.get('highlighted'):
                        print(f"Diff image: {files['highlighted']}")
                
                elif result['status'] == 'error':
                    print(f"❌ Visual test error: {result.get('error', 'Unknown error')}")
                
                # Save summary
                summary = engine.get_visual_summary()
                print(f"\n📊 Visual Test Summary:")
                print(f"Total baselines: {summary['total_baselines']}")
                print(f"Total diffs: {summary['total_diffs']}")
                
                return 0 if result['status'] in ['passed', 'baseline_created'] else 1
        
        except Exception as e:
            print(f"❌ Visual test failed: {e}")
            return 1
        
        finally:
            browser.close()


def cmd_smart_test(args):
    """Handle the smart locator test command."""
    import sys
    sys.path.append('.')
    
    from qastra.engine.action_wrapper import click, fill, get_action_wrapper
    from playwright.sync_api import sync_playwright
    
    print(f"🧠 Running Smart Locator Test")
    print(f"URL: {args.url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        page = browser.new_page()
        
        try:
            # Navigate to URL
            page.goto(args.url, wait_until="networkidle")
            page.wait_for_timeout(2000)
            
            print(f"📍 Navigated to {args.url}")
            
            # Test smart locator capabilities based on URL
            if "orangehrmlive.com" in args.url and "login" in args.url:
                print("\n🔍 Testing OrangeHRM login with smart locators...")
                
                # Fill username
                result = fill(page, "username", "Admin")
                
                # Fill password
                result = fill(page, "password", "admin123")
                
                # Click login
                result = click(page, "login")
                
                # Wait for dashboard
                page.wait_for_timeout(3000)
                
                # Test dashboard navigation
                print("\n🔍 Testing dashboard navigation...")
                
                dashboard_items = ["admin", "user", "directory", "performance", "recruitment"]
                
                for item in dashboard_items:
                    result = click(page, item)
                    if result['status'] == 'success':
                        print(f"✅ Successfully clicked {item}")
                        page.wait_for_timeout(1000)
                    else:
                        print(f"❌ Could not find {item}")
            
            elif "example.com" in args.url:
                print("\n🔍 Testing example.com with smart locators...")
                
                # Try to find and click links
                common_intents = ["more information", "link", "details", "about"]
                
                for intent in common_intents:
                    result = click(page, intent)
                    if result['status'] == 'success':
                        print(f"✅ Successfully clicked {intent}")
                        break
                    else:
                        print(f"❌ Could not find {intent}")
            
            else:
                print("\n🔍 Testing general smart locator capabilities...")
                
                # Try common actions
                common_intents = ["login", "search", "menu", "button", "submit"]
                
                for intent in common_intents:
                    result = click(page, intent)
                    if result['status'] == 'success':
                        print(f"✅ Successfully clicked {intent}")
                        break
                    else:
                        print(f"❌ Could not find {intent}")
            
            # Print action summary
            wrapper = get_action_wrapper()
            wrapper.print_action_summary()
            
            # Show smart locator stats
            from qastra.engine.smart_locator import SmartLocator
            locator = SmartLocator()
            
            print(f"\n📊 Smart Locator Statistics:")
            print(f"Supported intents: {len(locator.get_supported_intents())}")
            print(f"Confidence threshold: {locator.confidence_threshold}")
            
            # Benchmark the page
            benchmark = locator.benchmark_page(page)
            print(f"Page elements: {benchmark['total_elements']}")
            print(f"Elements with text: {benchmark['elements_with_text']}")
            print(f"Elements with ID: {benchmark['elements_with_id']}")
            print(f"Semantic elements: {benchmark['semantic_elements']}")
            
            print(f"\n✅ Smart Locator Test Completed!")
            
        except Exception as e:
            print(f"❌ Smart locator test failed: {e}")
            return 1
        
        finally:
            browser.close()
    
    return 0


def cmd_record(args):
    """Handle the record command."""
    import sys
    sys.path.append('.')
    
    from qastra.recorder.recorder import start_recorder, record_interactive, record_with_guidance
    
    print(f"🎬 Qastra Test Recorder")
    print(f"URL: {args.url}")
    
    try:
        if args.guided:
            # Guided recording mode
            steps = [
                "Navigate to the page",
                "Interact with elements you want to test",
                "Complete your test flow",
                "Recording will stop automatically"
            ]
            test_file = record_with_guidance(args.url, steps, args.output_dir)
            
        elif args.interactive:
            # Interactive recording mode
            test_file = record_interactive(args.url, args.output_dir)
            
        else:
            # Standard recording mode
            test_file = start_recorder(
                url=args.url,
                duration=args.duration,
                output_file=args.output,
                output_dir=args.output_dir
            )
        
        if test_file:
            print(f"\n✅ Recording completed successfully!")
            print(f"📄 Test file: {test_file}")
            print(f"\n🚀 Run your recorded test:")
            print(f"   python {test_file}")
            print(f"\n🧪 Or run with Qastra:")
            print(f"   qastra run {test_file}")
            
            return 0
        else:
            print(f"\n⚠️ No test generated - no actions were recorded")
            return 1
    
    except Exception as e:
        print(f"❌ Recording failed: {e}")
        return 1


def cmd_plan(args):
    """Handle the plan command."""
    import sys
    sys.path.append('.')
    
    from qastra.ai.planner.planner import TestPlanner, get_quick_analysis
    
    print(f"🧠 Qastra AI Test Planner")
    
    try:
        planner = TestPlanner(args.output_dir)
        
        if args.quick:
            # Quick analysis mode
            analysis = get_quick_analysis(args.url)
            
            if 'error' not in analysis:
                print(f"\n✅ Quick analysis completed!")
                print(f"📄 Use 'qastra plan {args.url}' for detailed test planning")
                return 0
            else:
                print(f"\n❌ Analysis failed: {analysis['error']}")
                return 1
        
        elif args.multi:
            # Multi-site planning mode
            print(f"📊 Multi-site planning mode")
            
            # Read URLs from file or use provided URL as first in list
            urls = []
            
            # For now, treat the URL argument as a file path or single URL
            if os.path.isfile(args.url):
                try:
                    with open(args.url, 'r') as f:
                        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                except Exception as e:
                    print(f"❌ Failed to read URLs from file: {e}")
                    return 1
            else:
                # Single URL mode
                urls = [args.url]
            
            if not urls:
                print(f"❌ No URLs found for multi-site planning")
                return 1
            
            print(f"📋 Planning tests for {len(urls)} sites")
            
            if len(urls) == 1:
                # Single URL - use regular planning
                test_plan = planner.plan_tests(args.url)
            else:
                # Multiple URLs
                test_plan = planner.plan_multiple_pages(urls)
            
            if 'error' not in test_plan:
                print(f"\n✅ Multi-site planning completed!")
                return 0
            else:
                print(f"\n❌ Planning failed: {test_plan['error']}")
                return 1
        
        else:
            # Standard single-site planning
            test_plan = planner.plan_tests(args.url)
            
            if 'error' not in test_plan:
                print(f"\n✅ Test planning completed!")
                
                # Show next steps
                page_info = test_plan.get('page_info', {})
                stats = test_plan.get('test_statistics', {})
                
                print(f"\n🎯 Next Steps:")
                print(f"1. Generate automated tests: qastra generate {args.url}")
                print(f"2. Record user interactions: qastra record {args.url}")
                print(f"3. Run natural language tests: qastra test \"<command>\"")
                print(f"4. Run smart locator tests: qastra smart {args.url}")
                
                if stats.get('critical_priority', 0) > 0:
                    print(f"\n🔥 Critical tests identified: {stats['critical_priority']}")
                    print(f"   Start with these tests for maximum impact!")
                
                return 0
            else:
                print(f"\n❌ Planning failed: {test_plan['error']}")
                return 1
    
    except Exception as e:
        print(f"❌ Test planning failed: {e}")
        return 1


def cmd_auto_fix(args):
    """Handle the auto-fix command."""
    import sys
    sys.path.append('.')
    
    from qastra.bot.maintenance_bot import MaintenanceBot
    
    print(f"🤖 Qastra Maintenance Bot")
    
    try:
        bot = MaintenanceBot()
        
        if args.cleanup:
            # Cleanup old backups
            print(f"🧹 Cleaning up backups older than {args.cleanup} days...")
            bot.cleanup_old_backups(args.cleanup)
            return 0
        
        if args.status:
            # Show status
            bot.print_status()
            return 0
        
        # Configure bot based on arguments
        if args.dry_run:
            bot.configure(auto_commit=False, auto_pr=False)
            print("🧪 Dry run mode - fixes will be applied but not committed")
        elif args.no_commit:
            bot.configure(auto_commit=False, auto_pr=False)
            print("⏸️  No-commit mode - fixes will be applied but not committed")
        elif args.no_pr:
            bot.configure(auto_commit=True, auto_pr=False)
            print("📝 Commit-only mode - fixes will be committed but no PR created")
        
        # Check dependencies
        if not bot.pr_creator.setup_environment():
            print("⚠️  Some dependencies are missing. Bot may not function fully.")
        
        # Run maintenance cycle
        result = bot.run_maintenance_cycle()
        
        if result['success']:
            print(f"\n✅ Maintenance completed successfully!")
            
            if result['fixes_applied'] > 0:
                print(f"🔧 {result['fixes_applied']} fix(es) applied")
                
                if not args.dry_run and not args.no_commit:
                    if result['changes_committed']:
                        print(f"📝 Changes committed")
                    
                    if not args.no_pr and result['pr_created']:
                        print(f"🔀 Pull request created")
                        print(f"   Review and merge the PR to complete the fix")
                else:
                    print(f"💡 Run without --dry-run to commit and create PR")
            
            return 0
        else:
            print(f"\n❌ Maintenance failed: {result.get('error', 'Unknown error')}")
            return 1
    
    except Exception as e:
        print(f"❌ Auto-fix failed: {e}")
        return 1


def cmd_report(args):
    """Handle the report command."""
    import sys
    sys.path.append('.')
    
    from qastra.report.report_builder import collect_results
    from qastra.report.report_writer import ReportWriter, write_all_reports, open_report
    
    print(f"📊 Qastra Report Generator")
    
    try:
        # Load test results
        if args.input:
            # Load from file
            with open(args.input, 'r') as f:
                test_results = json.load(f)
            print(f"📁 Loaded {len(test_results)} test results from {args.input}")
        else:
            # Generate sample data for demo
            test_results = _generate_sample_test_results()
            print(f"📝 Generated {len(test_results)} sample test results")
        
        # Collect and process results
        session_info = {
            'environment': 'local',
            'browser': 'chromium',
            'headless': True,
            'test_runner': 'Qastra CLI'
        }
        
        report_data = collect_results(test_results, session_info)
        
        # Generate reports
        writer = ReportWriter(args.output_dir)
        
        if args.format == 'all':
            reports = writer.write_all_formats(report_data)
            print(f"\n✅ Generated {len(reports)} report format(s):")
            for format_name, report_path in reports.items():
                print(f"   📄 {format_name.upper()}: {report_path}")
        else:
            if args.format == 'html':
                report_path = writer.write_html_report(report_data)
            elif args.format == 'json':
                report_path = writer.write_json_report(report_data)
            elif args.format == 'simple':
                report_path = writer.write_simple_report(report_data)
            elif args.format == 'email':
                report_path = writer.write_email_report(report_data)
            elif args.format == 'junit':
                report_path = writer.write_junit_report(report_data)
            
            print(f"\n✅ Generated {args.format.upper()} report: {report_path}")
        
        # Show summary
        summary = report_data.get('summary', {})
        print(f"\n📊 Test Summary:")
        print(f"   Total: {summary.get('total', 0)}")
        print(f"   Passed: {summary.get('passed', 0)}")
        print(f"   Failed: {summary.get('failed', 0)}")
        print(f"   Flaky: {summary.get('flaky', 0)}")
        print(f"   Pass Rate: {summary.get('pass_rate', 0):.1f}%")
        print(f"   Duration: {summary.get('total_duration', 0):.1f}s")
        
        # Open report if requested
        if args.open:
            print(f"\n🌐 Opening report in browser...")
            writer.open_report()
        else:
            print(f"\n💡 To open the report, run:")
            print(f"   qastra report --format {args.format} --open")
            print(f"   Or open directly: {os.path.join(args.output_dir, 'report.html')}")
        
        return 0
    
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return 1


def _generate_sample_test_results():
    """Generate sample test results for demonstration."""
    import random
    from datetime import datetime, timedelta
    
    test_names = [
        'login_test', 'search_test', 'checkout_test', 'profile_test',
        'registration_test', 'password_reset_test', 'product_detail_test',
        'cart_add_test', 'visual_homepage_test', 'visual_login_test'
    ]
    
    categories = ['authentication', 'search', 'ecommerce', 'forms', 'visual']
    browsers = ['chromium', 'firefox', 'webkit']
    statuses = ['PASS', 'FAIL', 'FLAKY']
    
    results = []
    base_time = datetime.now() - timedelta(minutes=30)
    
    for i, name in enumerate(test_names):
        status = random.choices(statuses, weights=[70, 20, 10])[0]
        category = random.choice(categories)
        browser = random.choice(browsers)
        duration = random.uniform(0.5, 5.0)
        
        result = {
            'name': name,
            'status': status,
            'duration': duration,
            'browser': browser,
            'category': category,
            'timestamp': (base_time + timedelta(minutes=i*3)).isoformat(),
            'tags': [category, browser] if random.random() > 0.5 else [category]
        }
        
        if status == 'FAIL':
            result['error_message'] = f"Element not found: #{random.choice(['login-btn', 'submit-btn', 'search-input'])}"
        
        if category == 'visual':
            result['screenshot'] = f"screenshots/{name}.png"
            if status == 'FAIL':
                result['visual_diff'] = f"visual_diffs/{name}_diff.png"
                result['difference_score'] = random.uniform(5.0, 25.0)
        
        results.append(result)
    
    return results


def cmd_version(args):
    """Handle the version command."""
    try:
        from qastra import __version__
        version = __version__
    except ImportError:
        version = "0.1.0"
    
    print(f"Qastra v{version}")
    print(f"AI-powered test automation framework")
    print(f"https://github.com/qastra/qastra")
    return 0


def cmd_init(args):
    """Handle the init command."""
    target_dir = Path(args.directory)
    
    # Create directory structure
    directories = [
        'tests',
        'generated_tests',
        '.qastra_cache',
        '.qastra_cache/locators'
    ]
    
    print(f"🚀 Initializing Qastra project in: {target_dir}")
    
    for directory in directories:
        dir_path = target_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")
    
    # Create example test file
    example_test = '''#!/usr/bin/env python3
"""
Example Qastra test
"""

from playwright.sync_api import sync_playwright

def test_example():
    """Example test using Qastra self-healing locators."""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navigate to a website
            page.goto("https://example.com")
            page.wait_for_load_state("networkidle")
            
            # Click a link (Qastra will heal if locator fails)
            page.click("text=More information")
            
            # Wait for navigation
            page.wait_for_load_state("networkidle")
            
            print("✅ Test completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
        
        finally:
            browser.close()

if __name__ == "__main__":
    test_example()
'''
    
    example_file = target_dir / "tests" / "example_test.py"
    with open(example_file, 'w') as f:
        f.write(example_test)
    print(f"  Created: tests/example_test.py")
    
    # Create README
    readme_content = '''# Qastra Project

AI-powered test automation with self-healing locators.

## Quick Start

1. Run the example test:
   ```bash
   qastra run tests/example_test.py
   ```

2. Generate a test from a URL:
   ```bash
   qastra generate https://example.com
   ```

3. Run AI-assisted testing:
   ```bash
   qastra ai-assist https://example.com
   ```

4. View healing reports:
   ```bash
   qastra heal-report
   ```

## Directory Structure

- `tests/` - Your test files
- `generated_tests/` - AI-generated tests
- `.qastra_cache/` - Locator cache and healing data

## Features

- 🤖 Self-healing locators
- 🧠 AI test generation
- 📊 Healing reports
- 🔄 Parallel test execution
'''
    
    readme_file = target_dir / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print(f"  Created: README.md")
    
    print(f"\n✅ Qastra project initialized!")
    print(f"\nNext steps:")
    print(f"  1. Run example test: qastra run tests/example_test.py")
    print(f"  2. Generate tests: qastra generate <url>")
    print(f"  3. View help: qastra --help")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Map commands to handlers
    command_handlers = {
        'run': cmd_run,
        'generate': cmd_generate,
        'heal-report': cmd_heal_report,
        'ai-assist': cmd_ai_assist,
        'test': cmd_nlp_test,
        'visual': cmd_visual_test,
        'smart': cmd_smart_test,
        'record': cmd_record,
        'plan': cmd_plan,
        'auto-fix': cmd_auto_fix,
        'report': cmd_report,
        'version': cmd_version,
        'init': cmd_init
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print(f"\n⏹️  Operation cancelled by user")
            return 130
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return 1
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
