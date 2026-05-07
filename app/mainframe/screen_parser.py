from __future__ import annotations

import re


class ScreenParser:
    def __init__(self, width: int = 80):
        self.width = width

    def parse(self, raw_screen: str) -> list[str]:
        return [raw_screen[i : i + self.width] for i in range(0, len(raw_screen), self.width)]

    def extract_menu_options(self, rows: list[str]) -> list[str]:
        options: list[str] = []
        for row in rows:
            stripped = row.strip()
            if re.match(r"^\d+\s+\S+", stripped):
                options.append(stripped)
        return options

    def detect_input_fields(self, rows: list[str]) -> list[dict[str, int | str]]:
        fields: list[dict[str, int | str]] = []
        for index, row in enumerate(rows):
            if "_" in row:
                fields.append({"row": index, "content": row.rstrip()})
        return fields

    def title(self, rows: list[str]) -> str:
        for row in rows[:3]:
            candidate = row.strip()
            if candidate:
                return candidate
        return "Unknown Screen"
