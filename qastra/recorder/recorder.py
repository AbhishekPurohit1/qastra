"""
Qastra Recorder - Turn manual browser actions into automated tests.

This module captures user interactions and generates Qastra test code automatically.
"""

import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright


class QastraRecorder:
    """Main recorder class that captures browser actions and generates tests."""
    
    def __init__(self):
        self.actions = []
        self.start_url = None
        self.recording_start_time = None
        
    def normalize_text(self, text):
        """Normalize element text to clean intent-based identifiers."""
        if not text:
            return "element"
            
        # Clean up common text
        text = text.strip().lower()
        
        # Handle special cases first
        if "submit" in text:
            return "submit"
        if "click" in text and "here" in text:
            return "click_here"
            
        # Convert to intent-based names
        synonyms = {
            "sign in": "login",
            "log in": "login", 
            "register": "signup",
            "sign up": "signup",
            "create account": "signup",
            "search": "search",
            "find": "search",
            "menu": "menu",
            "navigation": "menu",
            "profile": "profile",
            "account": "profile",
            "settings": "settings",
            "configuration": "settings",
            "logout": "logout",
            "sign out": "logout",
            "exit": "logout"
        }
        
        for key, value in synonyms.items():
            if key in text:
                return value
                
        # Remove common button text
        remove_words = ["button", "btn", "click", "go", "continue", "next", "back"]
        for word in remove_words:
            text = text.replace(word, "").strip()
            
        # Handle empty results
        if not text or len(text) < 2:
            return "element"
            
        # Return first meaningful word
        words = text.split()[:2]  # Take first 2 words max
        return "_".join(words)
    
    def record_click(self, selector):
        """Record a click action."""
        normalized = self.normalize_text(selector)
        action = f'click("{normalized}")'
        self.actions.append(action)
        print(f"🎯 Recorded: {action}")
        
    def record_type(self, name, value):
        """Record a typing action."""
        normalized_name = self.normalize_text(name)
        # Don't record sensitive data like passwords
        if "password" in normalized_name or "pass" in normalized_name:
            value = "your_password"
        action = f'type_into("{normalized_name}", "{value}")'
        self.actions.append(action)
        print(f"⌨️  Recorded: {action}")
        
    def record_navigation(self, url):
        """Record page navigation."""
        action = f'open_page("{url}")'
        self.actions.append(action)
        print(f"🌐 Recorded: {action}")
        
    def generate_test_file(self, output_file="recorded_test.py"):
        """Generate a Python test file from recorded actions."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f'''"""Auto-generated test by Qastra Recorder
Generated on: {timestamp}
URL: {self.start_url}
"""

from qastra import *

qastra("Recorded Test")

# Navigate to starting page
open_page("{self.start_url}")

'''
        
        # Add recorded actions
        for action in self.actions:
            if not action.startswith('open_page'):  # Skip duplicate navigation
                content += f"{action}\n"
        
        # Add completion message
        content += '''
# Test completed successfully!
print("✅ Recorded test executed successfully!")
'''
        
        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"\n📝 Test file generated: {output_file}")
        print(f"🎯 Actions recorded: {len(self.actions)}")
        print(f"⏱️  Recording duration: {time.time() - self.recording_start_time:.1f}s")
        
        return output_file


def start_recorder(url, duration=60, output_file="recorded_test.py"):
    """Start Qastra recorder.
    
    Args:
        url (str): Starting URL to record
        duration (int): Recording duration in seconds (default: 60)
        output_file (str): Output test file name (default: "recorded_test.py")
    """
    recorder = QastraRecorder()
    recorder.start_url = url
    recorder.recording_start_time = time.time()
    
    print("🎬 Qastra Recorder Starting...")
    print(f"🌐 URL: {url}")
    print(f"⏱️  Duration: {duration} seconds")
    print(f"📝 Output: {output_file}")
    print("=" * 50)
    print("🎯 Interact with page - your actions will be recorded!")
    print("⌨️  Click buttons, type in forms, navigate around")
    print("🛑 Recording will stop automatically after timeout")
    print("=" * 50)
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Qastra Recorder"
        )
        page = context.new_page()
        
        # Set up event listeners
        page.expose_binding("record_click", recorder.record_click)
        page.expose_binding("record_type", recorder.record_type)
        
        # Inject JavaScript to capture events
        page.evaluate("""
            // Capture click events
            document.addEventListener('click', function(event) {
                let el = event.target;
                let text = el.innerText || el.value || el.id || el.name || el.placeholder || 'element';
                window.record_click(text);
            });
            
            // Capture form input events
            document.addEventListener('change', function(event) {
                let el = event.target;
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                    let name = el.name || el.id || el.placeholder || 'field';
                    let value = el.value;
                    window.record_type(name, value);
                }
            });
            
            // Capture navigation
            window.addEventListener('beforeunload', function(event) {
                let url = window.location.href;
                if (url !== window.location.href) {
                    window.record_navigation(url);
                }
            });
        """)
        
        # Navigate to starting page
        page.goto(url)
        recorder.record_navigation(url)
        
        try:
            # Wait for user interactions or timeout
            print(f"⏳ Recording... (will stop after {duration}s)")
            page.wait_for_timeout(duration * 1000)
        except KeyboardInterrupt:
            print("\n🛑 Recording stopped by user")
        except Exception as e:
            print(f"\n⚠️ Recording stopped: {e}")
        finally:
            # Generate test file
            recorder.generate_test_file(output_file)
            
            # Clean up
            context.close()
            browser.close()
            
            print("\n🎉 Recording completed!")
            print(f"🚀 Run your test: python {output_file}")
            
    return recorder


def record_interactive(url):
    """Interactive recording mode with user control."""
    print("🎬 Qastra Interactive Recorder")
    print("Commands during recording:")
    print("  • Press Ctrl+C to stop recording early")
    print("  • Close browser to finish recording")
    print("  • Interact normally with the page")
    
    return start_recorder(url, duration=120)  # 2 minutes for interactive mode
