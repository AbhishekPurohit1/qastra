"""
Qastra API - Simple interface for writing tests.

This module provides a clean, simple API for writing tests
without needing to understand the internal complexity.
"""

from .test_api import test, click, fill, navigate, wait, verify

__all__ = [
    'test',
    'click', 
    'fill',
    'navigate',
    'wait',
    'verify'
]
