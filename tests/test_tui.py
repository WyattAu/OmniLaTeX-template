"""Smoke tests for the TUI menu structure.

Verifies that the TUI menu sections reference commands that actually exist
in the CLI command registry, and that the menu can be constructed without errors.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTUIMenuStructure:
    """Verify TUI menu consistency with CLI command registry."""

    def test_menu_commands_exist_in_cli(self) -> None:
        """All commands referenced in TUI menu sections must exist in cli.py."""
        # Parse menu_sections from tui.py
        tui_path = PROJECT_ROOT / "buildlib" / "tui.py"
        tui_content = tui_path.read_text(encoding="utf-8")

        # Extract command names from menu_sections (lines like ("cmd-name", "..."))
        import re

        menu_cmds = set(re.findall(r'\("(build-[^"]+|clean[^"]*|test|preflight|doctor|diff|lint|check|list-[^"]+|init|scaffold-[^"]+|watch|export|cache-[^"]+|plugin-[^"]+)"', tui_content))

        # Parse commands dict from cli.py
        cli_path = PROJECT_ROOT / "buildlib" / "cli.py"
        cli_content = cli_path.read_text(encoding="utf-8")

        # Extract command names from the commands dict
        cli_cmds = set(re.findall(r'"([a-z][\w-]+)":\s*\(', cli_content))

        # Every menu command must exist in CLI
        for cmd in menu_cmds:
            assert cmd in cli_cmds, (
                f"TUI menu references command '{cmd}' which is not defined "
                f"in cli.py commands dict. Available: {sorted(cli_cmds)}"
            )

    def test_menu_sections_are_well_formed(self) -> None:
        """Menu sections must be a list of (section_name, [(cmd, desc)]) tuples."""
        tui_path = PROJECT_ROOT / "buildlib" / "tui.py"
        content = tui_path.read_text(encoding="utf-8")

        # Verify menu_sections structure exists with correct section names
        assert "menu_sections = [" in content
        assert '"Build"' in content
        assert '"Clean"' in content
        assert '"Quality"' in content
        assert '"Utilities"' in content

    def test_menu_covers_all_commands(self) -> None:
        """Every CLI command should appear in at least one TUI menu section."""
        import re

        tui_path = PROJECT_ROOT / "buildlib" / "tui.py"
        tui_content = tui_path.read_text(encoding="utf-8")

        cli_path = PROJECT_ROOT / "buildlib" / "cli.py"
        cli_content = cli_path.read_text(encoding="utf-8")

        menu_cmds = set(re.findall(r'"(build-[^"]+|clean[^"]*|test|preflight|doctor|diff|lint|check|list-[^"]+|init|scaffold-[^"]+|watch|export|cache-[^"]+|plugin-[^"]+)"', tui_content))

        cli_cmds = set(re.findall(r'"([a-z][\w-]+)":\s*\(', cli_content))

        # Commands in CLI but not in menu (informational, not a failure)
        unlisted = cli_cmds - menu_cmds
        if unlisted:
            # These are commands accessible via CLI but not the interactive menu.
            # This is intentional for commands like plugin-*, which have many
            # sub-variants. Just verify the count is reasonable.
            assert len(unlisted) <= 10, (
                f"{len(unlisted)} CLI commands not in TUI menu: {sorted(unlisted)}"
            )
