from __future__ import annotations

import time


class Navigator:
    def __init__(self, ehllapi, parser, wait_seconds: float = 1.0):
        self.ehllapi = ehllapi
        self.parser = parser
        self.wait_seconds = wait_seconds

    def wait_for_host(self) -> None:
        if hasattr(self.ehllapi, "wait_for_host_ready"):
            self.ehllapi.wait_for_host_ready(timeout_seconds=int(self.wait_seconds) + 1)
        else:
            time.sleep(self.wait_seconds)

    def get_screen(self) -> list[str]:
        raw = self.ehllapi.copy_screen()
        return self.parser.parse(raw)

    def press_enter(self) -> None:
        self.ehllapi.send_keys("@E")
        self.wait_for_host()

    def press_pf(self, number: int) -> None:
        self.ehllapi.send_keys(f"@{number}")
        self.wait_for_host()

    def type_text(self, text: str) -> None:
        self.ehllapi.send_keys(text)

    def navigate_to_menu(self, option: str) -> None:
        self.type_text(option)
        self.press_enter()
