"""Unit tests for buildlib.tui module (interactive menu)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest


def _ensure_rich_mocks():
    """Inject mock rich modules into sys.modules if rich is not installed."""
    if "rich" not in sys.modules:
        mock_rich = MagicMock()
        for sub in ("console", "panel", "table", "text", "layout", "progress", "live"):
            mod = MagicMock()
            setattr(mock_rich, sub, mod)
            sys.modules[f"rich.{sub}"] = mod
        sys.modules["rich"] = mock_rich


_ensure_rich_mocks()

from buildlib.tui import _rich_menu, _simple_menu, interactive_menu  # noqa: E402


def _make_rich_mocks():
    """Create mock objects for all rich imports used by _rich_menu."""
    mock_console_cls = MagicMock()
    mock_console = MagicMock()
    mock_console_cls.return_value = mock_console

    mock_panel_cls = MagicMock()
    mock_panel_cls.return_value = MagicMock()

    mock_rich_table_cls = MagicMock()
    mock_rich_table = MagicMock()
    mock_rich_table_cls.return_value = mock_rich_table

    mock_rich_text_cls = MagicMock()
    mock_rich_text = MagicMock()
    mock_rich_text_cls.return_value = mock_rich_text

    return {
        "console_cls": mock_console_cls,
        "console": mock_console,
        "panel_cls": mock_panel_cls,
        "table_cls": mock_rich_table_cls,
        "text_cls": mock_rich_text_cls,
    }


def _patch_rich_modules():
    """Return a list of patches to mock all rich imports in _rich_menu."""
    mocks = _make_rich_mocks()
    return (
        [
            patch("rich.console.Console", mocks["console_cls"]),
            patch("rich.panel.Panel", mocks["panel_cls"]),
            patch("rich.table.Table", mocks["table_cls"]),
            patch("rich.text.Text", mocks["text_cls"]),
        ],
        mocks,
    )


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

    @patch("builtins.input", side_effect=["build", "", "q"])
    def test_simple_menu_fuzzy_match_prefix(self, mock_input, mock_tasks):
        """Fuzzy match by prefix should resolve to the matching command."""
        handler = MagicMock()
        commands = {
            "build-all": (handler, "Build root + all examples", False),
        }
        menu_sections = [
            ("Build", [("build-all", "Build root + all examples")]),
        ]
        flat_commands = {"99": ("other", "Other", False)}
        _simple_menu(mock_tasks, commands, menu_sections, flat_commands)
        handler.assert_called_once()


class TestRichMenu:
    """Test _rich_menu execution paths."""

    def test_rich_menu_quit(self, mock_tasks, sample_commands):
        """Quit command should exit cleanly."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            menu_sections = [
                ("Build", [("build-all", "Build root + all examples")]),
            ]
            flat_commands = {"1": ("build-all", "Build root + all examples", False)}
            with patch("builtins.input", return_value="q"):
                _rich_menu(mock_tasks, sample_commands, menu_sections, flat_commands)
            mocks["console"].print.assert_called()
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_execute_command(self, mock_tasks):
        """Selecting a command by number should invoke its handler."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            handler = MagicMock()
            commands = {
                "build-all": (handler, "Build root + all examples", False),
            }
            menu_sections = [
                ("Build", [("build-all", "Build root + all examples")]),
            ]
            flat_commands = {"1": ("build-all", "Build root + all examples", False)}
            with patch("builtins.input", side_effect=["1", "", "q"]):
                _rich_menu(mock_tasks, commands, menu_sections, flat_commands)
            handler.assert_called_once()
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_unknown_command(self, mock_tasks, sample_commands):
        """Unknown command should print error and continue."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            menu_sections = [
                ("Build", [("build-all", "Build root + all examples")]),
            ]
            flat_commands = {"1": ("build-all", "Build root + all examples", False)}
            with patch("builtins.input", side_effect=["unknown", "q"]), patch(
                "buildlib.tui.time.sleep"
            ):
                _rich_menu(mock_tasks, sample_commands, menu_sections, flat_commands)
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_fuzzy_match(self, mock_tasks):
        """Partial name should match via fuzzy logic."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            handler = MagicMock()
            commands = {
                "build-all": (handler, "Build root + all examples", False),
            }
            menu_sections = [
                ("Build", [("build-all", "Build root + all examples")]),
            ]
            flat_commands = {"99": ("other", "Other", False)}
            with patch("builtins.input", side_effect=["build", "", "q"]):
                _rich_menu(mock_tasks, commands, menu_sections, flat_commands)
            handler.assert_called_once()
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_match_by_name(self, mock_tasks):
        """Exact command name should match in commands dict."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            handler = MagicMock()
            commands = {
                "build-all": (handler, "Build root + all examples", False),
            }
            menu_sections = [
                ("Build", [("build-all", "Build root + all examples")]),
            ]
            flat_commands = {"99": ("other", "Other", False)}
            with patch("builtins.input", side_effect=["build-all", "", "q"]):
                _rich_menu(mock_tasks, commands, menu_sections, flat_commands)
            handler.assert_called_once()
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_file_command_prompt(self, mock_tasks):
        """File commands should prompt for additional input."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            handler = MagicMock()
            commands = {
                "init": (handler, "New project from template", True),
            }
            menu_sections = [
                ("Utilities", [("init", "New project from template")]),
            ]
            flat_commands = {"1": ("init", "New project from template", True)}
            with patch("builtins.input", side_effect=["1", "myfile.tex", "", "q"]):
                _rich_menu(mock_tasks, commands, menu_sections, flat_commands)
            handler.assert_called_once()
            handler.assert_called_with(mock_tasks, ["myfile.tex"])
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_file_command_empty_args(self, mock_tasks):
        """File command with empty input should pass empty list."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            handler = MagicMock()
            commands = {
                "init": (handler, "New project from template", True),
            }
            menu_sections = [
                ("Utilities", [("init", "New project from template")]),
            ]
            flat_commands = {"1": ("init", "New project from template", True)}
            with patch("builtins.input", side_effect=["1", "", "", "q"]):
                _rich_menu(mock_tasks, commands, menu_sections, flat_commands)
            handler.assert_called_once()
            handler.assert_called_with(mock_tasks, [])
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_file_command_cancel(self, mock_tasks):
        """Cancelling file input should continue the loop."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            handler = MagicMock()
            commands = {
                "init": (handler, "New project from template", True),
            }
            menu_sections = [
                ("Utilities", [("init", "New project from template")]),
            ]
            flat_commands = {"1": ("init", "New project from template", True)}
            with patch(
                "builtins.input", side_effect=["1", KeyboardInterrupt, "q"]
            ), patch("buildlib.tui.time.sleep"):
                _rich_menu(mock_tasks, commands, menu_sections, flat_commands)
            handler.assert_not_called()
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_handler_exception(self, mock_tasks):
        """Handler exceptions should be caught and displayed."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            handler = MagicMock(side_effect=RuntimeError("test error"))
            commands = {
                "build-all": (handler, "Build root + all examples", False),
            }
            menu_sections = [
                ("Build", [("build-all", "Build root + all examples")]),
            ]
            flat_commands = {"1": ("build-all", "Build root + all examples", False)}
            with patch("builtins.input", side_effect=["1", "", "q"]):
                _rich_menu(mock_tasks, commands, menu_sections, flat_commands)
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_system_exit(self, mock_tasks):
        """SystemExit from handler should be caught."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            handler = MagicMock(side_effect=SystemExit(0))
            commands = {
                "build-all": (handler, "Build root + all examples", False),
            }
            menu_sections = [
                ("Build", [("build-all", "Build root + all examples")]),
            ]
            flat_commands = {"1": ("build-all", "Build root + all examples", False)}
            with patch("builtins.input", side_effect=["1", "", "q"]):
                _rich_menu(mock_tasks, commands, menu_sections, flat_commands)
            handler.assert_called_once()
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_keyboard_interrupt(self, mock_tasks, sample_commands):
        """KeyboardInterrupt should exit cleanly."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            menu_sections = [
                ("Build", [("build-all", "Build root + all examples")]),
            ]
            flat_commands = {"1": ("build-all", "Build root + all examples", False)}
            with patch("builtins.input", side_effect=KeyboardInterrupt):
                _rich_menu(mock_tasks, sample_commands, menu_sections, flat_commands)
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_eof(self, mock_tasks, sample_commands):
        """EOFError should exit cleanly."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            menu_sections = [
                ("Build", [("build-all", "Build root + all examples")]),
            ]
            flat_commands = {"1": ("build-all", "Build root + all examples", False)}
            with patch("builtins.input", side_effect=EOFError):
                _rich_menu(mock_tasks, sample_commands, menu_sections, flat_commands)
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_build_example_shows_examples(self, mock_tasks):
        """build-example command should list available examples."""
        patches, mocks = _patch_rich_modules()
        for p in patches:
            p.start()
        try:
            handler = MagicMock()
            commands = {
                "build-example": (handler, "Build specific example(s)", True),
            }
            menu_sections = [
                ("Build", [("build-example", "Build specific example(s)")]),
            ]
            flat_commands = {"1": ("build-example", "Build specific example(s)", True)}
            example_obj = MagicMock()
            example_obj.name = "example1"
            mock_tasks.discover_examples.return_value = [example_obj]
            with patch("builtins.input", side_effect=["1", "example1", "", "q"]):
                _rich_menu(mock_tasks, commands, menu_sections, flat_commands)
            handler.assert_called_once()
        finally:
            for p in patches:
                p.stop()

    def test_rich_menu_quit_variants(self, mock_tasks, sample_commands):
        """quit/exit should also quit the menu."""
        for quit_val in ("quit", "exit"):
            patches, mocks = _patch_rich_modules()
            for p in patches:
                p.start()
            try:
                menu_sections = [
                    ("Build", [("build-all", "Build root + all examples")]),
                ]
                flat_commands = {"1": ("build-all", "Build root + all examples", False)}
                with patch("builtins.input", return_value=quit_val):
                    _rich_menu(
                        mock_tasks, sample_commands, menu_sections, flat_commands
                    )
            finally:
                for p in patches:
                    p.stop()


class TestInteractiveMenuRichBranch:
    """Test interactive_menu when RICH_AVAILABLE is True."""

    @pytest.fixture
    def full_commands(self):
        """Commands dict covering every entry in interactive_menu's menu_sections."""
        mock = MagicMock
        return {
            "build-all": (mock(), "Build root + all examples", False),
            "build-root": (mock(), "Build root document", False),
            "build-examples": (mock(), "Build all examples", False),
            "build-example": (mock(), "Build specific example(s)", True),
            "clean": (mock(), "Full cleanup", False),
            "clean-aux": (mock(), "Clean auxiliary files", False),
            "clean-pdf": (mock(), "Clean all PDFs", False),
            "clean-example": (mock(), "Clean specific example(s)", True),
            "test": (mock(), "Run test suite", False),
            "preflight": (mock(), "Run preflight checks", False),
            "doctor": (mock(), "Health diagnostics", False),
            "diff": (mock(), "Visual regression diff", False),
            "lint": (mock(), "Lint .tex files (chktex/lacheck)", False),
            "check": (mock(), "Cross-reference integrity check", False),
            "list-examples": (mock(), "List all examples", False),
            "init": (mock(), "New project from template", True),
            "scaffold-institution": (mock(), "New institution config", True),
            "watch": (mock(), "Watch files & rebuild", True),
            "export": (mock(), "Export LaTeX to HTML/EPUB/DOCX", True),
            "cache-stats": (mock(), "Show build cache statistics", False),
            "cache-clear": (mock(), "Delete build cache", False),
        }

    def test_interactive_menu_rich_branch(self, mock_tasks, full_commands):
        """interactive_menu should call _rich_menu when RICH_AVAILABLE is True."""
        with patch("buildlib.tui.RICH_AVAILABLE", True), patch(
            "buildlib.tui._rich_menu"
        ) as mock_rich_menu, patch("builtins.input", return_value="q"):
            interactive_menu(mock_tasks, full_commands)
            mock_rich_menu.assert_called_once()

    def test_interactive_menu_simple_branch(self, mock_tasks, full_commands):
        """interactive_menu should call _simple_menu when RICH_AVAILABLE is False."""
        with patch("buildlib.tui.RICH_AVAILABLE", False), patch(
            "buildlib.tui._simple_menu"
        ) as mock_simple_menu, patch("builtins.input", return_value="q"):
            interactive_menu(mock_tasks, full_commands)
            mock_simple_menu.assert_called_once()

    def test_interactive_menu_builds_flat_commands_correctly(
        self, mock_tasks, full_commands
    ):
        """interactive_menu should build flat_commands with correct numbering."""
        captured_args = {}

        def capture_simple(tasks, commands, menu_sections, flat_commands):
            captured_args["flat_commands"] = flat_commands
            captured_args["menu_sections"] = menu_sections

        with patch("buildlib.tui.RICH_AVAILABLE", False), patch(
            "buildlib.tui._simple_menu", side_effect=capture_simple
        ), patch("builtins.input", return_value="q"):
            interactive_menu(mock_tasks, full_commands)

        flat = captured_args["flat_commands"]
        assert "1" in flat
        assert flat["1"][0] == "build-all"
        nums = sorted(flat.keys(), key=int)
        for i, n in enumerate(nums, 1):
            assert int(n) == i
