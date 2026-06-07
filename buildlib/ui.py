"""Terminal output with optional color and Unicode support."""

from __future__ import annotations

import sys


class TerminalOutput:
    """Terminal output handler with color and Unicode fallback support.

    Args:
        use_color: Enable ANSI color codes (default: auto-detect TTY).
        use_unicode: Use Unicode symbols (checkmark, warning, cross).
            Falls back to ASCII ([OK], [WARN], [ERR]) when False.
    """

    def __init__(
        self,
        use_color: bool = sys.stdout.isatty(),
        use_unicode: bool = True,
    ):
        p = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "cyan": "\033[96m",
            "gray": "\033[90m",
            "bold": "\033[1m",
            "end": "\033[0m",
        }
        if use_color:
            self.__dict__.update(p)
        else:
            self.__dict__.update({k: "" for k in p})

        # Unicode symbols with ASCII fallback
        if use_unicode:
            self._check = "\u2713"
            self._warn = "\u26a0"
            self._cross = "\u2717"
        else:
            self._check = "[OK]"
            self._warn = "[WARN]"
            self._cross = "[ERR]"

    def header(self, m: str):
        print(f"\n{self.bold}{self.blue}=== {m} ==={self.end}")

    def info(self, m: str):
        print(f"{self.cyan}[INFO]{self.end} {m}")

    def success(self, m: str):
        print(f"{self.green}[{self._check}] {m}{self.end}")

    def warning(self, m: str):
        print(f"{self.yellow}[{self._warn}] {m}{self.end}")

    def error(self, m: str):
        print(f"{self.bold}{self.red}[{self._cross}] {m}{self.end}", file=sys.stderr)

    def debug(self, m: str):
        print(f"{self.gray}[DEBUG] {m}{self.end}")
