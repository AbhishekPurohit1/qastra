# Qastra Documentation

## Overview

Qastra is an AI-first browser automation framework that allows you to write tests using natural language instead of brittle selectors.

## Quick Start

### Installation

```bash
pip install qastra
```

### Basic Usage

```python
from qastra.api.test_api import test

# Natural language tests
test("open https://example.com")
test("login with username admin password 123")
test("click login button")
test("verify welcome message")
```

### CLI Usage

```bash
# Run a Qastra DSL test file
qastra run examples/login.qa

# Run a Python test file
qastra run my_test.py

# Run a folder of Python tests (sequential / parallel)
qastra run tests
qastra run tests --parallel 4
```

## Features

### 🤖 AI-Powered Testing
- Natural language test instructions
- Smart element location
- Self-healing selectors
- Intent-based automation

### 🎯 Smart Locator Engine
- Multiple fallback strategies
- Text-based locating
- Visual element recognition
- Robust element finding

### 📊 Professional Reporting
- HTML dashboards with charts
- Screenshot capture
- Test execution analytics
- Multiple report formats

### 🤖 Maintenance Bot
- Automatic test fixing
- GitHub integration
- Pull request creation
- Backup and recovery

## API Reference

### Test Functions

#### `test(instruction, timeout=30000)`
Execute a natural language test instruction.

**Parameters:**
- `instruction`: Natural language instruction
- `timeout`: Timeout in milliseconds

**Example:**
```python
test("open https://github.com")
test("search for qastra")
test("click first result")
```

#### `click(element, timeout=10000)`
Click on an element using smart locator.

**Example:**
```python
click("login button")
click("#submit")
click("text=Submit")
```

#### `fill(element, value, timeout=10000)`
Fill an input field.

**Example:**
```python
fill("username", "admin")
fill("#password", "123")
fill("email input", "test@example.com")
```

#### `navigate(url, wait_until="networkidle")`
Navigate to a URL.

**Example:**
```python
navigate("https://example.com")
navigate("https://github.com")
```

#### `wait(condition, timeout=10000)`
Wait for a condition.

**Example:**
```python
wait(2000)  # Wait 2 seconds
wait("#loading")  # Wait for element
```

#### `verify(condition, timeout=10000)`
Verify a condition on the page.

**Example:**
```python
verify("Welcome")
verify("#dashboard")
verify("text=Success")
```

### Context Manager

```python
from qastra.api.test_api import QastraTest

with QastraTest(headless=False):
    test("open https://example.com")
    test("click login button")
    # Browser automatically cleaned up
```

## CLI Commands

### `qastra run`
Run tests from a Qastra `.qa` file or from Python test files.

```bash
# Qastra DSL
qastra run examples/login.qa

# Single Python file
qastra run examples/demo_test.py

# Folder of Python tests
qastra run tests
qastra run tests --parallel 4
```

### `qastra generate`
Generate tests from a URL.

```bash
qastra generate https://example.com
qastra generate --multi sites.txt
```

### `qastra plan`
Generate AI test plan for a website.

```bash
qastra plan https://example.com
qastra plan --quick https://example.com
```

### `qastra record`
Record browser actions to generate tests.

```bash
qastra record https://example.com
qastra record --output my_test.py
```

### `qastra report`
Generate HTML test reports.

```bash
qastra report --format html --open
qastra report --format all
```

### `qastra auto-fix`
Run maintenance bot to fix broken tests.

```bash
qastra auto-fix --status
qastra auto-fix --dry-run
qastra auto-fix --no-commit
```

## Advanced Features

### Smart Locator Engine

The smart locator engine tries multiple strategies to find elements:

1. Text content matching
2. ARIA labels
3. Button text
4. Placeholder text
5. ID and class names
6. XPath fallbacks

```python
# All these work with the smart locator
click("login button")
click("text=Login")
click("aria-label=Login")
click("#login-btn")
click(".login-button")
```

### Self-Healing Selectors

Qastra automatically heals broken selectors by:

1. Detecting element changes
2. Finding similar elements
3. Updating locators
4. Creating backups

### Visual Testing

```python
qastra visual test https://example.com
qastra visual --baseline baseline.png
```

### AI Test Generation

> Note: The new `.qa` DSL and CLI flow is the recommended entrypoint for most users.

## Configuration

### Environment Variables

```bash
export QASTRA_HEADLESS=true
export QASTRA_TIMEOUT=30000
export QASTRA_CACHE_DIR=".qastra_cache"
```

### Configuration File

Create `qastra.config.json`:

```json
{
    "browser": {
        "headless": true,
        "timeout": 30000
    },
    "smart_locator": {
        "enabled": true,
        "fallbacks": ["text", "aria", "id", "class"]
    },
    "reporting": {
        "format": "html",
        "screenshots": true
    }
}
```

## Examples

### Basic Login Test

```python
from qastra.api.test_api import test

def test_login():
    test("open https://example.com/login")
    test("fill username with admin")
    test("fill password with 123")
    test("click login button")
    test("verify dashboard")

if __name__ == "__main__":
    test_login()
```

### E-commerce Test

```python
from qastra.api.test_api import test, navigate, click, fill, verify

def test_purchase_flow():
    navigate("https://shop.example.com")
    
    # Search for product
    fill("search input", "laptop")
    click("search button")
    
    # Select first product
    click("first product")
    
    # Add to cart
    click("add to cart")
    verify("item added to cart")
    
    # Checkout
    click("checkout button")
    fill("email", "test@example.com")
    fill("card number", "4111111111111111")
    click("complete purchase")
    verify("order confirmed")

if __name__ == "__main__":
    test_purchase_flow()
```

### Multi-Step Test with Context Manager

```python
from qastra.api.test_api import QastraTest, test

def test_user_journey():
    with QastraTest(headless=False):
        # Registration
        test("open https://example.com/signup")
        test("fill name with John Doe")
        test("fill email with john@example.com")
        test("fill password with secure123")
        test("click signup button")
        
        # Login
        test("open https://example.com/login")
        test("fill email with john@example.com")
        test("fill password with secure123")
        test("click login button")
        
        # Profile
        test("verify welcome John")
        test("click profile button")
        test("verify profile page")

if __name__ == "__main__":
    test_user_journey()
```

## Troubleshooting

### Common Issues

#### Element Not Found
- Use more descriptive element names
- Check if element is in an iframe
- Increase timeout values

#### Test Fails Intermittently
- Add explicit waits
- Use more specific selectors
- Check for network conditions

#### Browser Not Launching
- Install Playwright browsers: `playwright install`
- Check system dependencies
- Try non-headless mode for debugging

### Debug Mode

```python
from qastra.api.test_api import QastraTest

with QastraTest(headless=False):  # See browser actions
    test("open https://example.com")
    # Add debug prints or breakpoints
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: https://github.com/AbhishekPurohit1/qastra/issues
- Documentation: https://github.com/AbhishekPurohit1/qastra#readme
- Examples: https://github.com/AbhishekPurohit1/qastra/tree/main/examples
