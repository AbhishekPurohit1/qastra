"""Setup script for qastra."""
from setuptools import setup, find_packages

setup(
    name="qastra",
    version="0.1.0",
    description="AI-first browser automation framework for Python",
    long_description="Qastra - Test user intent, not selectors. Smart locator engine with self-healing elements.",
    packages=find_packages(),
    python_requires=">=3.13",
    install_requires=[
        "playwright>=1.40.0",
        "click>=8.0.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "qastra=qastra.cli.cli:cli",
        ],
    },
    author="AbhishekPurohit1",
    author_email="Abhishekpurohit444@gmail.com",
    maintainer="AbhishekPurohit1",
    maintainer_email="Abhishekpurohit444@gmail.com",
    url="https://github.com/AbhishekPurohit1/qastra",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)
