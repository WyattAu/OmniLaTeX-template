#!/usr/bin/env python3
"""OmniLaTeX build entry point — thin wrapper around buildlib package."""

import sys


def main() -> int:
    from buildlib import main as _main

    return _main() or 0


if __name__ == "__main__":
    sys.exit(main())
