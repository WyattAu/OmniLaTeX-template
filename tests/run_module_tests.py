#!/usr/bin/env python3
"""Compile focused LaTeX fixtures to sanity-check OmniLaTeX modules.

Each module test lives in ``tests/module_tests/<module>/`` and provides a
``main.tex`` plus a tailored ``.latexmkrc``.  We run ``latexmk`` with different
``BUILD_MODE`` values (where relevant) and assert that markers emitted via
``\typeout`` appear in the resulting log file.  This keeps the tests cheap while
still exercising the same toolchain configuration that the template relies on.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_TESTS_ROOT = REPO_ROOT / "tests" / "module_tests"
ROOT_LATEXMKRC = REPO_ROOT / ".latexmkrc"

LATEXMK = ["latexmk", "-pdf", "-r", str(ROOT_LATEXMKRC), "-r", ".latexmkrc", "main.tex"]
LATEXMK_CLEAN = ["latexmk", "-C", "-r", str(ROOT_LATEXMKRC), "-r", ".latexmkrc", "main.tex"]


@dataclass
class ModeExpectation:
    markers: Iterable[str]


@dataclass
class ModuleTest:
    name: str
    path: Path
    modes: Dict[str, ModeExpectation]


TEST_MATRIX: List[ModuleTest] = [
    ModuleTest(
        name="core-base",
        path=MODULE_TESTS_ROOT / "core-base",
        modes={
            "dev": ModeExpectation(
                markers=[
                    "OMNIMODE:dev",
                    "OMNIDEV:TRUE",
                    "OMNIPROD:FALSE",
                    "OMNIULTRA:FALSE",
                ]
            ),
            "prod": ModeExpectation(
                markers=[
                    "OMNIMODE:prod",
                    "OMNIDEV:FALSE",
                    "OMNIPROD:TRUE",
                    "OMNIULTRA:FALSE",
                ]
            ),
            "ultra": ModeExpectation(
                markers=[
                    "OMNIMODE:ultra",
                    "OMNIDEV:FALSE",
                    "OMNIPROD:FALSE",
                    "OMNIULTRA:TRUE",
                ]
            ),
        },
    ),
    ModuleTest(
        name="code-listings",
        path=MODULE_TESTS_ROOT / "code-listings",
        modes={
            "dev": ModeExpectation(markers=["MINTED_MODE:FALSE"]),
            "ultra": ModeExpectation(markers=["MINTED_MODE:TRUE"]),
        },
    ),
    ModuleTest(
        name="graphics",
        path=MODULE_TESTS_ROOT / "graphics",
        modes={
            # Ultra-lite mode should avoid calling Inkscape, relying on cached PDFs or
            # the placeholder path. We only assert that the custom marker survived.
            "ultra": ModeExpectation(markers=["SVG_TEST:BEGIN"]),
        },
    ),
    ModuleTest(
        name="glossary",
        path=MODULE_TESTS_ROOT / "glossary",
        modes={
            "dev": ModeExpectation(markers=["GLOSSARY:BEGIN"]),
        },
    ),
    ModuleTest(
        name="bibliography",
        path=MODULE_TESTS_ROOT / "bibliography",
        modes={
            "dev": ModeExpectation(markers=["BIBLIOGRAPHY:BEGIN"]),
        },
    ),
]


def run_latexmk(cmd: List[str], cwd: Path, env: Dict[str, str]) -> subprocess.CompletedProcess:
    """Run latexmk and raise a rich error if it fails."""
    print(f"[module-test] cwd={cwd.relative_to(REPO_ROOT)} cmd={' '.join(cmd)}", flush=True)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
        timeout=180,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"latexmk failed (exit {result.returncode}) in {cwd.relative_to(REPO_ROOT)}\n"
            f"Command: {' '.join(cmd)}\n"
            f"Output:\n{result.stdout}"
        )
    return result


def ensure_markers(log_path: Path, markers: Iterable[str]) -> None:
    log_text = log_path.read_text(encoding="utf-8", errors="ignore")
    missing = [marker for marker in markers if marker not in log_text]
    if missing:
        raise AssertionError(
            f"Missing markers in {log_path.relative_to(REPO_ROOT)}: {missing}"
        )


def run_module_test(module: ModuleTest) -> Dict[str, str]:
    results = {}
    for mode, expectation in module.modes.items():
        env = os.environ.copy()
        env.setdefault("BUILD_MODE", mode)
        env.setdefault("OMNILATEX_SKIP_BIB2GLS", "1")

        # Thoroughly clean before each build to avoid reused logs.
        run_latexmk(LATEXMK_CLEAN, cwd=module.path, env=env)
        run_latexmk(LATEXMK, cwd=module.path, env=env)

        log_path = module.path / "main.log"
        if not log_path.exists():
            raise FileNotFoundError(
                f"Expected log not found: {log_path.relative_to(REPO_ROOT)}"
            )

        ensure_markers(log_path, expectation.markers)
        results[mode] = "ok"
    return results


def main() -> int:
    matrix_summary = {}
    for module in TEST_MATRIX:
        matrix_summary[module.name] = run_module_test(module)

    print(json.dumps(matrix_summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
