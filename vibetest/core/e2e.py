"""End-to-End testing framework for VibeTest."""

import time
from vibetest.core.actions import open_page, click, type_into
from vibetest.core.assertions import expect
from vibetest.core.cross_browser import CrossBrowser, BrowserType, cross_browser_test

class E2ETest:
    def __init__(self, name, base_url=None):
        self.name = name
        self.base_url = base_url
        self.test_steps = []
        self.passed = 0
        self.failed = 0
        
    def step(self, description, action):
        """Add a test step."""
        self.test_steps.append({
            "description": description,
            "action": action,
            "status": "pending"
        })
        
    def run_step(self, index):
        """Execute a specific test step."""
        if index >= len(self.test_steps):
            return False
            
        step = self.test_steps[index]
        print(f"📝 Step {index + 1}: {step['description']}")
        
        try:
            step['action']()
            step['status'] = 'passed'
            self.passed += 1
            print(f"✅ PASSED")
            return True
        except Exception as e:
            step['status'] = 'failed'
            self.failed += 1
            print(f"❌ FAILED: {e}")
            return False
            
    def run_all(self):
        """Run all test steps."""
        print(f"\n🚀 Running E2E Test: {self.name}")
        print("=" * 60)
        
        for i in range(len(self.test_steps)):
            if not self.run_step(i):
                break  # Stop on first failure
                
        self.print_summary()
        
    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        print(f"\n📊 Test Summary:")
        print(f"   Total: {total}")
        print(f"   Passed: {self.passed}")
        print(f"   Failed: {self.failed}")
        
        if self.failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {self.failed} test(s) failed")

class UserJourney:
    """Simulate complete user journeys."""
    
    @staticmethod
    def login_flow(username="admin", password="admin123"):
        """Complete login flow."""
        open_page("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        type_into("username", username)
        type_into("password", password)
        click("Login")
        
    @staticmethod
    def search_flow(search_term):
        """Complete search flow."""
        click("search")
        type_into("search", search_term)
        click("submit")
        
    @staticmethod
    def form_flow(form_data):
        """Complete form submission."""
        for field, value in form_data.items():
            type_into(field, value)
        click("submit")
        
    @staticmethod
    def navigation_flow():
        """Complete navigation flow."""
        click("menu")
        click("dashboard")
        click("profile")
        
    @staticmethod
    def logout_flow():
        """Complete logout flow."""
        click("logout")
        click("confirm")

def create_e2e_test(name, base_url=None):
    """Factory function to create E2E tests."""
    return E2ETest(name, base_url)
