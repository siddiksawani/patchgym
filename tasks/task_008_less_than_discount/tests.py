from buggy import qualifies_for_discount


def test_below_limit():
    assert qualifies_for_discount(99) is True


def test_exact_limit():
    assert qualifies_for_discount(100) is True


def test_above_limit():
    assert qualifies_for_discount(101) is False
