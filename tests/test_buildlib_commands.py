"""Unit tests for buildlib.commands module (command mixin)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from buildlib.commands.commands import _Commands
from buildlib.config import REPO_ROOT, ProjectConfig
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput


@pytest.fixture
def commands():
    ui = TerminalOutput(use_color=False)
    runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
    config = ProjectConfig()
    obj = object.__new__(_Commands)
    obj.ui = ui
    obj.runner = runner
    obj.config = config
    obj.jobs = 1
    return obj


class TestCheckTool:
    def test_found_tool(self, commands):
        name, ok, detail = commands._check_tool("python3", "Python")
        assert ok is True
        assert "Found" in detail

    def test_missing_tool(self, commands):
        name, ok, detail = commands._check_tool("nonexistent_xyz", "Missing")
        assert ok is False
        assert "Not found" in detail

    def test_missing_optional_tool(self, commands):
        name, ok, detail = commands._check_tool(
            "nonexistent_xyz", "Optional", required=False
        )
        assert ok is True


class TestGetTexliveVersion:
    def test_returns_int_or_none(self, commands):
        result = commands._get_texlive_version()
        assert result is None or isinstance(result, int)


class TestCheckLatexPackage:
    def test_returns_bool(self, commands):
        result = commands._check_latex_package("fontspec")
        assert isinstance(result, bool)


class TestCheckAllLatexPackages:
    def test_returns_dict(self, commands):
        result = commands._check_all_latex_packages(["fontspec", "hyperref"])
        assert isinstance(result, dict)
        assert "fontspec" in result

    def test_empty_list(self, commands):
        result = commands._check_all_latex_packages([])
        assert result == {}


class TestCmdPreflight:
    def test_preflight_runs(self, commands, capsys):
        commands.cmd_preflight()
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestCmdTest:
    def test_cmd_test_returns_int(self, commands):
        with patch("buildlib.commands.commands.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = commands.cmd_test()
            assert isinstance(result, int)


class TestIsGitRef:
    def test_valid_ref(self, commands):
        assert commands._is_git_ref("HEAD") is True

    def test_invalid_ref(self, commands):
        assert commands._is_git_ref("nonexistent_ref_xyz_12345") is False


class TestFindTexForPdf:
    def test_finds_main_tex(self, commands):
        result = commands._find_tex_for_pdf(str(REPO_ROOT / "main.pdf"))
        if (REPO_ROOT / "main.tex").exists():
            assert result is not None
            assert result.name == "main.tex"

    def test_no_tex_found(self, commands, tmp_path):
        result = commands._find_tex_for_pdf(str(tmp_path / "nonexistent.pdf"))
        assert result is None


class TestBasicPdfCompare:
    def test_same_size_files(self, commands, tmp_path, capsys):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(b"PDF-1.4 content")
        b.write_bytes(b"PDF-1.4 content")
        commands._basic_pdf_compare(str(a), str(b))
        captured = capsys.readouterr()
        assert "identical" in captured.out.lower() or "bytes" in captured.out.lower()


class TestCmdDiff:
    def test_diff_no_files(self, commands, capsys):
        commands.cmd_diff([])
        captured = capsys.readouterr()
        assert "No examples" in captured.out or "SKIP" in captured.out


class TestCmdScaffoldInstitution:
    def test_scaffold_no_args(self, commands, capsys):
        commands.cmd_scaffold_institution([])
        captured = capsys.readouterr()
        assert "Usage" in captured.out

    def test_scaffold_invalid_name(self, commands, capsys):
        commands.cmd_scaffold_institution(["invalid name!"])
        captured = capsys.readouterr()
        # Error messages go to stderr
        assert "Invalid" in captured.err

    def test_scaffold_existing_institution(self, commands, capsys):
        commands.cmd_scaffold_institution(["generic"])
        captured = capsys.readouterr()
        assert "already exists" in captured.err


class TestCmdScaffoldLanguage:
    def test_scaffold_no_args(self, commands, capsys):
        commands.cmd_scaffold_language([])
        captured = capsys.readouterr()
        assert "Usage" in captured.out


class TestCmdInit:
    def test_init_no_args(self, commands, capsys):
        commands.cmd_init([])
        captured = capsys.readouterr()
        assert "Usage" in captured.out

    def test_init_invalid_name(self, commands, capsys):
        commands.cmd_init(["invalid name!"])
        captured = capsys.readouterr()
        assert "Invalid" in captured.err

    def test_init_existing_directory(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "existing-project").mkdir()
        commands.cmd_init(["existing-project"])
        captured = capsys.readouterr()
        assert "already exists" in captured.err

    def test_init_valid_name(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["test-project"])
        captured = capsys.readouterr()
        assert "Initialized" in captured.out
        assert (tmp_path / "test-project").is_dir()
        assert (tmp_path / "test-project" / "main.tex").exists()


class TestCmdInitThesis:
    def test_init_thesis_creates_structure(
        self, commands, capsys, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-thesis"], thesis=True)
        captured = capsys.readouterr()
        assert "Initialized" in captured.out
        thesis_dir = tmp_path / "my-thesis"
        assert (thesis_dir / "chapters").is_dir()
        assert (thesis_dir / "bib").is_dir()
        assert (thesis_dir / "figures").is_dir()
        assert (thesis_dir / "README.md").exists()


class TestCmdDoctor:
    def test_doctor_runs(self, commands, capsys):
        commands.cmd_doctor()
        captured = capsys.readouterr()
        assert "OmniLaTeX Doctor" in captured.out or "Platform" in captured.out


class TestCmdCheck:
    def test_check_returns_int(self, commands):
        result = commands.cmd_check([])
        assert isinstance(result, int)

    def test_check_on_repo_root(self, commands):
        result = commands.cmd_check([str(REPO_ROOT)])
        assert isinstance(result, int)


class TestCmdLint:
    def test_cmd_lint_returns_int(self, commands):
        with patch("buildlib.commands.commands.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = commands.cmd_lint()
            assert isinstance(result, int)


class TestCmdWatch:
    def test_watch_imports(self, commands):
        assert hasattr(commands, "cmd_watch")
        assert callable(commands.cmd_watch)
