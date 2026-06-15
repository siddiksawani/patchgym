from buggy import is_valid_name


def test_accepts_non_empty_name():
    assert is_valid_name("Ada") is True


def test_rejects_empty_name():
    assert is_valid_name("") is False


def test_rejects_none():
    assert is_valid_name(None) is False
