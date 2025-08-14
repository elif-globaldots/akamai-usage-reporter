"""
Basic tests for akamai_usage_reporter package.
"""

import pytest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_import_package():
    """Test that the package can be imported."""
    import akamai_usage_reporter
    assert akamai_usage_reporter is not None


def test_import_main():
    """Test that the main module can be imported."""
    from akamai_usage_reporter import __main__
    assert __main__ is not None


def test_main_function_exists():
    """Test that the main function exists."""
    from akamai_usage_reporter.__main__ import main
    assert callable(main)


def test_requirements_file_exists():
    """Test that requirements.txt exists."""
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")
    assert os.path.exists(requirements_path)


def test_readme_exists():
    """Test that README.md exists."""
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
    assert os.path.exists(readme_path)


def test_setup_py_exists():
    """Test that setup.py exists."""
    setup_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "setup.py")
    assert os.path.exists(setup_path)


if __name__ == "__main__":
    pytest.main([__file__])
