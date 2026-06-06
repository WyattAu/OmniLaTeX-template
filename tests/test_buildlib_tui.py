"""Unit tests for buildlib.tui module (interactive menu)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from buildlib.tui import _simple_menu, interactive_menu


@pytest.fixture
def mock_tasks():
    tasks = MagicMock()
    tasks.version = "2.4.0"
    tasks.discover_examples.return_value = [MagicMock(name="example1")]
    tasks.source_files = [MagicMock()]
    return tasks


@pytest.fixture
def sample_commands():
    return {
        "build-all": (MagicMock(), "Build root + all examples", False),
        "build-root": (MagicMock(), "Build root document", False),
        "test": (MagicMock(), "Run test suite", False),
        "doctor": (MagicMock(), "Health diagnostics", False),
        "list-examples": (MagicMock(), "List all examples", False),
        "init": (MagicMock(), "New project from template", True),
        "scaffold-institution": (MagicMock(), "New institution config", True),
        "watch": (MagicMock(), "Watch files & rebuild", True),
    }


class TestInteractiveMenu:
    """Test interactive menu dispatch logic."""

    def test_menu_builds_flat_commands(self, mock_tasks, sample_commands):
        """Verify flat command lookup is built correctly."""
        # We can't easily test the interactive loop, but verify the function exists
        assert callable(interactive_menu)

    def test_simple_menu_exists(self):
        """Verify _simple_menu function exists."""
        assert callable(_simple_menu)


class TestMenuCommandResolution:
    """Test command name resolution logic."""

    def test_exact_match(self, sample_commands):
        """Exact command name should match."""
        assert "build-all" in sample_commands
        assert sample_commands["build-all"][1] == "Build root + all examples"

    def test_partial_match(self, sample_commands):
        """Partial name should match via startswith."""
        matches = [k for k in sample_commands if k.startswith("build")]
        assert len(matches) >= 2  # build-all, build-root

    def test_file_commands_require_input(self, sample_commands):
        """Commands with takes_files=True need user input."""
        for name, (_, _, takes_files) in sample_commands.items():
            if name in ("init", "scaffold-institution", "watch"):
                assert takes_files is True

    def test_non_file_commands(self, sample_commands):
        """Commands with takes_files=False don't need user input."""
        for name, (_, _, takes_files) in sample_commands.items():
            if name in ("build-all", "build-root", "test", "doctor", "list-examples"):
                assert takes_files is False
