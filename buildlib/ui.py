"""Terminal output with optional color support."""

from __future__ import annotations

import sys


class TerminalOutput:
    def __init__(self, use_color: bool = sys.stdout.isatty()):
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

    def header(self, m: str):
        print(f"\n{self.bold}{self.blue}=== {m} ==={self.end}")

    def info(self, m: str):
        print(f"{self.cyan}[INFO]{self.end} {m}")

    def success(self, m: str):
        print(f"{self.green}[✓] {m}{self.end}")

    def warning(self, m: str):
        print(f"{self.yellow}[⚠] {m}{self.end}")

    def error(self, m: str):
        print(f"{self.bold}{self.red}[✗] {m}{self.end}", file=sys.stderr)

    def debug(self, m: str):
        print(f"{self.gray}[DEBUG] {m}{self.end}")
