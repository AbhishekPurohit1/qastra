# 🤖 Qastra

**AI-first Playwright-based test framework that understands user intent instead of selectors.**

[![PyPI version](https://badge.fury.io/py/qastra.svg)](https://badge.fury.io/py/qastra)
[![Python versions](https://img.shields.io/pypi/pyversions/qastra.svg)](https://pypi.org/project/qastra/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://github.com/AbhishekPurohit1/qastra/workflows/CI/badge.svg)](https://github.com/AbhishekPurohit1/qastra/actions)
[![Stage: Alpha](https://img.shields.io/badge/stage-alpha-orange.svg)](https://github.com/AbhishekPurohit1/qastra)

## 🎯 Who is this for?

- **QA Engineers** who want reliable, maintainable tests
- **SDETs** building test automation frameworks  
- **Manual Testers** transitioning to automation
- **Developers** needing quick browser tests
- **Teams** wanting to reduce test maintenance

## � Problem → Solution → Example

### 😩 The Problem
```python
# Traditional automation - BRITTLE
driver.find_element(By.XPATH, "//button[@class='btn-primary']")
driver.find_element(By.CSS_SELECTOR, "#username")
```
*Breaks when UI changes, hard to read, requires selector knowledge.*

### 😎 The Solution  
```python
# Qastra - INTENT-DRIVEN
click("login")
type_into("username", "admin")
```
*Understands user intent, self-healing, readable by anyone.*

### 🚀 Real Example
```python
from qastra import *

@qastra
def login_flow():
    # Open login page
    open_page("https://example.com/login")
    
    # Fill credentials (Qastra finds the fields)
    type_into("username", "admin")
    type_into("password", "secure123")
    
    # Click login button
    click("login")
    
    # Verify success with assertions
    expect_page_title_contains("Dashboard")
    wait_for_element("welcome-message", timeout=5000)
    
    # Error handling
    try:
        click("user-profile")
        print("✅ Login successful!")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        raise

if __name__ == "__main__":
    login_flow()
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

## � Examples by Scenario

### 🎯 Core Test Flows
- **[`login_flow_intent.py`](examples/login_flow_intent.py)** - Complete authentication with error handling
- **[`ecommerce_checkout.py`](examples/ecommerce_test.py)** - Shopping cart to payment workflow  
- **[`form_validation.py`](examples/form_validation.py)** - Form submission with validation testing
- **[`multi_page_navigation.py`](examples/multi_page_test.py)** - Complex site navigation patterns

### 🤖 AI-Powered Examples  
- **[`visual_regression_demo.py`](examples/advanced/visual_regression_demo.py)** - AI-based visual testing
- **[`intent_locators.py`](examples/advanced/intent_locators.py)** - Advanced AI locator strategies
- **[`cross_browser_test.py`](examples/advanced/cross_browser_test.py)** - Multi-browser test execution

### 📝 DSL vs Python
**Qastra DSL (`.qa` files):**
```qa
# test_login.qa
open_page "https://example.com/login"
type_into "username" "admin"  
type_into "password" "secure123"
click "login"
expect_page_title "Dashboard"
```

**Equivalent Python:**
```python
# test_login.py
from qastra import *

@qastra  
def login_test():
    open_page("https://example.com/login")
    type_into("username", "admin")
    type_into("password", "secure123") 
    click("login")
    expect_page_title("Dashboard")

if __name__ == "__main__":
    login_test()
```

## 🤖 AI Features

**🧠 [Complete AI Features Guide](AI_FEATURES.md)**

| Feature | What it does | When to use | Limitations |
|---------|--------------|-------------|-------------|
| **Natural Language Understanding** | Parses user intent from simple text | Complex UI descriptions | Requires clear context |
| **Intent Confidence Scoring** | Provides match confidence (0-1) | Debugging locator issues | May need manual override |
| **Synonym Recognition** | "login" ≈ "sign in" ≈ "submit" | Robust element matching | Limited to common terms |
| **Self-Healing Locators** | Auto-adapts to UI changes | Long-running test suites | Requires fallback locators |

### 🔍 Intent Matching Behavior

**Tie-breaking Rules:**
1. **Higher confidence score wins**
2. **Element position matters** (top/left preferred)  
3. **Semantic context** (form vs navigation)
4. **Explicit locators override** (if provided)

**Confidence Thresholds:**
- `> 0.8`: High confidence - auto-select
- `0.5-0.8`: Medium - verify with user
- `< 0.5`: Low - require explicit locator

**Override Examples:**
```python
# Force specific element
click("login", selector="button[type='submit']")

# Use multiple criteria  
click("login", text="Sign In", role="button")
```

### 🔒 Privacy & Offline

**AI Processing:**
- ✅ **Local heuristics** - Pattern matching on DOM
- ✅ **Offline capable** - No external API calls required  
- ✅ **No data transmission** - Everything stays local
- ⚠️ **Optional cloud models** - For enhanced accuracy (opt-in)

## 🖥️ CLI Reference

| Flag | Description | Example |
|------|-------------|---------|
| `--parallel` | Run tests in parallel | `--parallel 4` |
| `--report` | Generate HTML report | `--report` |
| `--browser` | Specify browser | `--browser firefox` |
| `--timeout` | Set timeout (seconds) | `--timeout 30` |
| `--output` | Custom report path | `--output ./reports` |
| `--workers` | Number of parallel workers | `--workers 8` |

### 📁 Typical Project Structure
```
my_project/
├── tests/
│   ├── login_flow.py
│   ├── ecommerce.py
│   └── api_tests.py
├── config/
│   └── qastra_config.json
├── reports/          # Auto-generated HTML reports
├── .qastra_cache/    # Locator cache
├── requirements.txt
└── pytest.ini       # If using pytest integration
```

### 🔄 CI Integration

**GitHub Actions:**
```yaml
name: Qastra Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install qastra
        playwright install
    - name: Run Qastra tests
      run: qastra run tests/ --parallel 4 --report
```

**Integration with pytest:**
```python
# conftest.py
import pytest
from qastra import QastraTest

@pytest.fixture
def qastra_test():
    return QastraTest()

# test_example.py  
def test_login_with_qastra(qastra_test):
    qastra_test.open_page("https://example.com/login")
    qastra_test.type_into("username", "admin")
    qastra_test.click("login")
```

## 📖 Documentation

- **📋 [Installation Guide](INSTALLATION.md)** - Step-by-step setup for all systems
- **⚡ [Quick Start Guide](QUICK_START.md)** - Learn Qastra in 5 minutes  
- **🎬 [Examples](examples/)** - Ready-to-use test templates
- **🧠 [AI Features](AI_FEATURES.md)** - Advanced automation capabilities
- **🤝 [Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **🗺️ [Roadmap](ROADMAP.md)** - Future development plans

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
