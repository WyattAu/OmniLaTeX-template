"""Subprocess execution wrapper with logging and timeout support."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Callable

from buildlib.ui import TerminalOutput


class CommandRunner:
    """Default timeout for all subprocess invocations (seconds)."""
    DEFAULT_TIMEOUT = 3600  # 1 hour

    def __init__(self, ui: TerminalOutput, build_mode: str, verbose: bool):
        self.ui, self.build_mode, self.verbose = ui, build_mode, verbose

    def run(
        self,
        cmd_args: list[str],
        *,
        extra_env: dict[str, str] | None = None,
        cwd: Path | None = None,
        on_line: Callable[[str], None] | None = None,
        timeout: int | None = None,
    ) -> tuple[int, list[str]]:
        """Executes a command, streams output, and returns
        (exit_code, logs). Does NOT raise on failure."""
        if self.verbose:
            self.ui.debug(
                f"RUN in '{cwd or Path.cwd()}': "
                f"{' '.join(cmd_args)}"
            )
        env = os.environ.copy()
        env["BUILD_MODE"] = self.build_mode
        if extra_env:
            env.update(extra_env)

        logs = []
        try:
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                cwd=cwd,
            )
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    logs.append(line.rstrip())
                    if on_line:
                        on_line(line.rstrip())
            return_code = process.wait(timeout=timeout or self.DEFAULT_TIMEOUT)
            return return_code, logs
        except FileNotFoundError as e:
            return -1, [f"Command not found: {cmd_args[0]}", str(e)]
        except PermissionError as e:
            return -1, [f"Permission denied: {cmd_args[0]}", str(e)]
        except OSError as e:
            return -1, [f"OS error running {cmd_args[0]}: {e}"]
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            return -1, [f"Command timed out after {timeout or self.DEFAULT_TIMEOUT}s: {cmd_args[0]}"]
