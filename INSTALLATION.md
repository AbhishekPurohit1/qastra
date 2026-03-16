# 🚀 Qastra Installation Guide

**AI-first browser automation framework for Python**

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: For browser automation

## 🔧 Quick Installation (All Systems)

### Step 1: Install Qastra
```bash
pip install qastra
```

### Step 2: Install Browser Dependencies
```bash
playwright install
```

### Step 3: Verify Installation
```bash
qastra --help
```

## 🖥️ Platform-Specific Instructions

### Windows
```powershell
# Using PowerShell
pip install qastra
playwright install
qastra --help

# Using CMD
pip install qastra
playwright install
qastra --help
```

### macOS
```bash
# Using Terminal
pip install qastra
playwright install
qastra --help

# If pip not found, try pip3
pip3 install qastra
playwright install
qastra --help
```

### Linux
```bash
# Using Terminal
pip install qastra
playwright install
qastra --help

# If pip not found, try pip3
pip3 install qastra
playwright install
qastra --help
```

## 🎯 Your First Test

Create a file `my_first_test.py`:

```python
from qastra import *

@qastra
def my_test():
    print("🚀 Starting my first test...")
    
    # Open a website
    open_page("https://example.com")
    
    # Click a button
    click("More information")
    
    print("✅ Test completed!")

# Run the test
if __name__ == "__main__":
    my_test()
```

Run your test:
```bash
python my_first_test.py
```

## 🛠️ CLI Commands

### Run Tests
```bash
# Run single test file
qastra run my_test.py

# Run all tests in folder
qastra run tests/

# Run with parallel execution
qastra run tests/ --parallel 4
```

### Record Browser Actions
```bash
# Record your actions
qastra record https://example.com

# Record with duration limit
qastra record https://example.com --duration 60

# Record to specific file
qastra record https://example.com --output my_test.py
```

### Parallel Testing
```bash
# Sequential execution
qastra sequential tests/

# Parallel execution (faster)
qastra parallel tests/ --workers 4
```

## 🔍 Troubleshooting

### Common Issues

**"qastra command not found"**
```bash
# Find where qastra is installed
python -c "import qastra; print(qastra.__file__)"

# Add to PATH (example for macOS/Linux)
export PATH="$PATH:$(python -c "import site; print(site.USER_BASE + '/bin')")"

# Windows - add Python Scripts to PATH
# Usually: C:\Users\YourName\AppData\Roaming\Python\PythonXX\Scripts
```

**"playwright not found"**
```bash
# Install playwright browsers
playwright install

# Or install specific browsers
playwright install chromium
playwright install firefox
playwright install webkit
```

**Permission Issues**
```bash
# Use user installation
pip install --user qastra

# Or use virtual environment
python -m venv qastra_env
source qastra_env/bin/activate  # Linux/macOS
# qastra_env\Scripts\activate  # Windows
pip install qastra
playwright install
```

## 🌐 Browser Support

Qastra supports all major browsers:
- ✅ Chrome/Chromium
- ✅ Firefox  
- ✅ Safari (macOS)
- ✅ Edge (Windows)

## 📚 Next Steps

1. **Read the [Main Documentation](README.md)**
2. **Try [Examples](examples/)**
3. **Join our Community**
4. **Report Issues**

## 🆘 Need Help?

- **Documentation**: https://github.com/AbhishekPurohit1/qastra
- **Issues**: https://github.com/AbhishekPurohit1/qastra/issues
- **PyPI**: https://pypi.org/project/qastra/

---

**Happy Testing! 🎉**
