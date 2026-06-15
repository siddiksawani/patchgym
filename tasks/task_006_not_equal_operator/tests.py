from buggy import is_active


def test_active_status():
    assert is_active("active") is True


def test_inactive_status():
    assert is_active("inactive") is False


def test_empty_status():
    assert is_active("") is False
