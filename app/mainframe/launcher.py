from __future__ import annotations

import subprocess
import time
from pathlib import Path


class MainframeLauncher:
    def __init__(self, workspace_path: str, executable_path: str):
        self.workspace_path = workspace_path
        self.executable_path = executable_path

    def launch(self, startup_wait_seconds: int = 10) -> bool:
        if not Path(self.executable_path).exists():
            raise FileNotFoundError("IBM PCOMM executable was not found.")

        if not Path(self.workspace_path).exists():
            raise FileNotFoundError("PCOMM workspace file was not found.")

        subprocess.Popen([self.executable_path, self.workspace_path])
        time.sleep(startup_wait_seconds)
        return True
