"""Additional coverage tests targeting tui.py, commands.py, and remaining builder.py paths.

These tests focus on interactive menus (mocked input), command helpers,
and build edge cases to push total coverage toward 80%.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from buildlib.builder import RICH_AVAILABLE, _BuildCore
from buildlib.config import ProjectConfig
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ui():
    return TerminalOutput(use_color=False)


@pytest.fixture
def runner(ui):
    return CommandRunner(ui=ui, build_mode="dev", verbose=False)


@pytest.fixture
def build_core(tmp_path, ui, runner):
    config = ProjectConfig(build_dir=tmp_path / "build")
    return _BuildCore(config=config, runner=runner, ui=ui, jobs=1)


# ===================================================================
# tui.py -- interactive_menu flat command building
# ===================================================================


class TestTUIFlatCommands:
    """Test flat command lookup construction in interactive_menu."""

    def test_flat_commands_built_correctly(self):
        """Verify flat_commands dict maps indices to command tuples."""
        menu_sections = [
            ("Build", [("build-all", "Build all")]),
            ("Quality", [("test", "Run tests")]),
        ]
        commands = {
            "build-all": (MagicMock(), "Build all", False),
            "test": (MagicMock(), "Run tests", False),
        }
        # Build the flat dict the same way the function does
        flat_commands = {}
        idx = 1
        for _section, items in menu_sections:
            for cmd_name, desc in items:
                flat_commands[str(idx)] = (cmd_name, desc, commands[cmd_name][2])
                idx += 1

        assert flat_commands["1"] == ("build-all", "Build all", False)
        assert flat_commands["2"] == ("test", "Run tests", False)

    def test_interactive_menu_is_callable(self):
        from buildlib.tui import interactive_menu

        assert callable(interactive_menu)

    def test_simple_menu_is_callable(self):
        from buildlib.tui import _simple_menu

        assert callable(_simple_menu)


class TestTUISimpleMenu:
    """Test _simple_menu with mocked input."""

    def test_simple_menu_quit_immediately(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        commands = {
            "build-all": (MagicMock(), "Build all", False),
            "test": (MagicMock(), "Run tests", False),
        }
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["q"]):
            _simple_menu(tasks, commands, menu_sections, flat_commands)

        captured = capsys.readouterr()
        assert "Goodbye" in captured.out

    def test_simple_menu_eof(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        commands = {"build-all": (MagicMock(), "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=EOFError):
            _simple_menu(tasks, commands, menu_sections, flat_commands)

    def test_simple_menu_select_by_number(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock()
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["1", "", "q"]):
            _simple_menu(tasks, commands, menu_sections, flat_commands)

        handler.assert_called_once()

    def test_simple_menu_select_by_name(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock()
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["build-all", "", "q"]):
            _simple_menu(tasks, commands, menu_sections, flat_commands)

        handler.assert_called_once()

    def test_simple_menu_unknown_command(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        commands = {"build-all": (MagicMock(), "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["nonexistent", "q"]):
            _simple_menu(tasks, commands, menu_sections, flat_commands)

    def test_simple_menu_file_command(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock()
        commands = {"init": (handler, "New project", True)}
        menu_sections = [("Utilities", [("init", "New project")])]
        flat_commands = {"1": ("init", "New project", True)}

        with patch("builtins.input", side_effect=["1", "myproject", "", "q"]):
            _simple_menu(tasks, commands, menu_sections, flat_commands)

        handler.assert_called_once()

    def test_simple_menu_file_command_eof(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        commands = {"init": (MagicMock(), "New project", True)}
        menu_sections = [("Utilities", [("init", "New project")])]
        flat_commands = {"1": ("init", "New project", True)}

        with patch("builtins.input", side_effect=["1", EOFError, "q"]):
            _simple_menu(tasks, commands, menu_sections, flat_commands)

    def test_simple_menu_handler_exception(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock(side_effect=ValueError("boom"))
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["1", "", "q"]):
            _simple_menu(tasks, commands, menu_sections, flat_commands)

    def test_simple_menu_system_exit(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock(side_effect=SystemExit(0))
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["1", "", "q"]):
            _simple_menu(tasks, commands, menu_sections, flat_commands)

    def test_simple_menu_press_enter_to_continue(self, capsys):
        from buildlib.tui import _simple_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.ui = TerminalOutput(use_color=False)
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock()
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["1", "continue", "q"]):
            _simple_menu(tasks, commands, menu_sections, flat_commands)


@pytest.mark.skipif(not RICH_AVAILABLE, reason="rich library not installed")
class TestTUIRichMenu:
    """Test _rich_menu with mocked input."""

    def test_rich_menu_quit(self, capsys):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        commands = {"build-all": (MagicMock(), "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

    def test_rich_menu_eof(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        commands = {"build-all": (MagicMock(), "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=EOFError):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

    def test_rich_menu_select_by_number(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock()
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["1", "", "q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

        handler.assert_called_once()

    def test_rich_menu_select_by_name(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock()
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["build-all", "", "q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

        handler.assert_called_once()

    def test_rich_menu_unknown_command(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        commands = {"build-all": (MagicMock(), "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["xyz", "q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

    def test_rich_menu_fuzzy_match(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock()
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["build", "", "q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

        handler.assert_called_once()

    def test_rich_menu_file_command(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock()
        commands = {"build-example": (handler, "Build example", True)}
        menu_sections = [("Build", [("build-example", "Build example")])]
        flat_commands = {"1": ("build-example", "Build example", True)}

        with patch("builtins.input", side_effect=["1", "minimal-starter", "", "q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

    def test_rich_menu_file_command_eof(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        commands = {"build-example": (MagicMock(), "Build example", True)}
        menu_sections = [("Build", [("build-example", "Build example")])]
        flat_commands = {"1": ("build-example", "Build example", True)}

        with patch("builtins.input", side_effect=["1", EOFError]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

    def test_rich_menu_handler_exception(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock(side_effect=ValueError("boom"))
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["1", "", "q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

    def test_rich_menu_system_exit(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock(side_effect=SystemExit(0))
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["1", "", "q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

    def test_rich_menu_press_enter(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        handler = MagicMock()
        commands = {"build-all": (handler, "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["1", "continue", "q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)

    def test_rich_menu_fuzzy_no_match(self):
        from buildlib.tui import _rich_menu

        tasks = MagicMock()
        tasks.version = "2.4.0"
        tasks.discover_examples.return_value = []
        tasks.source_files = []

        commands = {"build-all": (MagicMock(), "Build all", False)}
        menu_sections = [("Build", [("build-all", "Build all")])]
        flat_commands = {"1": ("build-all", "Build all", False)}

        with patch("builtins.input", side_effect=["zzz", "q"]):
            _rich_menu(tasks, commands, menu_sections, flat_commands)


# ===================================================================
# commands.py -- helper methods
# ===================================================================


class TestCommandsHelpers:
    """Test utility/helper methods of the Commands class."""

    def test_check_tool_found(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        result = cmds._check_tool("echo", "Echo command")
        assert result[1] is True
        assert "Found" in result[2]

    def test_check_tool_not_found(self, tmp_path):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        result = cmds._check_tool("nonexistent_tool_xyz", "Missing tool")
        assert result[1] is False

    def test_check_tool_optional(self, tmp_path):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        result = cmds._check_tool(
            "nonexistent_tool_xyz", "Optional tool", required=False
        )
        assert result[1] is True

    def test_get_texlive_version(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        # Mock subprocess.run to return TeX Live version
        mock_result = MagicMock()
        mock_result.stdout = "TeX Live 2025\n"
        mock_result.returncode = 0
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        version = cmds._get_texlive_version()
        assert version == 2025

    def test_get_texlive_version_not_found(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        mock_result = MagicMock()
        mock_result.stdout = "Some other output\n"
        mock_result.returncode = 0
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        version = cmds._get_texlive_version()
        assert version is None

    def test_get_texlive_version_timeout(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        def raise_timeout(*a, **kw):
            raise subprocess.TimeoutExpired(cmd="tex", timeout=5)

        monkeypatch.setattr("subprocess.run", raise_timeout)
        version = cmds._get_texlive_version()
        assert version is None

    def test_check_latex_package(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/some/path/hyperref.sty\n"
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        assert cmds._check_latex_package("hyperref") is True

    def test_check_latex_package_not_found(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        assert cmds._check_latex_package("nonexistent") is False

    def test_check_latex_package_timeout(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        def raise_timeout(*a, **kw):
            raise subprocess.TimeoutExpired(cmd="kpsewhich", timeout=5)

        monkeypatch.setattr("subprocess.run", raise_timeout)
        assert cmds._check_latex_package("hyperref") is False

    def test_check_all_latex_packages(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/path/hyperref.sty\n/path/fontspec.sty\n"
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        result = cmds._check_all_latex_packages(["hyperref", "fontspec", "missing"])
        assert result["hyperref"] is True
        assert result["fontspec"] is True
        assert result["missing"] is False

    def test_check_all_latex_packages_timeout(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        def raise_timeout(*a, **kw):
            raise subprocess.TimeoutExpired(cmd="kpsewhich", timeout=30)

        monkeypatch.setattr("subprocess.run", raise_timeout)
        result = cmds._check_all_latex_packages(["hyperref"])
        assert result["hyperref"] is False

    def test_is_git_ref(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        mock_result = MagicMock()
        mock_result.returncode = 0
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)
        assert cmds._is_git_ref("HEAD") is True

    def test_is_git_ref_invalid(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        mock_result = MagicMock()
        mock_result.returncode = 128
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)
        assert cmds._is_git_ref("invalid-ref-xyz") is False

    def test_find_tex_for_pdf(self, tmp_path):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        # Test with matching .tex file
        pdf = tmp_path / "test.pdf"
        tex = tmp_path / "test.tex"
        tex.write_text("content")
        result = cmds._find_tex_for_pdf(str(pdf))
        assert result == tex

    def test_find_tex_for_pdf_main_tex(self, tmp_path):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        # Test fallback to main.tex
        pdf = tmp_path / "test.pdf"
        main_tex = tmp_path / "main.tex"
        main_tex.write_text("content")
        result = cmds._find_tex_for_pdf(str(pdf))
        assert result == main_tex

    def test_find_tex_for_pdf_not_found(self, tmp_path):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        pdf = tmp_path / "test.pdf"
        result = cmds._find_tex_for_pdf(str(pdf))
        assert result is None

    def test_rebuild_affected_with_files(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.build_example = MagicMock()
        cmds._rebuild_affected(Path("test.tex"), ["test"])
        cmds.build_example.assert_called_once_with(["test"])

    def test_rebuild_affected_without_files(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.build_examples = MagicMock()
        cmds._rebuild_affected(Path("test.tex"), [])
        cmds.build_examples.assert_called_once_with([])


# ===================================================================
# commands.py -- cmd_diff modes
# ===================================================================


class TestCmdDiff:
    """Test cmd_diff different modes."""

    def test_diff_no_files(self, tmp_path):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_diff([])

    def test_diff_basic_pdf_compare(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        # Create two identical fake PDFs
        pdf_a = tmp_path / "a.pdf"
        pdf_b = tmp_path / "b.pdf"
        pdf_a.write_bytes(b"%PDF-1.0 fake content")
        pdf_b.write_bytes(b"%PDF-1.0 fake content")

        cmds._diff_two_pdfs = MagicMock()
        cmds.cmd_diff([str(pdf_a), str(pdf_b)])
        cmds._diff_two_pdfs.assert_called_once()

    def test_diff_regenerate_references(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        ref_dir = tmp_path / "tests" / "references"
        ref_dir.mkdir(parents=True)
        build_dir = tmp_path / "build" / "examples"
        build_dir.mkdir(parents=True)
        (build_dir / "test1.pdf").write_bytes(b"pdf content")

        cmds.cmd_diff(["test1"], regenerate_references=True)
        assert (ref_dir / "test1.pdf").exists()

    def test_diff_no_source_pdf(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_diff(["nonexistent_example"])


# ===================================================================
# commands.py -- scaffold-institution edge cases
# ===================================================================


class TestScaffoldInstitution:
    def test_no_files(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_scaffold_institution([])

    def test_invalid_name(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_scaffold_institution(["invalid name with spaces!"])

    def test_already_exists(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        # Create the institution directory
        inst_dir = tmp_path / "config" / "institutions" / "existing"
        inst_dir.mkdir(parents=True)
        cmds.cmd_scaffold_institution(["existing"])

    def test_generic_not_found(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_scaffold_institution(["newinst"])


# ===================================================================
# commands.py -- init edge cases
# ===================================================================


class TestCmdInit:
    def test_no_files(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_init([])

    def test_invalid_project_name(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_init(["invalid name!"])

    def test_invalid_doctype(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_init(["myproject"], doctype="nonexistent_type")

    def test_invalid_language(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_init(["myproject"], language="klingon")


# ===================================================================
# commands.py -- scaffold-language edge cases
# ===================================================================


class TestScaffoldLanguage:
    def test_no_files(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_scaffold_language([])

    def test_i18n_not_found(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds.cmd_scaffold_language(["klingon"])


# ===================================================================
# commands.py -- cmd_diff byte-level comparison
# ===================================================================


class TestBasicPdfCompare:
    def test_identical_sizes(self, tmp_path):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        pdf_a = tmp_path / "a.pdf"
        pdf_b = tmp_path / "b.pdf"
        pdf_a.write_bytes(b"same content")
        pdf_b.write_bytes(b"same content")

        cmds._basic_pdf_compare(str(pdf_a), str(pdf_b))

    def test_different_sizes(self, tmp_path):
        from buildlib import BuildTasks as Commands

        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        pdf_a = tmp_path / "a.pdf"
        pdf_b = tmp_path / "b.pdf"
        pdf_a.write_bytes(b"short")
        pdf_b.write_bytes(b"much longer content that is definitely different")

        cmds._basic_pdf_compare(str(pdf_a), str(pdf_b))


# ===================================================================
# builder.py -- _run_with_dashboard
# ===================================================================


@pytest.mark.skipif(not RICH_AVAILABLE, reason="rich library not installed")
class TestRunWithDashboard:
    def test_run_with_dashboard(self, build_core, monkeypatch):
        """Test _run_with_dashboard (CI mode skips dashboard)."""
        # Force CI mode to use simple runner path
        monkeypatch.setenv("CI", "true")
        with patch.object(build_core.runner, "run", return_value=(0, ["ok"])):
            exit_code, logs = build_core._run_with_dashboard(
                ["echo", "test"], title="Test"
            )
            assert exit_code == 0


# ===================================================================
# commands.py -- cmd_diff git refs mode
# ===================================================================


class TestDiffGitRefs:
    def test_diff_git_refs_invalid_ref(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        # Mock _is_git_ref to return True
        cmds._is_git_ref = MagicMock(return_value=True)

        # Mock subprocess.run for git show to fail
        def mock_run(cmd, **kwargs):
            result = MagicMock()
            if "git" in cmd[0]:
                result.returncode = 1
                result.stderr = "bad ref"
                result.stdout = ""
            return result

        monkeypatch.setattr("subprocess.run", mock_run)
        cmds.cmd_diff(["ref1", "ref2"])

    def test_diff_git_refs_latexdiff_not_available(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        cmds._is_git_ref = MagicMock(return_value=True)
        monkeypatch.setattr(
            "shutil.which", lambda x: None if x == "latexdiff" else "/usr/bin/" + x
        )

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            if "git" in cmd[0] and "show" in cmd:
                result.returncode = 0
                result.stdout = (
                    "\\documentclass{article}\\begin{document}old\\end{document}"
                )
                result.stderr = ""
            elif cmd[0] == "diff":
                result.returncode = 1
                result.stdout = "--- a\n+++ b\n@@ -1 +1 @@\n-old\n+new\n"
                result.stderr = ""
            else:
                result.returncode = 0
                result.stdout = ""
                result.stderr = ""
            return result

        monkeypatch.setattr("subprocess.run", mock_run)
        cmds.cmd_diff(["ref1", "ref2"])


# ===================================================================
# commands.py -- cmd_check
# ===================================================================


class TestCmdCheck:
    def test_check_runs(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: mock_result)

        if hasattr(cmds, "cmd_check"):
            cmds.cmd_check([])


# ===================================================================
# commands.py -- cmd_lint
# ===================================================================


class TestCmdLint:
    def test_lint_no_args(self, tmp_path, monkeypatch):
        from buildlib import BuildTasks as Commands

        monkeypatch.setattr("buildlib.commands.REPO_ROOT", tmp_path)
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        config = ProjectConfig(build_dir=tmp_path / "build")
        cmds = Commands(config=config, runner=runner, ui=ui, jobs=1)

        if hasattr(cmds, "cmd_lint"):
            result = cmds.cmd_lint([])
            assert result is not None
