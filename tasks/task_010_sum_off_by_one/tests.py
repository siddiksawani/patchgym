from buggy import sum_items


def test_empty_list():
    assert sum_items([]) == 0


def test_one_item():
    assert sum_items([5]) == 5


def test_multiple_items():
    assert sum_items([1, 2, 3, 4]) == 10
