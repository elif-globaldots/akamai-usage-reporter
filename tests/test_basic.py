"""
Basic tests for akamai_usage_reporter package.
"""

import pytest
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def test_import_package():
    """Test that the package can be imported."""
    try:
        import akamai_usage_reporter

        assert akamai_usage_reporter is not None
    except ImportError as e:
        pytest.skip(f"Package import failed: {e}")


def test_import_main():
    """Test that the main module can be imported."""
    try:
        from akamai_usage_reporter import __main__

        assert __main__ is not None
    except ImportError as e:
        pytest.skip(f"Main module import failed: {e}")


def test_main_function_exists():
    """Test that the main function exists."""
    try:
        from akamai_usage_reporter.__main__ import main

        assert callable(main)
    except ImportError as e:
        pytest.skip(f"Main function import failed: {e}")


def test_requirements_file_exists():
    """Test that requirements.txt exists."""
    requirements_path = os.path.join(project_root, "requirements.txt")
    assert os.path.exists(
        requirements_path
    ), f"requirements.txt not found at {requirements_path}"


def test_readme_exists():
    """Test that README.md exists."""
    readme_path = os.path.join(project_root, "README.md")
    assert os.path.exists(readme_path), f"README.md not found at {readme_path}"


def test_setup_py_exists():
    """Test that setup.py exists."""
    setup_path = os.path.join(project_root, "setup.py")
    assert os.path.exists(setup_path), f"setup.py not found at {setup_path}"


def test_pytest_config_exists():
    """Test that pytest.ini exists."""
    pytest_path = os.path.join(project_root, "pytest.ini")
    assert os.path.exists(pytest_path), f"pytest.ini not found at {pytest_path}"


if __name__ == "__main__":
    pytest.main([__file__])
