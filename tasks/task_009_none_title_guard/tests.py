from buggy import clean_title


def test_regular_title():
    assert clean_title("  hello world ") == "Hello world"


def test_blank_title():
    assert clean_title("   ") == ""


def test_none_title():
    assert clean_title(None) == ""
