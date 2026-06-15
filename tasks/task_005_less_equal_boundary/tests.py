from buggy import is_child


def test_younger_than_twelve():
    assert is_child(11) is True


def test_exactly_twelve():
    assert is_child(12) is False


def test_older_than_twelve():
    assert is_child(13) is False
