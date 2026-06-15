from buggy import is_adult


def test_minor():
    assert is_adult(17) is False


def test_exactly_eighteen():
    assert is_adult(18) is True


def test_over_eighteen():
    assert is_adult(21) is True
