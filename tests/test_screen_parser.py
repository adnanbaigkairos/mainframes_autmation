from app.mainframe.screen_parser import ScreenParser


def test_parse_builds_rows_by_width():
    parser = ScreenParser(width=10)
    rows = parser.parse("ABCDEFGHIJ1234567890")
    assert rows == ["ABCDEFGHIJ", "1234567890"]


def test_extract_menu_options_detects_numeric_rows():
    parser = ScreenParser()
    rows = [
        "1 Customer Search                                                              ",
        "2 Reports                                                                      ",
        "Not a menu option                                                              ",
    ]
    options = parser.extract_menu_options(rows)
    assert options == ["1 Customer Search", "2 Reports"]


def test_detect_input_fields_detects_underscore_rows():
    parser = ScreenParser()
    rows = ["Customer ID: ________", "No fields here"]
    fields = parser.detect_input_fields(rows)
    assert fields == [{"row": 0, "content": "Customer ID: ________"}]
