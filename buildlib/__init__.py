"""OmniLaTeX build system package.

Composes mixin classes into the final BuildTasks class.
"""

from __future__ import annotations

# Re-export public API for convenience
from buildlib.cli import main  # noqa: F401, E402
from buildlib.config import (BUILD_EXAMPLES_SUBDIR,  # noqa: F401, E402
                             FORCE_REBUILD_FLAG, INTERACTION_NONSTOP,
                             LATEXMK_COMMAND, MAIN_TEX_FILENAME,
                             MINTED_CACHE_SUBDIR, RICH_AVAILABLE,
                             SVG_INKSCAPE_CACHE, ProjectConfig)
from buildlib.runner import CommandRunner  # noqa: F401, E402
from buildlib.tasks import BuildTasks  # noqa: F401
from buildlib.ui import TerminalOutput  # noqa: F401, E402
