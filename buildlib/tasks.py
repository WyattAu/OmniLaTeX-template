"""BuildTasks composition - combines core build logic with CLI commands."""

from __future__ import annotations

from buildlib.builder import _BuildCore
from buildlib.commands import _Commands


class BuildTasks(_BuildCore, _Commands):
    """Combined build tasks with core build logic and CLI commands."""

    pass
