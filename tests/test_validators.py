from app.testing.validators import validate_expected_text, validate_non_empty_rows


def test_validate_non_empty_rows():
    assert validate_non_empty_rows(["", " value "]) is True
    assert validate_non_empty_rows(["", "   "]) is False


def test_validate_expected_text():
    rows = ["Customer Search", "Customer ID field"]
    assert validate_expected_text(rows, "customer id")
    assert not validate_expected_text(rows, "missing text")
