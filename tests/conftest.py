# E:\FinalProjects\Cyberbear\Askify\tests\conftest.py
import sys
import os
import pytest
import asyncio  # Add this import

# Add both the Askify directory and its parent to Python path
askify_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, askify_dir)
sys.path.insert(0, os.path.dirname(askify_dir))

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

# Set the default fixture loop scope to avoid the deprecation warning
def pytest_configure(config):
    config.addinivalue_line(
        "asyncio_default_fixture_loop_scope",
        "function"
    )

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()