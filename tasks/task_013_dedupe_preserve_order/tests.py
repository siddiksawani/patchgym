from buggy import dedupe_preserve_order


def test_preserves_order():
    assert dedupe_preserve_order(["b", "a", "b", "c", "a"]) == ["b", "a", "c"]


def test_empty_list():
    assert dedupe_preserve_order([]) == []


def test_all_duplicates():
    assert dedupe_preserve_order([1, 1, 1]) == [1]
