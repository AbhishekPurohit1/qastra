# VibeTest

AI-first browser automation framework for Python.

**Test user intent, not selectors.**

## Features

- 🧠 **Smart locator engine** - Find elements by intent, not brittle XPath/CSS selectors
- 🔄 **Self-healing elements** - Automatically adapts to UI changes
- ✨ **Clean test DSL** - Write readable tests that anyone can understand
- 🖥️ **CLI test runner** - Run tests from command line
- ⚡ **Built on Playwright** - Reliable browser automation under the hood

## Example

```python
from vibetest import *

test("Login Test")

open_page("https://example.com")

type_into("username", "admin")
type_into("password", "1234")

click("login")

expect("Dashboard")
```

## Installation

```bash
pip install vibetest
```

## Quick Start

1. Install Playwright browsers:
```bash
playwright install
```

2. Create a test file `test_login.py`:
```python
from vibetest import *

test("Login Flow")

open_page("https://example.com")
click("More information")
```

3. Run your test:
```bash
vibetest run test_login.py
```

## CLI Usage

```bash
# Run single test
vibetest run test_login.py

# Run all tests in folder
vibetest run tests/

# Run examples
vibetest run examples/
```

## Why VibeTest?

**Traditional automation:**
```python
driver.find_element(By.XPATH, "//button[@class='btn-primary']")
```

**VibeTest:**
```python
click("login")
```

VibeTest understands user intent rather than forcing you to write brittle selectors. When the UI changes, VibeTest automatically heals and finds the right elements.

## Documentation

- [API Reference](https://github.com/vibetest/vibetest/wiki)
- [Examples](examples/)
- [Contributing Guide](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md).

---

**VibeTest v0.1** - Initial demo release
