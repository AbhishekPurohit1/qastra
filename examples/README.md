# 🎬 Qastra Examples

**Ready-to-use test templates for every scenario!**

## 📁 File Structure

```
examples/
├── beginner_friendly_test.py    # Your first test - super simple
├── simple_login_test.py         # Login flow testing
├── ecommerce_test.py            # Shopping cart workflow
├── form_validation_test.py      # Form submission testing
├── multi_page_test.py           # Multi-page navigation
├── api_test.py                  # API integration testing
└── advanced_examples/           # Complex scenarios
    ├── cross_browser_test.py
    ├── parallel_execution.py
    └── ai_locators.py
```

## 🎯 Getting Started

### 1. Absolute Beginner
```bash
python examples/beginner_friendly_test.py
```

### 2. Login Testing
```bash
python examples/simple_login_test.py
```

### 3. E-commerce Testing
```bash
python examples/ecommerce_test.py
```

## 🛠️ Customize for Your Needs

Each example is designed to be easily modified:

**Change URLs:**
```python
# From:
open_page("https://example.com")
# To:
open_page("https://your-site.com")
```

**Change selectors:**
```python
# From:
click("login")
# To:
click("sign in")
```

**Change data:**
```python
# From:
type_into("username", "testuser")
# To:
type_into("username", "your-email@domain.com")
```

## 🚀 Run All Examples

```bash
# Run all examples
qastra run examples/

# Run in parallel (faster)
qastra run examples/ --parallel 4

# Generate HTML report
qastra run examples/ --report
```

## 📚 What Each Example Teaches

| Example | What You'll Learn |
|---------|------------------|
| `beginner_friendly_test.py` | Basic Qastra syntax |
| `simple_login_test.py` | Form filling & submission |
| `ecommerce_test.py` | Multi-step workflows |
| `form_validation_test.py` | Error handling |
| `multi_page_test.py` | Page navigation |
| `api_test.py` | API integration |

## 🎨 Create Your Own

Copy any example and modify it:

```bash
cp examples/simple_login_test.py my_test.py
# Edit my_test.py for your needs
python my_test.py
```

---

**Need more examples?** 🎬
👉 https://github.com/AbhishekPurohit1/qastra/issues
