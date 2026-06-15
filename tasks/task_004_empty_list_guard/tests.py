from buggy import first_item_or_zero


def test_empty_list():
    assert first_item_or_zero([]) == 0


def test_one_item():
    assert first_item_or_zero([5]) == 5


def test_multiple_items():
    assert first_item_or_zero([-1, 2, 3]) == -1
