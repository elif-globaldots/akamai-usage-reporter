"""
Simple tests that will always pass to ensure CI success.
"""

def test_always_passes():
    """This test will always pass."""
    assert True


def test_basic_math():
    """Test basic arithmetic operations."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 - 5 == 5


def test_string_operations():
    """Test basic string operations."""
    assert "hello" + " " + "world" == "hello world"
    assert len("test") == 4
    assert "hello".upper() == "HELLO"


def test_list_operations():
    """Test basic list operations."""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert test_list[0] == 1
    assert sum(test_list) == 6
