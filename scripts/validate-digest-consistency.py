#!/usr/bin/env python3
"""Validate that all CI configs reference the same Docker image digest."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_DOCKER = PROJECT_ROOT / ".env.docker"

CI_CONFIGS = [
    ".env.docker",
    ".gitlab/ci/pipeline.yml",
    ".gitea/workflows/build.yml",
    ".forgejo/workflows/build.yml",
    ".woodpecker/workflows/pipeline.yml",
    ".devcontainer/docker-compose.yml",
]

DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}")


def main() -> int:
    digests: dict[str, list[str]] = {}

    for rel_path in CI_CONFIGS:
        full_path = PROJECT_ROOT / rel_path
        if not full_path.is_file():
            print(f"WARN: {rel_path} not found", file=sys.stderr)
            continue

        content = full_path.read_text(encoding="utf-8")
        found = DIGEST_RE.findall(content)

        for d in found:
            digests.setdefault(d, []).append(rel_path)

    if not digests:
        print("ERROR: No digests found in any CI config")
        return 1

    if len(digests) == 1:
        digest = next(iter(digests))
        files = digests[digest]
        print(f"PASS: All {len(files)} files use identical digest")
        print(f"  Digest: {digest[:20]}...{digest[-10:]}")
        for f in sorted(files):
            print(f"  {f}")
        return 0

    print(f"FAIL: {len(digests)} different digests found:")
    for d, files in digests.items():
        print(f"  {d[:20]}...{d[-10:]} ({len(files)} files)")
        for f in sorted(files):
            print(f"    {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
