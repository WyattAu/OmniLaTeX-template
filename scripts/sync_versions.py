#!/usr/bin/env python3
"""Synchronize version strings across the OmniLaTeX project.

Reads the canonical version from VERSION.md and updates all hardcoded
version strings across the codebase to match.

Usage:
    python scripts/sync_versions.py           # apply changes
    python scripts/sync_versions.py --dry-run  # preview only

Exit codes:
    0  all versions already match (or --dry-run with no diffs)
    1  changes were needed / applied
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

VERSION_FILE = ROOT / "VERSION.md"
SEMVER_RE = re.compile(r"v(\d+\.\d+\.\d+)")
DATE_SEMVER_RE = re.compile(r"\d{4}/\d{2}/\d{2} v\d+\.\d+\.\d+")
BARE_SEMVER_RE = re.compile(r"\d+\.\d+\.\d+")


def _read_canonical() -> tuple[str, str]:
    """Return (semver, date_str) from VERSION.md."""
    text = VERSION_FILE.read_text(encoding="utf-8")
    m_ver = SEMVER_RE.search(text)
    if not m_ver:
        sys.exit(f"ERROR: no version found in {VERSION_FILE}")
    semver = m_ver.group(1)
    m_date = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if not m_date:
        today = date.today()
        date_str = f"{today.year:04d}/{today.month:02d}/{today.day:02d}"
    else:
        parts = m_date.group(1).split("-")
        date_str = f"{parts[0]}/{parts[1]}/{parts[2]}"
    return semver, date_str


def _file_paths(pattern: str) -> list[Path]:
    return sorted(ROOT.glob(pattern))


def _update_file(
    path: Path,
    pattern: re.Pattern[str],
    replacement: str,
    dry_run: bool,
) -> bool:
    """Replace *pattern* with *replacement* in *path*. Returns True if changed."""
    text = path.read_text(encoding="utf-8")
    new_text = pattern.sub(replacement, text)
    if new_text == text:
        return False
    label = str(path.relative_to(ROOT))
    if dry_run:
        print(f"  [would update] {label}")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"  [updated]      {label}")
    return True


def sync(dry_run: bool) -> int:
    semver, date_str = _update_date_and_ver(dry_run)
    changed = False

    # --- .cls ---
    cls = ROOT / "omnilatex.cls"
    if cls.exists():
        pat = re.compile(
            r"(\\ProvidesClass\{omnilatex\}\[)\d{4}/\d{2}/\d{2} v\d+\.\d+\.\d+"
        )
        changed |= _update_file(cls, pat, rf"\g<1>{date_str} v{semver}", dry_run)

    # --- build.lua ---
    lua = ROOT / "build.lua"
    if lua.exists():
        changed |= _update_file(
            lua,
            re.compile(r'pkgversion\s*=\s*"\d+\.\d+\.\d+"'),
            f'pkgversion = "{semver}"',
            dry_run,
        )
        changed |= _update_file(
            lua,
            re.compile(r'pkgdate\s*=\s*"\d{4}-\d{2}-\d{2}"'),
            f'pkgdate = "{date_str.replace("/", "-")}"',
            dry_run,
        )

    # --- build.py TUI subtitle ---
    build_py = ROOT / "build.py"
    if build_py.exists():
        changed |= _update_file(
            build_py,
            re.compile(r'f"v\d+\.\d+\.\d+'),
            f'f"v{semver}',
            dry_run,
        )

    # --- scripts/doctype_generator.py ---
    gen = ROOT / "scripts" / "doctype_generator.py"
    if gen.exists():
        pat = re.compile(
            r"(\\ProvidesPackage\{\{config/document-types/\{name\}\}\}\[)"
            r"\d{4}/\d{2}/\d{2} v\d+\.\d+\.\d+"
        )
        changed |= _update_file(gen, pat, rf"\g<1>{date_str} v{semver}", dry_run)

    # --- mkdocs.yml ---
    mkdocs = ROOT / "mkdocs.yml"
    if mkdocs.exists():
        changed |= _update_file(
            mkdocs,
            re.compile(r"(\bversion:\s*)\d+\.\d+\.\d+"),
            rf"\g<1>{semver}",
            dry_run,
        )

    # --- lib/**/*.sty (31 files) ---
    sty_pat = re.compile(
        r"(\\ProvidesPackage\{[^}]+\}\[)\d{4}/\d{2}/\d{2} v\d+\.\d+\.\d+"
    )
    for sty in _file_paths("lib/**/*.sty"):
        changed |= _update_file(sty, sty_pat, rf"\g<1>{date_str} v{semver}", dry_run)

    # --- config/document-types/*.sty ---
    for sty in _file_paths("config/document-types/*.sty"):
        changed |= _update_file(sty, sty_pat, rf"\g<1>{date_str} v{semver}", dry_run)

    # --- config/document-settings.sty ---
    settings = ROOT / "config" / "document-settings.sty"
    if settings.exists():
        changed |= _update_file(
            settings, sty_pat, rf"\g<1>{date_str} v{semver}", dry_run
        )

    return 1 if changed else 0


def _update_date_and_ver(dry_run: bool) -> tuple[str, str]:
    semver: str = ""
    date_str: str = ""
    text = VERSION_FILE.read_text(encoding="utf-8")
    m_ver = SEMVER_RE.search(text)
    if m_ver:
        semver = m_ver.group(1)
    m_date = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m_date:
        date_str = f"{m_date.group(1)}/{m_date.group(2)}/{m_date.group(3)}"
    if not semver:
        sys.exit(f"ERROR: no version found in {VERSION_FILE}")
    if not date_str:
        today = date.today()
        date_str = f"{today.year:04d}/{today.month:02d}/{today.day:02d}"
    return semver, date_str


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synchronize version strings across OmniLaTeX"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing files",
    )
    args = parser.parse_args()
    if args.dry_run:
        print("=== DRY RUN (no files will be modified) ===\n")
    else:
        print("=== Syncing versions ===\n")
    rc = sync(dry_run=args.dry_run)
    print()
    if rc == 0:
        print("All versions already match.")
    elif args.dry_run:
        print("Changes needed (none applied).")
    else:
        print("Versions synchronized successfully.")
    sys.exit(rc)


if __name__ == "__main__":
    main()
