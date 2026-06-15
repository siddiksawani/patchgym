from buggy import normalize_name


def test_normal_name():
    assert normalize_name(" ada lovelace ") == "Ada Lovelace"


def test_blank_name():
    assert normalize_name("   ") == ""


def test_none_name():
    assert normalize_name(None) == ""
