from __future__ import annotations

import ctypes
from ctypes import byref, c_int, create_string_buffer


class EHLLAPI:
    def __init__(self, dll_name: str = "ehlapi32.dll"):
        self.dll = ctypes.WinDLL(dll_name)

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
