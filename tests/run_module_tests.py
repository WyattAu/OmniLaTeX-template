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

REPO_ROOT = Path(__file__).resolve().parent.parent
MODULE_TESTS_ROOT = REPO_ROOT / "tests" / "module_tests"
ROOT_LATEXMKRC = REPO_ROOT / ".latexmkrc"

LATEXMK = [
    "latexmk",
    "-pdf",
    "-r",
    str(ROOT_LATEXMKRC),
    "main.tex",
]
LATEXMK_CLEAN = [
    "latexmk",
    "-C",
    "-r",
    str(ROOT_LATEXMKRC),
    "main.tex",
]


@dataclass
class ModeExpectation:
    markers: list[str]


@dataclass
class ModuleTest:
    name: str
    path: Path
    modes: dict[str, ModeExpectation]


TEST_MATRIX: list[ModuleTest] = [
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
        },
    ),
    ModuleTest(
        name="code-listings",
        path=MODULE_TESTS_ROOT / "code-listings",
        modes={
            "dev": ModeExpectation(markers=["MINTED:LOADED"]),
        },
    ),
    ModuleTest(
        name="graphics",
        path=MODULE_TESTS_ROOT / "graphics",
        modes={
            "dev": ModeExpectation(markers=["SVG_TEST:BEGIN"]),
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
        name="layout",
        path=MODULE_TESTS_ROOT / "layout",
        modes={
            "dev": ModeExpectation(
                markers=[
                    "LAYOUT:PAGE_LOADED",
                    "LAYOUT:FLOATS_LOADED",
                    "LAYOUT:BOXES_LOADED",
                ]
            ),
        },
    ),
    ModuleTest(
        name="typography",
        path=MODULE_TESTS_ROOT / "typography",
        modes={
            "dev": ModeExpectation(
                markers=[
                    "TYPO:MATH_LOADED",
                    "TYPO:DELIMITERS_WORK",
                ]
            ),
        },
    ),
    ModuleTest(
        name="references",
        path=MODULE_TESTS_ROOT / "references",
        modes={
            "dev": ModeExpectation(
                markers=[
                    "REFS:HYPERREF_LOADED",
                    "REFS:CREF_WORKS",
                ]
            ),
        },
    ),
    ModuleTest(
        name="language",
        path=MODULE_TESTS_ROOT / "language",
        modes={
            "dev": ModeExpectation(
                markers=[
                    "LANG:I18N_LOADED",
                    "LANG:TRANSLATION_WORKS",
                ]
            ),
        },
    ),
    ModuleTest(
        name="tables",
        path=MODULE_TESTS_ROOT / "tables",
        modes={
            "dev": ModeExpectation(
                markers=[
                    "TABLES:LOADED",
                    "TABLES:BOOKTABS_WORKS",
                ]
            ),
        },
    ),
]


def run_latexmk(
    cmd: list[str], cwd: Path, env: dict[str, str]
) -> subprocess.CompletedProcess:
    """Run latexmk and raise a rich error if it fails."""
    print(
        f"[module-test] cwd={cwd.relative_to(REPO_ROOT)} cmd={' '.join(cmd)}",
        flush=True,
    )
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


def ensure_markers(log_path: Path, markers: list[str]) -> None:
    log_text = log_path.read_text(encoding="utf-8", errors="ignore")
    missing = [marker for marker in markers if marker not in log_text]
    if missing:
        raise AssertionError(
            f"Missing markers in {log_path.relative_to(REPO_ROOT)}: {missing}"
        )


def run_module_test(module: ModuleTest) -> dict[str, str]:
    results = {}
    for mode, expectation in module.modes.items():
        env = os.environ.copy()
        # Always use 'dev' BUILD_MODE to avoid ultra-mode's max_repeat=1,
        # which prevents latexmk from completing multi-pass compilations.
        # The 'mode' field in TEST_MATRIX selects which markers to check,
        # not the actual build mode.
        env["BUILD_MODE"] = "dev"
        env["OMNILATEX_SKIP_BIB2GLS"] = "1"
        # Add repo root and key subdirs to TEXINPUTS so lib/ modules are findable.
        # Use trailing colon to include default search paths.
        # The CWD (module test directory) comes first implicitly via kpathsea,
        # but we explicitly add it to be safe.
        texinputs = env.get("TEXINPUTS", "")
        repo_entry = str(REPO_ROOT)
        if repo_entry not in texinputs.split(os.pathsep):
            # Add lib/, config/, lua/, and root (for .latexmkrc, omnilatex.cls)
            extra = os.pathsep.join(
                [
                    str(module.path),  # module test dir first
                    str(REPO_ROOT / "lib"),
                    str(REPO_ROOT / "config"),
                    str(REPO_ROOT / "lua"),
                    str(REPO_ROOT),
                ]
            )
            env["TEXINPUTS"] = extra + os.pathsep + texinputs

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
