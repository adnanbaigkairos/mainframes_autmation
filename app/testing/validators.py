from __future__ import annotations


def validate_non_empty_rows(rows: list[str]) -> bool:
    return any(row.strip() for row in rows)


def validate_expected_text(rows: list[str], expected_text: str) -> bool:
    haystack = "\n".join(rows).lower()
    return expected_text.lower() in haystack
