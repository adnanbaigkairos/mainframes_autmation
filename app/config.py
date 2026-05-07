from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4.1"))
    pcomm_exe_path: str = Field(
        default_factory=lambda: os.getenv(
            "PCOMM_EXE_PATH",
            r"C:\Program Files\IBM\Personal Communications\pcsws.exe",
        )
    )
    pcomm_workspace_path: str = Field(
        default_factory=lambda: os.getenv(
            "PCOMM_WORKSPACE_PATH",
            r"C:\ProgramData\IBM\Personal Communications\IBMPLEX - IBMESYS.ws",
        )
    )
    ehllapi_dll_path: str = Field(default_factory=lambda: os.getenv("EHLLAPI_DLL_PATH", ""))
    session_id: str = Field(default_factory=lambda: os.getenv("MAINFRAME_SESSION_ID", "A"))
    screen_width: int = Field(default_factory=lambda: int(os.getenv("MAINFRAME_SCREEN_WIDTH", "80")))
    screen_height: int = Field(default_factory=lambda: int(os.getenv("MAINFRAME_SCREEN_HEIGHT", "24")))
    action_timeout_seconds: float = Field(
        default_factory=lambda: float(os.getenv("MAINFRAME_ACTION_TIMEOUT_SECONDS", "1.0"))
    )
    logfire_token: str = Field(default_factory=lambda: os.getenv("LOGFIRE_TOKEN", ""))
    data_dir: Path = Field(default_factory=lambda: Path(os.getenv("DATA_DIR", "data")))
    reports_dir: Path = Field(default_factory=lambda: Path(os.getenv("REPORTS_DIR", "reports")))


settings = Settings()
