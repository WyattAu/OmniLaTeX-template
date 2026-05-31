"""Constants and configuration for the OmniLaTeX build system."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
MAIN_TEX_FILENAME = "main.tex"
LATEXMK_COMMAND = "latexmk"
INTERACTION_NONSTOP = "-interaction=nonstopmode"
FORCE_REBUILD_FLAG = "-g"
# Force latexmk to continue processing despite intermediate-pass errors.
# Without this, latexmk stops on first-pass undefined refs/missing TOC errors,
# preventing subsequent passes that would resolve them.
LATEXMK_FORCE_CONTINUE = "-f"
MINTED_CACHE_SUBDIR = "_minted"
SVG_INKSCAPE_CACHE = "svg-inkscape"
BUILD_EXAMPLES_SUBDIR = "examples"

# Repository root directory (two levels up from this file: buildlib/ -> repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class ProjectConfig:
    build_dir: Path = Path("build")
    cnf_lines: list[str] = None

    def is_ci(self) -> bool:
        return any(os.environ.get(var) for var in ["CI", "GITHUB_ACTIONS", "GITLAB_CI"])

    def verbose_enabled(self) -> bool:
        return os.environ.get("OMNILATEX_VERBOSE", "0").lower() in {"1", "true", "yes"}
