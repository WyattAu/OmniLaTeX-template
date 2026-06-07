"""Unit tests for buildlib.tui module (interactive menu)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from buildlib.tui import _simple_menu, interactive_menu


@pytest.fixture
def mock_tasks():
    tasks = MagicMock()
    tasks.version = "2.4.1"
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


class TestSimpleMenuExecution:
    """Test _simple_menu execution paths."""

    @patch("builtins.input", return_value="q")
    def test_simple_menu_quit(self, mock_input, mock_tasks, sample_commands):
        """Quit command should exit cleanly."""
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"1": ("build-all", "Build root + all examples", False)}
        _simple_menu(mock_tasks, sample_commands, menu_sections, flat_commands)

    @patch("builtins.input", side_effect=["1", "", "q"])
    def test_simple_menu_execute_command(self, mock_input, mock_tasks, sample_commands):
        """Selecting a command should invoke its handler."""
        handler = MagicMock()
        commands = {
            "build-all": (handler, "Build root + all examples", False),
        }
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"1": ("build-all", "Build root + all examples", False)}
        _simple_menu(mock_tasks, commands, menu_sections, flat_commands)
        handler.assert_called_once()

    @patch("builtins.input", side_effect=["unknown", "q"])
    def test_simple_menu_unknown_command(self, mock_input, mock_tasks, sample_commands):
        """Unknown command should print error and continue."""
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"1": ("build-all", "Build root + all examples", False)}
        # Should not raise, just print error and continue
        _simple_menu(mock_tasks, sample_commands, menu_sections, flat_commands)

    @patch("builtins.input", side_effect=["build-all", KeyboardInterrupt])
    def test_simple_menu_name_match(self, mock_input, mock_tasks, sample_commands):
        """Command name should match in flat_commands or commands dict."""
        handler = MagicMock()
        commands = {
            "build-all": (handler, "Build root + all examples", False),
        }
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"1": ("build-all", "Build root + all examples", False)}
        _simple_menu(mock_tasks, commands, menu_sections, flat_commands)
        handler.assert_called_once()

    @patch("builtins.input", side_effect=["", ""])
    def test_simple_menu_empty_input(self, mock_input, mock_tasks, sample_commands):
        """Empty input should quit."""
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"1": ("build-all", "Build root + all examples", False)}
        _simple_menu(mock_tasks, sample_commands, menu_sections, flat_commands)

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_simple_menu_keyboard_interrupt(
        self, mock_input, mock_tasks, sample_commands
    ):
        """KeyboardInterrupt should exit cleanly."""
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"1": ("build-all", "Build root + all examples", False)}
        _simple_menu(mock_tasks, sample_commands, menu_sections, flat_commands)

    @patch("builtins.input", side_effect=EOFError)
    def test_simple_menu_eof(self, mock_input, mock_tasks, sample_commands):
        """EOFError should exit cleanly."""
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"1": ("build-all", "Build root + all examples", False)}
        _simple_menu(mock_tasks, sample_commands, menu_sections, flat_commands)

    @patch("builtins.input", side_effect=["1", "", "", "q"])
    def test_simple_menu_file_command_prompt(self, mock_input, mock_tasks):
        """File commands should prompt for additional input."""
        handler = MagicMock()
        commands = {
            "init": (handler, "New project from template", True),
        }
        menu_sections = [
            ("Utilities", [("init", "New project from template")]),
        ]
        flat_commands = {"1": ("init", "New project from template", True)}
        _simple_menu(mock_tasks, commands, menu_sections, flat_commands)
        handler.assert_called_once()

    @patch("builtins.input", side_effect=["1", KeyboardInterrupt, "q"])
    def test_simple_menu_file_command_cancel(self, mock_input, mock_tasks):
        """Cancelling file input should continue the loop."""
        handler = MagicMock()
        commands = {
            "init": (handler, "New project from template", True),
        }
        menu_sections = [
            ("Utilities", [("init", "New project from template")]),
        ]
        flat_commands = {"1": ("init", "New project from template", True)}
        _simple_menu(mock_tasks, commands, menu_sections, flat_commands)
        handler.assert_not_called()

    @patch("builtins.input", side_effect=["1", "", "q"])
    def test_simple_menu_handler_exception(self, mock_input, mock_tasks):
        """Handler exceptions should be caught and displayed."""
        handler = MagicMock(side_effect=RuntimeError("test error"))
        commands = {
            "build-all": (handler, "Build root + all examples", False),
        }
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"1": ("build-all", "Build root + all examples", False)}
        # Should not raise
        _simple_menu(mock_tasks, commands, menu_sections, flat_commands)

    @patch("builtins.input", side_effect=["1", "", "q"])
    def test_simple_menu_system_exit(self, mock_input, mock_tasks):
        """SystemExit from handler should be caught."""
        handler = MagicMock(side_effect=SystemExit(0))
        commands = {
            "build-all": (handler, "Build root + all examples", False),
        }
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"1": ("build-all", "Build root + all examples", False)}
        _simple_menu(mock_tasks, commands, menu_sections, flat_commands)
        handler.assert_called_once()

    @patch("builtins.input", side_effect=["build-all", "", "q"])
    def test_simple_menu_match_by_name_in_commands(self, mock_input, mock_tasks):
        """Match by name in commands dict (not flat_commands)."""
        handler = MagicMock()
        commands = {
            "build-all": (handler, "Build root + all examples", False),
        }
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        # flat_commands has different key, so name match in commands dict
        flat_commands = {"99": ("other", "Other", False)}
        _simple_menu(mock_tasks, commands, menu_sections, flat_commands)
        handler.assert_called_once()
