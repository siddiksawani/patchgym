from buggy import is_public_by_default


def test_public_default_is_enabled():
    assert is_public_by_default() is True
