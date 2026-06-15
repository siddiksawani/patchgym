from buggy import is_strictly_passing


def test_below_threshold():
    assert is_strictly_passing(59) is False


def test_exact_threshold():
    assert is_strictly_passing(60) is False


def test_above_threshold():
    assert is_strictly_passing(61) is True
