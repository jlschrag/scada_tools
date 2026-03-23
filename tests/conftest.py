"""Pytest configuration and fixtures"""

import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables before any tests run"""
    # Set required credentials for testing
    os.environ.setdefault("IGNITION_USERNAME", "test_user")
    os.environ.setdefault("IGNITION_PASSWORD", "test_password")
    
    yield
    
    # Cleanup (optional)
    pass
