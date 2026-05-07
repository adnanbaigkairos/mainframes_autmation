from __future__ import annotations


class SessionManager:
    def __init__(self, ehllapi, session_id: str = "A"):
        self.ehllapi = ehllapi
        self.session_id = session_id
        self.connected = False

    def connect(self) -> bool:
        result = self.ehllapi.connect(self.session_id)
        self.connected = bool(result)
        return self.connected

    def ensure_connected(self) -> None:
        if not self.connected:
            self.connect()

    def disconnect(self) -> None:
        if self.connected:
            self.ehllapi.disconnect()
        self.connected = False
