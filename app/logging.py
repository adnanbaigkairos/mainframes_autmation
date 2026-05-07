from __future__ import annotations

from typing import Any


class _FallbackLogger:
    def info(self, message: str, **kwargs: Any) -> None:
        _ = (message, kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        _ = (message, kwargs)

    def configure(self, **kwargs: Any) -> None:
        _ = kwargs


try:
    import logfire as _logfire

    log = _logfire
except Exception:
    log = _FallbackLogger()
