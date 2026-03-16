# Qastra

AI-first browser automation framework for Python.

**Test user intent, not selectors.**

**Owner:** [AbhishekPurohit1](https://github.com/AbhishekPurohit1)

## Problem

Automation tests break because of brittle selectors.

```python
# Traditional automation - FRAGILE
driver.find_element(By.XPATH, "//button[@class='btn-primary']")
```

## Solution

Write tests using user intent.

```python
# Qastra - ROBUST
click("login")
```

## 🌟 AI-Powered Features (v0.2+)

### **Natural Language Understanding**
```python
# AI understands intent, not just text
find_element_ai(page, "the blue login button on the right")
```

### **Intent Analysis**
```python
# AI parses: "click the blue login button"
# → Target: "login"
# → Position: "right" 
# → Color: "blue"
# → Confidence: 0.8
```

### **Synonym Recognition**
```python
# AI knows these are equivalent:
click("login")      # ≈ click("sign in")
click("register")   # ≈ click("sign up")
click("search")     # ≈ click("find")
```

## 🚀 Advanced Automation Features

### **Cross-Browser Testing**
```python
@cross_browser_test("My Test", [BrowserType.CHROME, BrowserType.FIREFOX])
def my_test():
    open_page("https://example.com")
    click("button")
```

### **E2E Test Framework**
```python
test_suite = create_e2e_test("Complete User Journey")
test_suite.step("Login", lambda: UserJourney.login_flow())
test_suite.step("Navigate", lambda: UserJourney.navigation_flow())
test_suite.run_all()
```

### **Parallel Test Execution**
```python
# CLI Commands
qastra run tests                    # Sequential execution
qastra run tests --parallel 4       # Parallel with 4 workers
qastra run tests --parallel 8       # Parallel with 8 workers

# Performance: 100 tests @ 30s each
# Sequential: 50 minutes
# Parallel (8 workers): ~7 minutes
# 7x faster execution!
```

### **HTML Test Reports**
```python
# CLI Commands - Reports generated automatically
qastra run tests                    # Sequential + HTML report
qastra run tests --parallel 4       # Parallel + HTML report

# Features:
- 📊 Professional HTML dashboard
- 🌐 Auto-opens in browser (macOS)
- ✅ Pass/Fail status with details
- ⏱️ Execution timing and statistics
- 📱 Mobile-responsive design
- 🔍 Expandable error details
```

### **Test Recorder**
```python
# CLI Commands
qastra record https://example.com
qastra record https://example.com --duration 120
qastra record https://example.com --output my_test.py

# Workflow:
# 1. Browser opens automatically
# 2. Click around, type in forms
# 3. Recorder captures actions
# 4. Generates test file automatically
# 5. Run: python recorded_test.py
```

### **Smart Assertions**
```python
expect_page_title("Dashboard")
expect_url("dashboard")
wait_for_element("profile", timeout=5000)
```

## Features

### 🤖 AI Features (v0.2+)
- 🧠 **Natural Language Understanding** - AI parses user intent
- 🎯 **Context Awareness** - Understands position, color, descriptions
- 📚 **Synonym Recognition** - "login" ≈ "sign in" ≈ "submit"
- 📊 **Intent Confidence Scoring** - AI confidence levels
- 🔍 **Semantic Matching** - Beyond text to meaning

### 🚀 Automation Features
- 🧠 **Smart locator engine** - Find elements by intent, not brittle XPath/CSS selectors
- 🔄 **Self-healing elements** - Automatically adapts to UI changes
- ✨ **Clean test DSL** - Write readable tests that anyone can understand
- 🌐 **Cross-browser support** - Chrome, Firefox, Safari, Edge
- 🖥️ **CLI test runner** - Run tests from command line
- ⚡ **Parallel execution** - Run multiple tests simultaneously for 7x speed improvement
- 🎬 **Test recorder** - Turn manual browser actions into automated tests
- 📊 **HTML reports** - Professional test dashboard with auto-open
- 🛡️ **Timeout protection** - Prevent hanging tests with 5-minute timeouts
- 📱 **Mobile-responsive** - Reports work on all devices
- ⚡ **Built on Playwright** - Reliable browser automation under the hood

## Example

```python
from qastra import *

test("Login Test")

open_page("https://example.com")

type_into("username", "admin")
type_into("password", "1234")

click("login")

expect("Dashboard")
```

## Installation

```bash
pip install qastra
```

## 🚀 Quick Start

**Install in 30 seconds:**
```bash
pip install qastra
playwright install
qastra --help
```

**Your first test:**
```python
from qastra import *

@qastra
def my_test():
    open_page("https://example.com")
    click("More information")
    expect_page_title_contains("Example")

if __name__ == "__main__":
    my_test()
```

**Run it:**
```bash
python my_test.py
```

**No coding required - Record tests:**
```bash
qastra record https://example.com
# Click around, then close browser
python recorded_test.py
```

## 📖 Documentation

- **📋 [Installation Guide](INSTALLATION.md)** - Step-by-step setup for all systems
- **⚡ [Quick Start Guide](QUICK_START.md)** - Learn Qastra in 5 minutes  
- **🎬 [Examples](examples/)** - Ready-to-use test templates
- **🤖 [AI Features](AI_FEATURES.md)** - Advanced automation capabilities

## CLI Usage

```bash
# Run single test
qastra run test_login.py

# Run all tests in folder
qastra run tests/

# Run examples
qastra run examples/
```

## Why Qastra?

**Traditional automation:**
```python
driver.find_element(By.XPATH, "//button[@class='btn-primary']")
```

**Qastra:**
```python
click("login")
```

Qastra understands user intent rather than forcing you to write brittle selectors. When the UI changes, Qastra automatically heals and finds the right elements.

## Documentation

- [API Reference](https://github.com/qastra/qastra/wiki)
- [Examples](examples/)
- [Contributing Guide](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

---

**Qastra v0.1** - Initial demo release
