"""OmniLaTeX build system package.

Composes mixin classes into the final BuildTasks class.
"""

from __future__ import annotations

from buildlib.builder import _BuildCore  # noqa: F401
from buildlib.commands import _Commands  # noqa: F401


class BuildTasks(_BuildCore, _Commands):
    """Combined build tasks with core build logic and CLI commands."""

    pass


# Re-export public API for convenience
from buildlib.cli import main  # noqa: F401, E402
from buildlib.config import (  # noqa: F401, E402
    BUILD_EXAMPLES_SUBDIR,
    FORCE_REBUILD_FLAG,
    INTERACTION_NONSTOP,
    LATEXMK_COMMAND,
    MAIN_TEX_FILENAME,
    MINTED_CACHE_SUBDIR,
    SVG_INKSCAPE_CACHE,
    ProjectConfig,
)
from buildlib.runner import CommandRunner  # noqa: F401, E402
from buildlib.ui import TerminalOutput  # noqa: F401, E402
