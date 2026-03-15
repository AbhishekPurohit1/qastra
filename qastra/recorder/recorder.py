"""
Qastra Recorder - Turn manual browser actions into automated tests.

This module captures user interactions and generates Qastra test code automatically.
"""

import os
import time
from datetime import datetime
from typing import Optional
from playwright.sync_api import sync_playwright

from .event_listener import EventListener
from .code_generator import CodeGenerator


class QastraRecorder:
    """Main recorder class that captures browser actions and generates tests."""
    
    def __init__(self, output_dir: str = "generated_tests"):
        self.output_dir = output_dir
        self.event_listener = EventListener()
        self.code_generator = CodeGenerator(output_dir)
        self.start_url = None
        self.recording_start_time = None
        
    def start_recording(self, url: str, duration: int = 60, test_name: Optional[str] = None) -> str:
        """
        Start recording user interactions and generate test.
        
        Args:
            url: Starting URL to record
            duration: Recording duration in seconds (default: 60)
            test_name: Optional name for the generated test
            
        Returns:
            Path to generated test file
        """
        self.start_url = url
        self.recording_start_time = time.time()
        
        print("🎬 Qastra Recorder Starting...")
        print(f"🌐 URL: {url}")
        print(f"⏱️  Duration: {duration} seconds")
        print(f"📝 Output directory: {self.output_dir}")
        print("=" * 50)
        print("🎯 Interact with page - your actions will be recorded!")
        print("⌨️  Click buttons, type in forms, navigate around")
        print("🛑 Recording will stop automatically after timeout")
        print("⏹️  Press Ctrl+C to stop early")
        print("=" * 50)
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Qastra Recorder v1.0"
            )
            page = context.new_page()
            
            try:
                # Inject event listener
                self.event_listener.inject_listener(page, self.event_listener.actions)
                
                # Navigate to starting page
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(2000)  # Wait for page to stabilize
                
                print(f"✅ Browser opened and ready for recording")
                print(f"📍 Current URL: {page.url}")
                
                # Wait for user interactions or timeout
                print(f"⏳ Recording... (will stop after {duration}s)")
                
                # Show live recording stats
                self._show_live_stats(page, duration)
                
            except KeyboardInterrupt:
                print("\n🛑 Recording stopped by user")
            except Exception as e:
                print(f"\n⚠️ Recording stopped: {e}")
            finally:
                # Generate test files
                actions = self.event_listener.get_actions()
                
                if actions:
                    test_files = self.code_generator.generate_test_variants(
                        actions, url, test_name or self._generate_test_name(url)
                    )
                    
                    # Print recording summary
                    self._print_recording_summary(actions)
                    
                    print(f"\n🎉 Recording completed!")
                    print(f"📁 Generated test files:")
                    for test_file in test_files:
                        print(f"   📄 {test_file}")
                    
                    print(f"\n🚀 Run your test: python {test_files[0]}")
                    
                    return test_files[0] if test_files else None
                else:
                    print("\n⚠️ No actions recorded - no test generated")
                    return None
                
                # Clean up
                context.close()
                browser.close()
    
    def _show_live_stats(self, page, duration: int):
        """Show live recording statistics."""
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # Check if page is still open
                if page.is_closed():
                    print("\n� Browser closed - stopping recording")
                    break
                
                # Show stats every 10 seconds
                if int(time.time() - start_time) % 10 == 0 and int(time.time() - start_time) > 0:
                    actions_count = len(self.event_listener.actions)
                    elapsed = int(time.time() - start_time)
                    remaining = duration - elapsed
                    
                    print(f"⏱️  {elapsed}s elapsed, {remaining}s remaining - {actions_count} actions recorded")
                
                page.wait_for_timeout(1000)  # Check every second
                
            except Exception:
                break
    
    def _generate_test_name(self, url: str) -> str:
        """Generate test name from URL."""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace('www.', '')
            clean_domain = ''.join(c for c in domain if c.isalnum() or c in ('-', '_'))
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"recorded_{clean_domain}_{timestamp}"
        
        except:
            return f"recorded_test_{int(time.time())}"
    
    def _print_recording_summary(self, actions: list):
        """Print detailed recording summary."""
        summary = self.event_listener.get_recording_summary()
        stats = self.code_generator.get_recording_statistics(actions)
        
        print(f"\n📊 Recording Summary")
        print(f"{'='*40}")
        print(f"Total actions: {summary['total_actions']}")
        print(f"Duration: {summary['duration']:.1f}s")
        print(f"Unique intents: {summary['unique_intents']}")
        
        if summary['action_types']:
            print(f"\nAction Types:")
            for action_type, count in summary['action_types'].items():
                print(f"  {action_type}: {count}")
        
        if summary['intents']:
            print(f"\nDetected Intents:")
            for intent in summary['intents'][:10]:  # Show first 10
                print(f"  • {intent}")
            if len(summary['intents']) > 10:
                print(f"  ... and {len(summary['intents']) - 10} more")
        
        if stats['most_common_action']:
            action_type, count = stats['most_common_action']
            print(f"\nMost common action: {action_type} ({count} times)")
        
        # Show action flow
        flow = self.event_listener.get_action_flow()
        if flow:
            print(f"\nAction Flow:")
            for i, step in enumerate(flow[:10], 1):  # Show first 10 steps
                print(f"  {i}. {step}")
            if len(flow) > 10:
                print(f"  ... and {len(flow) - 10} more steps")


def start_recorder(url: str, duration: int = 60, output_file: Optional[str] = None, 
                  output_dir: str = "generated_tests") -> str:
    """
    Start Qastra recorder with smart locators and AI features.
    
    Args:
        url: Starting URL to record
        duration: Recording duration in seconds (default: 60)
        output_file: Optional output test file name
        output_dir: Output directory for generated tests
        
    Returns:
        Path to generated test file
    """
    recorder = QastraRecorder(output_dir)
    
    # Generate test name from output file if provided
    test_name = None
    if output_file and output_file.endswith('.py'):
        test_name = output_file[:-3]  # Remove .py extension
    
    return recorder.start_recording(url, duration, test_name)


def record_interactive(url: str, output_dir: str = "generated_tests") -> str:
    """
    Interactive recording mode with user control.
    
    Args:
        url: URL to record
        output_dir: Output directory for generated tests
        
    Returns:
        Path to generated test file
    """
    print("🎬 Qastra Interactive Recorder")
    print("Commands during recording:")
    print("  • Press Ctrl+C to stop recording early")
    print("  • Close browser to finish recording")
    print("  • Interact normally with the page")
    
    return start_recorder(url, duration=120, output_dir=output_dir)  # 2 minutes for interactive mode


def record_with_guidance(url: str, steps: list, output_dir: str = "generated_tests") -> str:
    """
    Record with guided steps for testing specific flows.
    
    Args:
        url: Starting URL
        steps: List of steps to guide the user through
        output_dir: Output directory for generated tests
        
    Returns:
        Path to generated test file
    """
    print("🎬 Qastra Guided Recorder")
    print("Follow these steps:")
    
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")
    
    print("\nPress Enter when ready to start recording...")
    input()
    
    return start_recorder(url, duration=180, output_dir=output_dir)  # 3 minutes for guided mode
