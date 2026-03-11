"""Setup script for vibetest."""
from setuptools import setup, find_packages

setup(
    name="vibetest",
    version="0.1.0",
    description="AI-first browser automation framework for Python",
    long_description="VibeTest - Test user intent, not selectors. Smart locator engine with self-healing elements.",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "click>=8.0.0",
        "beautifulsoup4>=4.12.0",
    ],
    entry_points={
        "console_scripts": [
            "vibetest=vibetest.cli.cli:cli",
        ],
    },
    author="AbhishekPurohit1",
    author_email="Abhishekpurohit444@gmail.com",
    maintainer="AbhishekPurohit1",
    maintainer_email="Abhishekpurohit444@gmail.com",
    url="https://github.com/AbhishekPurohit1/vibetest",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
