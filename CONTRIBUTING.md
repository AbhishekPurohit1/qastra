# 🤝 Contributing to Qastra

**Thank you for your interest in contributing!** This guide will help you get started.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of browser automation

### Setup Development Environment

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/qastra.git
cd qastra

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate     # Windows

# 3. Install in development mode
pip install -e .
pip install -e .[dev]

# 4. Install Playwright browsers
playwright install

# 5. Run tests to verify setup
python -m pytest tests/
```

## 🏗️ Project Structure

```
qastra/
├── qastra/                 # Main package
│   ├── core/              # Core automation engine
│   ├── ai/                # AI-powered features
│   ├── browser/           # Browser management
│   ├── cli/               # Command-line interface
│   ├── recorder/          # Test recording
│   ├── reporter/          # HTML reports
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── examples/              # Example tests
├── docs/                  # Documentation
└── scripts/               # Development scripts
```

## 🧪 Running Tests

### Local Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_core.py

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=qastra --cov-report=html
```

### Integration Testing

```bash
# Run integration tests (requires browsers)
python -m pytest tests/integration/

# Run specific browser tests
python -m pytest tests/integration/ --browser chromium
python -m pytest tests/integration/ --browser firefox
```

### Performance Testing

```bash
# Run performance benchmarks
python scripts/benchmark.py

# Test AI performance
python scripts/ai_performance.py
```

## 📝 Coding Style

### Python Standards

We follow [PEP 8](https://pep8.org/) with some modifications:

```python
# Use 100 character line length
# Use snake_case for variables and functions
# Use PascalCase for classes
# Use UPPER_CASE for constants

# Good:
def find_element_by_intent(page, intent, confidence_threshold=0.8):
    """Find element using AI intent matching."""
    pass

class SmartLocator:
    """AI-powered element locator."""
    pass

MAX_TIMEOUT = 30000  # milliseconds
```

### Type Hints

Use type hints for all public functions:

```python
from typing import List, Dict, Optional, Union
from playwright.sync_api import Page

def find_element(
    page: Page, 
    intent: str, 
    timeout: Optional[int] = None
) -> Optional[Any]:
    """Find element by intent."""
    pass
```

### Documentation

Use Google-style docstrings:

```python
def click_element(intent: str, **kwargs) -> bool:
    """Click an element using intent matching.
    
    Args:
        intent: Human-readable description of element
        **kwargs: Additional options (timeout, index, etc.)
    
    Returns:
        True if click was successful, False otherwise
        
    Raises:
        ElementNotFoundError: If element cannot be found
        TimeoutError: If element not found within timeout
        
    Example:
        >>> click_element("login button")
        True
    """
    pass
```

## 🐛 Bug Reports

### Reporting Issues

1. **Search existing issues** first
2. **Use the issue template** provided
3. **Include minimal reproduction case**
4. **Add screenshots/videos** for UI issues
5. **Provide system information**

### Issue Template

```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior  
What actually happened

## Environment
- OS: [e.g. macOS 12.0]
- Python: [e.g. 3.9.0]
- Qastra: [e.g. 0.1.1]
- Browser: [e.g. Chrome 95.0]

## Additional Context
Any other relevant information
```

## ✨ Feature Requests

### Proposing New Features

1. **Check roadmap** for planned features
2. **Open issue** with "feature-request" label
3. **Describe use case** clearly
4. **Consider API design**
5. **Discuss implementation**

### Feature Request Template

```markdown
## Feature Description
Clear description of proposed feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How should it work?

## API Design
Example API usage

## Alternatives Considered
Other approaches you thought of

## Additional Context
Any other relevant information
```

## 🔧 Development Workflow

### 1. Create Branch

```bash
# For bug fixes
git checkout -b fix/issue-123-description

# For features  
git checkout -b feature/feature-name

# For documentation
git checkout -b docs/improvement-name
```

### 2. Make Changes

- **Small, focused commits**
- **Clear commit messages**
- **Add tests for new features**
- **Update documentation**

### 3. Test Your Changes

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run linting
black qastra/
flake8 qastra/
mypy qastra/

# Run full test suite
python -m pytest tests/ --cov=qastra
```

### 4. Submit Pull Request

- **Update CHANGELOG.md**
- **Add entry to release notes**
- **Link relevant issues**
- **Request review from maintainers**

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change  
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] CHANGELOG.md updated
```

## 🧠 AI Feature Contributions

### Improving AI Locators

```python
# Add new intent patterns
INTENT_PATTERNS = {
    "login": ["sign in", "log in", "submit", "continue"],
    "register": ["sign up", "create account", "join"],
    # Add your patterns here
}

# Improve scoring algorithm
def calculate_confidence(element, intent):
    """Calculate match confidence score."""
    # Your improvement here
    pass
```

### Adding New AI Features

1. **Research existing approaches**
2. **Design API interface**  
3. **Implement with tests**
4. **Document behavior**
5. **Add examples**

### AI Testing Guidelines

```python
# Test AI features with various scenarios
def test_ai_locator_variations():
    """Test AI works with different page structures."""
    pass

def test_ai_confidence_scoring():
    """Test confidence scores are accurate."""
    pass

def test_ai_performance():
    """Test AI performance is acceptable."""
    pass
```

## 📚 Documentation Contributions

### Improving Documentation

- **Fix typos and grammar**
- **Add missing examples**
- **Improve clarity**
- **Add troubleshooting sections**

### Documentation Structure

```
docs/
├── user-guide/          # User documentation
├── api-reference/       # API documentation  
├── tutorials/          # Step-by-step tutorials
├── examples/           # Code examples
└── contributing/       # This guide
```

### Writing Examples

```python
# Examples should be:
# 1. Complete and runnable
# 2. Well-commented
# 3. Real-world scenarios
# 4. Error-handled

@qastra
def example_test():
    """Complete example with error handling."""
    try:
        open_page("https://example.com")
        click("login")
        expect_page_title("Dashboard")
    except Exception as e:
        print(f"Test failed: {e}")
        raise
```

## 🚀 Release Process

### Version Bumping

```bash
# Update version in pyproject.toml
# Update CHANGELOG.md
# Create git tag
git tag v0.1.2
git push origin v0.1.2
```

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] GitHub release created
- [ ] PyPI package published

## 🏆 Recognition

### Contributors

All contributors are recognized in:
- **README.md** - Top contributors
- **CHANGELOG.md** - Feature credits  
- **Release notes** - Specific contributions
- **GitHub stars** - Community appreciation

### Types of Contributions

- **Code** - Features, fixes, improvements
- **Documentation** - Guides, examples, tutorials
- **Testing** - Bug reports, test cases
- **Community** - Support, discussions, feedback
- **Design** - UI/UX, graphics, branding

## 🆘 Getting Help

### Community Support

- **GitHub Discussions** - General questions
- **GitHub Issues** - Bug reports and features
- **Discord/Slack** - Real-time chat (if available)

### Maintainer Contact

- **Email**: abhishekpurohit444@gmail.com
- **GitHub**: @AbhishekPurohit1

### Code of Conduct

Please be respectful and inclusive. We follow the [Python Code of Conduct](https://www.python.org/psf/conduct/).

---

**🎉 Thank you for contributing to Qastra!**

Every contribution helps make browser automation better for everyone.
