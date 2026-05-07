from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ScreenMemoryStore:
    def __init__(self, storage_path: Path | str = "data/screen_memory.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("{}", encoding="utf-8")

    def _read_all(self) -> dict[str, Any]:
        return json.loads(self.storage_path.read_text(encoding="utf-8"))

    def _write_all(self, payload: dict[str, Any]) -> None:
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def upsert_screen(self, screen_hash: str, data: dict[str, Any]) -> None:
        payload = self._read_all()
        payload[screen_hash] = data
        self._write_all(payload)

    def get_screen(self, screen_hash: str) -> dict[str, Any] | None:
        payload = self._read_all()
        return payload.get(screen_hash)
