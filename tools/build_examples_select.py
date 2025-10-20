#!/usr/bin/env python3
"""Interactive helper to build one or more OmniLaTeX examples.

Prompts the user with a numbered list of example directories and executes
``python3 build.py --mode <mode> build-example <example>`` for each selection.

Usage (normally invoked through VS Code tasks):
    python3 tools/build_examples_select.py --mode dev

The script expects to be run from the repository root or receives --root.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import List


def discover_examples(root: str) -> List[str]:
    examples_dir = os.path.join(root, "examples")
    if not os.path.isdir(examples_dir):
        return []
    entries = []
    for name in sorted(os.listdir(examples_dir)):
        path = os.path.join(examples_dir, name)
        if not os.path.isdir(path):
            continue
        main_tex = os.path.join(path, "main.tex")
        if os.path.exists(main_tex):
            entries.append(name)
    return entries


def parse_selection(selection: str, names: List[str]) -> List[str]:
    selection = selection.strip()
    if not selection:
        return []
    if selection == "*":
        return names
    chosen: List[str] = []
    tokens = selection.replace(";", ",").split(",")
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        try:
            index = int(token)
        except ValueError:
            raise ValueError(f"Invalid index '{token}'. Please enter numbers like '1,3,4'.")
        if index < 1 or index > len(names):
            raise ValueError(f"Index '{index}' out of range (1..{len(names)}).")
        chosen.append(names[index - 1])
    # Deduplicate while preserving order
    seen = set()
    ordered = []
    for name in chosen:
        if name not in seen:
            ordered.append(name)
            seen.add(name)
    return ordered


def run_builds(root: str, mode: str, selections: List[str]) -> None:
    if not selections:
        print("No examples selected. Nothing to build.")
        return
    base_cmd = [sys.executable, os.path.join(root, "build.py"), "--mode", mode, "build-example"]
    for name in selections:
        print(f"\n=== Building example: {name} ===")
        completed = subprocess.run(base_cmd + [name], cwd=root)
        if completed.returncode != 0:
            print(f"[ERROR] Example '{name}' failed with exit code {completed.returncode}.")
            sys.exit(completed.returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build selected OmniLaTeX examples.")
    parser.add_argument("--mode", default="dev", choices=["dev", "prod"], help="Build mode passed to build.py")
    parser.add_argument("--root", default=os.getcwd(), help="Repository root (defaults to current working directory)")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    examples = discover_examples(root)
    if not examples:
        print("No examples with main.tex found under 'examples/'.")
        sys.exit(1)

    print("Select examples to build. Enter indices separated by commas, or '*' for all.")
    for idx, name in enumerate(examples, start=1):
        print(f"  [{idx}] {name}")

    try:
        selection = input("> ")
    except KeyboardInterrupt:
        print("\nSelection cancelled.")
        sys.exit(130)

    try:
        chosen = parse_selection(selection, examples)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(2)

    run_builds(root, args.mode, chosen)


if __name__ == "__main__":
    main()
