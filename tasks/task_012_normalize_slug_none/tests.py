from buggy import normalize_slug


def test_normalizes_spaces_and_case():
    assert normalize_slug(" Hello World ") == "hello-world"


def test_preserves_empty_string():
    assert normalize_slug("   ") == ""


def test_handles_none():
    assert normalize_slug(None) == ""
