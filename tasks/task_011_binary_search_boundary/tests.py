from buggy import binary_search


def test_finds_first_item():
    assert binary_search([1, 3, 5, 7], 1) == 0


def test_finds_last_item():
    assert binary_search([1, 3, 5, 7], 7) == 3


def test_missing_item():
    assert binary_search([1, 3, 5, 7], 6) == -1
