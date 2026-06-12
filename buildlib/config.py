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

# --- Rich library availability ---
try:
    import rich  # noqa: F401

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class ProjectConfig:
    """Build system configuration.

    Attributes:
        build_dir: Output directory for built artifacts.
        cnf_lines: Optional TeX CNF lines to pass via environment.
    """

    build_dir: Path = Path("build")
    cnf_lines: list[str] | None = None

    def is_ci(self) -> bool:
        """Return True if running in a CI environment."""
        return any(os.environ.get(var) for var in ["CI", "GITHUB_ACTIONS", "GITLAB_CI"])

    def verbose_enabled(self) -> bool:
        """Return True if verbose logging is enabled via environment."""
        return os.environ.get("OMNILATEX_VERBOSE", "0").lower() in {"1", "true", "yes"}


def base_build_env() -> dict[str, str]:
    """Return the base environment variables for any LaTeX build.

    Both builder.py and profiler.py need TEXINPUTS and LC_ALL.  This function
    is the single source of truth for these values, avoiding duplication.
    """
    return {
        "TEXINPUTS": os.pathsep.join([".", str(REPO_ROOT), ""]),
        "LC_ALL": "C.utf8",
    }


def build_latexmk_command(
    force_rebuild: bool = False,
    include_root_rc: bool = False,
    root_rc_path: Path | None = None,
    extra_flags: list[str] | None = None,
) -> list[str]:
    """Construct the standard latexmk invocation command.

    Returns a list of command-line arguments for invoking latexmk with OmniLaTeX
    defaults (nonstopmode, force-continue). This is the single source of truth
    for build command construction, used by both builder.py and profiler.py.

    Args:
        force_rebuild: Append the force-rebuild flag (-g).
        include_root_rc: Include the root .latexmkrc via -r flag.
        root_rc_path: Explicit path to .latexmkrc (overrides include_root_rc).
        extra_flags: Additional flags to append (e.g. ['-interaction=scrollmode']).
    """
    cmd = [LATEXMK_COMMAND, INTERACTION_NONSTOP, LATEXMK_FORCE_CONTINUE]
    if force_rebuild:
        cmd.append(FORCE_REBUILD_FLAG)

    if include_root_rc and root_rc_path is not None:
        cmd.extend(["-r", str(root_rc_path)])
    elif include_root_rc:
        _root_rc = REPO_ROOT / ".latexmkrc"
        if _root_rc.exists():
            cmd.extend(["-r", str(_root_rc)])

    if extra_flags:
        cmd.extend(extra_flags)

    cmd.append(MAIN_TEX_FILENAME)
    return cmd
