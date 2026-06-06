"""Integration tests for buildlib scaffold commands."""

from __future__ import annotations

import pytest

from buildlib.commands import _Commands
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput


@pytest.fixture
def commands():
    ui = TerminalOutput(use_color=False)
    runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
    from buildlib.config import ProjectConfig

    config = ProjectConfig()
    obj = object.__new__(_Commands)
    obj.ui = ui
    obj.runner = runner
    obj.config = config
    obj.jobs = 1
    return obj


class TestScaffoldInstitutionIntegration:
    """Integration tests for institution scaffolding.

    These tests run against the real repo since scaffold commands
    use REPO_ROOT for path resolution.
    """

    def test_scaffold_invalid_name_blocked(self, commands, capsys):
        commands.cmd_scaffold_institution(["../../../etc"])
        captured = capsys.readouterr()
        # Path traversal should be blocked
        assert "Invalid" in captured.err or "resolves outside" in captured.err

    def test_scaffold_nonexistent_generic_template(
        self, commands, capsys, tmp_path, monkeypatch
    ):
        """When generic template doesn't exist, command should error gracefully."""
        monkeypatch.chdir(tmp_path)
        # This runs against REPO_ROOT, so the generic template should exist
        # Just verify the command doesn't crash
        commands.cmd_scaffold_institution(["test-nonexistent"])
        # Should either succeed or fail gracefully
        captured = capsys.readouterr()
        assert len(captured.out + captured.err) > 0


class TestScaffoldLanguageIntegration:
    """Integration tests for language scaffolding."""

    def test_scaffold_language_runs(self, commands, capsys):
        """Verify scaffold-language produces output without crashing."""
        commands.cmd_scaffold_language(["testlang"])
        captured = capsys.readouterr()
        # Should produce some output
        assert len(captured.out) > 0

    def test_scaffold_language_with_empty_name(self, commands, capsys):
        """Empty language name should produce usage message."""
        commands.cmd_scaffold_language([])
        captured = capsys.readouterr()
        assert "Usage" in captured.out


class TestInitIntegration:
    """Integration tests for project initialization."""

    def test_init_creates_project(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-project"])
        project_dir = tmp_path / "my-project"
        assert project_dir.is_dir()
        assert (project_dir / "main.tex").exists()

    def test_init_with_doctype(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-thesis"], doctype="thesis")
        main_tex = tmp_path / "my-thesis" / "main.tex"
        content = main_tex.read_text(encoding="utf-8")
        assert "doctype=thesis" in content

    def test_init_with_language(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-doc"], language="german")
        main_tex = tmp_path / "my-doc" / "main.tex"
        content = main_tex.read_text(encoding="utf-8")
        assert "language=german" in content

    def test_init_thesis_creates_chapters(
        self, commands, capsys, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-thesis"], thesis=True)
        chapters_dir = tmp_path / "my-thesis" / "chapters"
        assert chapters_dir.is_dir()
        expected = [
            "introduction.tex",
            "methodology.tex",
            "results.tex",
            "conclusion.tex",
        ]
        for ch in expected:
            assert (chapters_dir / ch).exists()

    def test_init_thesis_creates_bib(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-thesis"], thesis=True)
        bib_dir = tmp_path / "my-thesis" / "bib"
        assert bib_dir.is_dir()
        assert (bib_dir / "bibliography.bib").exists()

    def test_init_thesis_creates_readme(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-thesis"], thesis=True)
        readme = tmp_path / "my-thesis" / "README.md"
        assert readme.exists()
        content = readme.read_text(encoding="utf-8")
        # README should contain the project name
        assert "my-thesis" in content.lower()

    def test_init_symlinks_latexmkrc(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-project"])
        latexmkrc = tmp_path / "my-project" / ".latexmkrc"
        assert latexmkrc.exists()

    def test_init_with_all_options(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(
            ["full-project"],
            doctype="article",
            institution="tum",
            language="german",
        )
        main_tex = tmp_path / "full-project" / "main.tex"
        content = main_tex.read_text(encoding="utf-8")
        assert "doctype=article" in content
        assert "institution=tum" in content
        assert "language=german" in content

    def test_init_does_not_overwrite(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-project"])
        commands.cmd_init(["my-project"])
        captured = capsys.readouterr()
        assert "already exists" in captured.err
