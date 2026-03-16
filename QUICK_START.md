# ⚡ Qastra Quick Start Guide

**Test user intent, not selectors - in 5 minutes!**

## 🎯 What You'll Learn

1. Install Qastra
2. Write your first test
3. Run tests with CLI
4. Record browser actions

---

## 🚀 Step 1: Installation (30 seconds)

```bash
# Install Qastra
pip install qastra

# Install browser support
playwright install

# Verify it works
qastra --help
```

---

## ✍️ Step 2: Your First Test (2 minutes)

Create `first_test.py`:

```python
from qastra import *

@qastra
def login_test():
    print("🚀 Testing login...")
    
    # Open website
    open_page("https://example.com")
    
    # Type in form
    type_into("username", "admin")
    type_into("password", "1234")
    
    # Click button
    click("login")
    
    # Verify success
    expect_page_title_contains("Dashboard")
    
    print("✅ Test passed!")

if __name__ == "__main__":
    login_test()
```

Run it:
```bash
python first_test.py
```

---

## 🎬 Step 3: Record Tests (1 minute)

No coding required! Let Qastra record your actions:

```bash
qastra record https://example.com
```

1. Browser opens automatically
2. Click around, type in forms
3. Close browser when done
4. Test file is generated automatically

Run the recorded test:
```bash
python recorded_test.py
```

---

## 🏃 Step 4: Run Multiple Tests (30 seconds)

```bash
# Run all tests in folder
qastra run tests/

# Run tests in parallel (7x faster!)
qastra run tests/ --parallel 4

# Generate HTML report
qastra run tests/ --report
```

---

## 🎯 Real Examples

### Example 1: E-commerce Test
```python
from qastra import *

@qastra
def test_shopping():
    open_page("https://shop.example.com")
    
    # Search for product
    type_into("search", "laptop")
    click("search button")
    
    # Add to cart
    click("Add to Cart")
    
    # Checkout
    click("Checkout")
    expect_page_title_contains("Checkout")
```

### Example 2: Form Validation
```python
from qastra import *

@qastra 
def test_contact_form():
    open_page("https://example.com/contact")
    
    # Fill form
    type_into("name", "John Doe")
    type_into("email", "john@example.com")
    type_into("message", "Hello!")
    
    # Submit
    click("Send")
    
    # Verify success
    expect_page_title_contains("Thank You")
```

### Example 3: Multi-step Workflow
```python
from qastra import *

@qastra
def test_user_registration():
    open_page("https://example.com")
    
    # Step 1: Click Sign Up
    click("Sign Up")
    
    # Step 2: Fill registration form
    type_into("username", "newuser")
    type_into("email", "user@example.com")
    type_into("password", "secure123")
    click("Create Account")
    
    # Step 3: Verify email confirmation
    expect_page_title_contains("Confirm Email")
    
    # Step 4: Check email (mock)
    print("📧 Check email for confirmation link")
```

---

## 🛠️ Advanced Features

### Parallel Testing
```python
# CLI - Run 8 tests at once
qastra run tests/ --parallel 8

# Code - Cross-browser test
@cross_browser_test("Login Test", [BrowserType.CHROME, BrowserType.FIREFOX])
def login_test():
    open_page("https://example.com/login")
    click("login")
```

### Smart Assertions
```python
# Wait for element
wait_for_element("dashboard", timeout=5000)

# Expect page title
expect_page_title("Dashboard")

# Expect URL
expect_url("https://example.com/dashboard")
```

### Test Reports
```python
# CLI - Auto-generates HTML report
qastra run tests/ --report

# Report opens automatically in browser
# 📊 Professional dashboard with results
```

---

## 🎨 Why Qastra is Different

### Traditional Automation 😓
```python
# Brittle, breaks when UI changes
driver.find_element(By.XPATH, "//button[@class='btn-primary']")
driver.find_element(By.CSS_SELECTOR, "#username")
```

### Qastra 😎
```python
# Smart, understands intent
click("login")
type_into("username", "admin")
```

**Qastra understands what you mean, not just where things are.**

---

## 🏁 You're Ready!

In 5 minutes you've learned:
- ✅ Install Qastra
- ✅ Write automated tests
- ✅ Record browser actions  
- ✅ Run tests with CLI
- ✅ Generate reports

**Next Steps:**
- 📖 Read [Full Documentation](README.md)
- 🎬 Try [More Examples](examples/)
- 🤖 Explore [AI Features](AI_FEATURES.md)

---

**Happy Testing! 🎉**

*Questions? Issues?* 
👉 https://github.com/AbhishekPurohit1/qastra/issues
