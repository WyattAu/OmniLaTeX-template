#!/usr/bin/env python3
"""Validate semantic versioning consistency across the project."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def extract_version(text: str, pattern: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1) if m else None


def main() -> int:
    errors: list[str] = []

    # 1. VERSION.md
    version_md = PROJECT_ROOT / "VERSION.md"
    version_md_text = version_md.read_text(encoding="utf-8")
    version_md_ver = extract_version(version_md_text, r"v(\d+\.\d+\.\d+)")
    if not version_md_ver:
        errors.append("VERSION.md: no version found")

    # 2. build.lua
    build_lua = PROJECT_ROOT / "build.lua"
    build_lua_text = build_lua.read_text(encoding="utf-8")
    build_lua_ver = extract_version(
        build_lua_text, r'pkgversion\s*=\s*"(\d+\.\d+\.\d+)"'
    )
    if not build_lua_ver:
        errors.append("build.lua: no pkgversion found")

    # 3. Check consistency
    versions = {
        "VERSION.md": version_md_ver,
        "build.lua": build_lua_ver,
    }
    unique_versions = set(v for v in versions.values() if v)
    if len(unique_versions) > 1:
        for name, ver in versions.items():
            if ver and ver != version_md_ver:
                errors.append(f"{name}: version {ver} != VERSION.md {version_md_ver}")

    # 4. Check CHANGELOG entry exists
    if version_md_ver:
        changelog_entry = PROJECT_ROOT / "CHANGELOG" / f"v{version_md_ver}.md"
        if not changelog_entry.is_file():
            errors.append(f"CHANGELOG/v{version_md_ver}.md: missing")

    # 5. Check CHANGELOG index references latest version
    changelog_index = PROJECT_ROOT / "CHANGELOG.md"
    if changelog_index.is_file() and version_md_ver:
        index_text = changelog_index.read_text(encoding="utf-8")
        if f"v{version_md_ver}" not in index_text:
            errors.append(f"CHANGELOG.md: does not reference v{version_md_ver}")

    if errors:
        print("FAIL: SemVer consistency errors:")
        for e in errors:
            print(f"  {e}")
        return 1

    print(f"PASS: Version {version_md_ver} consistent across all files")
    for name, ver in versions.items():
        if ver:
            print(f"  {name}: v{ver}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
