from __future__ import annotations

import hashlib
import json
from pathlib import Path

from app.logging import log


class MainframeCrawler:
    def __init__(self, navigator, parser):
        self.navigator = navigator
        self.parser = parser
        self.visited: set[str] = set()
        self.graph: dict[str, dict[str, object]] = {}

    @staticmethod
    def screen_hash(rows: list[str]) -> str:
        joined = "\n".join(rows)
        return hashlib.md5(joined.encode("utf-8")).hexdigest()

    def crawl(self, depth: int = 0, max_depth: int = 5) -> None:
        if depth > max_depth:
            return

        rows = self.navigator.get_screen()
        screen_id = self.screen_hash(rows)
        if screen_id in self.visited:
            return

        self.visited.add(screen_id)
        options = self.parser.extract_menu_options(rows)
        fields = self.parser.detect_input_fields(rows)

        self.graph[screen_id] = {
            "screen": rows,
            "title": self.parser.title(rows),
            "options": options,
            "fields": fields,
            "depth": depth,
        }

        for option in options:
            option_id = option.split(maxsplit=1)[0]
            if not option_id.isdigit():
                continue
            try:
                self.navigator.navigate_to_menu(option_id)
                self.crawl(depth + 1, max_depth)
            except Exception as exc:
                log.warning("Failed option exploration: {option} ({error})", option=option, error=str(exc))
            finally:
                try:
                    self.navigator.press_pf(3)
                except Exception as exc:
                    log.warning("Failed PF3 recovery after option {option}: {error}", option=option, error=str(exc))

    def save_graph(self, path: str | Path = "data/screen_graph.json") -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.graph, indent=2), encoding="utf-8")
        return output_path
