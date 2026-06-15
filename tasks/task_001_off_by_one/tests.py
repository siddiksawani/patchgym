from buggy import count_items


def test_empty_list():
    assert count_items([]) == 0


def test_one_item():
    assert count_items(["a"]) == 1


def test_multiple_items():
    assert count_items([1, 2, 3]) == 3
