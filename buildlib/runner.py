"""Subprocess execution wrapper with logging and timeout support."""

from __future__ import annotations

import os
import subprocess
import threading
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
        """Execute a command, stream output, and return (exit_code, logs).

        Timeout is enforced wall-clock from process start. A daemon reader
        thread drains stdout so that the readline loop never blocks past
        the deadline.
        """
        effective_timeout = timeout or self.DEFAULT_TIMEOUT

        if self.verbose:
            self.ui.debug(f"RUN in '{cwd or Path.cwd()}': " f"{' '.join(cmd_args)}")
        env = os.environ.copy()
        env["BUILD_MODE"] = self.build_mode
        if extra_env:
            env.update(extra_env)

        logs: list[str] = []
        lock = threading.Lock()
        timeout_flag = [False]  # mutable container visible to reader thread

        def _reader(stream):
            """Read lines from *stream* until EOF or timeout."""
            try:
                for line in iter(stream.readline, ""):
                    if timeout_flag[0]:
                        break
                    stripped = line.rstrip()
                    with lock:
                        logs.append(stripped)
                    if on_line:
                        on_line(stripped)
            finally:
                try:
                    stream.close()
                except OSError:
                    pass

        process: subprocess.Popen | None = None
        reader: threading.Thread | None = None
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
                reader = threading.Thread(
                    target=_reader, args=(process.stdout,), daemon=True
                )
                reader.start()

            # Block until process exits or deadline.
            try:
                return_code = process.wait(timeout=effective_timeout)
            except subprocess.TimeoutExpired:
                timeout_flag[0] = True
                try:
                    process.kill()
                except OSError:
                    pass
                process.wait()
                if reader is not None:
                    reader.join(timeout=5)
                return -1, [
                    f"Command timed out after {effective_timeout}s: " f"{cmd_args[0]}"
                ]

            if reader is not None:
                reader.join(timeout=5)
            return return_code, logs

        except FileNotFoundError as e:
            return -1, [f"Command not found: {cmd_args[0]}", str(e)]
        except PermissionError as e:
            return -1, [f"Permission denied: {cmd_args[0]}", str(e)]
        except OSError as e:
            return -1, [f"OS error running {cmd_args[0]}: {e}"]
