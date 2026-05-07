from __future__ import annotations

import ctypes
from ctypes import byref, c_int, create_string_buffer
from pathlib import Path


class EHLLAPI:
    def __init__(self, dll_name: str = "ehlapi32.dll"):
        self.dll = self._load_dll(dll_name)

    @staticmethod
    def _candidate_dll_paths(dll_name: str) -> list[str]:
        requested = dll_name.strip()
        candidates: list[str] = []

        if requested:
            candidates.append(requested)
            if not requested.lower().endswith(".dll"):
                candidates.append(f"{requested}.dll")
        else:
            requested = "ehlapi32.dll"
            candidates.append(requested)

        common_dirs = [
            Path(r"C:\Program Files\IBM\Personal Communications"),
            Path(r"C:\Program Files (x86)\IBM\Personal Communications"),
        ]
        for base_dir in common_dirs:
            candidates.append(str(base_dir / requested))
            if not requested.lower().endswith(".dll"):
                candidates.append(str(base_dir / f"{requested}.dll"))

        # Preserve order and remove duplicates.
        deduped: list[str] = []
        for item in candidates:
            if item not in deduped:
                deduped.append(item)
        return deduped

    @classmethod
    def _load_dll(cls, dll_name: str):
        attempts: list[str] = []
        for candidate in cls._candidate_dll_paths(dll_name):
            try:
                candidate_path = Path(candidate)
                if candidate_path.is_absolute() and not candidate_path.exists():
                    attempts.append(f"{candidate} (not found)")
                    continue
                return ctypes.WinDLL(candidate)
            except OSError as exc:
                attempts.append(f"{candidate} ({exc})")

        attempted_text = "\n".join(f"- {item}" for item in attempts) if attempts else "- no candidates generated"
        raise FileNotFoundError(
            "Unable to load EHLLAPI DLL. Set EHLLAPI_DLL_PATH in your .env to the full DLL path.\n"
            f"Tried:\n{attempted_text}"
        )

    def hllapi(self, function: int, data: str, length: int, position: int) -> dict[str, int | str]:
        func = c_int(function)
        data_length = c_int(length)
        data_position = c_int(position)
        buffer = create_string_buffer(data.encode())

        self.dll.hllapi(byref(func), buffer, byref(data_length), byref(data_position))

        return {
            "buffer": buffer.value.decode(errors="ignore"),
            "length": data_length.value,
            "position": data_position.value,
        }

    def connect(self, session: str = "A") -> dict[str, int | str]:
        return self.hllapi(1, session, len(session), 0)

    def disconnect(self) -> dict[str, int | str]:
        return self.hllapi(2, "", 0, 0)

    def send_keys(self, text: str) -> dict[str, int | str]:
        return self.hllapi(3, text, len(text), 0)

    def copy_screen(self, width: int = 80, height: int = 24) -> str:
        length = width * height
        result = self.hllapi(5, " " * length, length, 0)
        return str(result["buffer"])

    def wait_for_host_ready(self, timeout_seconds: int = 5) -> bool:
        # Function 4 in EHLLAPI is wait.
        # Position receives timeout in seconds for many implementations.
        self.hllapi(4, "", 0, timeout_seconds)
        return True
