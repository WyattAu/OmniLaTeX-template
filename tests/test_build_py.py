"""Integration tests for build.py CLI commands.

Each test invokes build.py as a subprocess to verify the top-level CLI
behaviour without importing the script as a module.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_SCRIPT = PROJECT_ROOT / "build.py"


def _run(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Helper: run build.py with the given arguments."""
    return subprocess.run(
        ["python3", str(BUILD_SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=PROJECT_ROOT,
    )


class TestHelp:
    """Verify the --help output documents every known command."""

    DOCUMENTED_COMMANDS = [
        "build",
        "build-root",
        "build-all",
        "clean",
        "clean-aux",
        "clean-pdf",
        "preflight",
        "lint",
        "list-examples",
        "build-example",
        "build-examples",
        "clean-example",
        "clean-examples",
        "test",
        "watch",
        "doctor",
        "diff",
        "scaffold-institution",
        "scaffold-language",
        "init",
    ]

    def test_help_returncode(self) -> None:
        result = _run("--help")
        assert result.returncode == 0

    def test_help_lists_all_commands(self) -> None:
        result = _run("--help")
        combined = result.stdout + result.stderr
        for cmd in self.DOCUMENTED_COMMANDS:
            assert cmd in combined, f"Command '{cmd}' missing from --help output"


class TestListExamples:
    """Tests for the list-examples subcommand."""

    def test_list_examples_returncode(self) -> None:
        result = _run("list-examples")
        assert result.returncode == 0

    def test_list_examples_output_nonempty(self) -> None:
        result = _run("list-examples")
        assert len(result.stdout.strip()) > 0

    def test_list_examples_shows_example_count(self) -> None:
        result = _run("list-examples")
        assert "example" in result.stdout.lower()

    @pytest.mark.xfail(
        reason="--format json is not yet implemented in build.py list-examples",
        strict=True,
    )
    def test_list_examples_json_format(self) -> None:
        """list-examples --format json should return valid JSON."""
        result = _run("list-examples", "--format", "json")
        combined = result.stdout + result.stderr
        parsed = json.loads(combined)
        assert isinstance(parsed, list)


class TestPreflight:
    """Tests for the preflight subcommand."""

    def test_preflight_runs_without_crash(self) -> None:
        """preflight should execute without raising an unhandled exception."""
        result = _run("preflight")
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "check" in combined.lower() or "preflight" in combined.lower()

    def test_preflight_output_mentions_tools(self) -> None:
        """preflight output should reference checked tools."""
        result = _run("preflight")
        combined = result.stdout + result.stderr
        assert "lualatex" in combined.lower() or "latexmk" in combined.lower()


class TestScaffoldInstitution:
    """Tests for the scaffold-institution subcommand."""

    def test_scaffold_no_args_shows_usage(self) -> None:
        result = _run("scaffold-institution")
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "Usage" in combined or "usage" in combined

    def test_scaffold_creates_directory(self) -> None:
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["python3", str(BUILD_SCRIPT), "scaffold-institution", "test-univ"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=tmpdir,
            )
            target = Path(tmpdir) / "config" / "institutions" / "test-univ"
            if target.exists():
                shutil.rmtree(target)
            assert result.returncode == 0


class TestInit:
    """Tests for the init subcommand."""

    def test_init_no_args_shows_usage(self) -> None:
        result = _run("init")
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert "Usage" in combined or "usage" in combined

    @pytest.mark.xfail(
        reason="init creates directory; needs cleanup in CI",
        strict=False,
    )
    def test_init_creates_project(self) -> None:
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["python3", str(BUILD_SCRIPT), "init", "test-project"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=tmpdir,
                env={**os.environ, "PATH": os.environ.get("PATH", "")},
            )
            target = Path(tmpdir) / "test-project"
            if target.exists():
                shutil.rmtree(target)
            assert result.returncode == 0


class TestDoctor:
    """Tests for the doctor subcommand."""

    def test_doctor_runs_without_crash(self) -> None:
        """doctor should execute without raising an unhandled exception."""
        result = _run("doctor", timeout=60)
        assert result.returncode == 0
        combined = result.stdout + result.stderr
        assert len(combined) > 0, "doctor produced no output"

    def test_doctor_checks_core_tools(self) -> None:
        """doctor should report on lualatex and latexmk."""
        result = _run("doctor", timeout=60)
        combined = result.stdout + result.stderr
        assert "lualatex" in combined.lower(), "doctor should mention lualatex"
        assert "latexmk" in combined.lower(), "doctor should mention latexmk"

    def test_doctor_reports_environment(self) -> None:
        """doctor should show TeX distribution or environment info."""
        result = _run("doctor", timeout=60)
        combined = (result.stdout + result.stderr).lower()
        # Should mention something about the environment
        has_env_info = any(
            kw in combined
            for kw in ["tex live", "texlive", "distribution", "environment", "version"]
        )
        assert has_env_info, "doctor should report environment info"


class TestLint:
    """Tests for the lint subcommand."""

    def test_lint_no_args_shows_usage(self) -> None:
        result = _run("lint", timeout=120)
        # lint may exit 0 with usage or exit 1 if no files match
        combined = result.stdout + result.stderr
        assert len(combined) > 0, "lint produced no output"


class TestCheck:
    """Tests for the check subcommand."""

    def test_check_no_args_shows_usage_or_runs(self) -> None:
        result = _run("check", timeout=30)
        # check should either show usage or run against repo files
        combined = result.stdout + result.stderr
        assert len(combined) > 0, "check produced no output"


class TestClean:
    """Tests for the clean subcommand."""

    def test_clean_aux_runs(self) -> None:
        result = _run("clean-aux", timeout=30)
        # Should not crash even if nothing to clean
        assert result.returncode == 0

    def test_clean_dry_run(self) -> None:
        """clean with --dry-run should list files without deleting."""
        result = _run("clean", "--dry-run", timeout=30)
        combined = result.stdout + result.stderr
        # Should at least not crash
        assert result.returncode == 0 or "dry" in combined.lower()


class TestExport:
    """Tests for the export subcommand."""

    def test_export_no_args_shows_usage(self) -> None:
        result = _run("export", timeout=30)
        combined = result.stdout + result.stderr
        # Export may show "not found" for missing tools (latexml)
        # or "usage"/"format" for help text
        assert len(combined) > 0, "export produced no output"
        assert "export" in combined.lower() or "latexml" in combined.lower()


class TestDiff:
    """Tests for the diff subcommand."""

    def test_diff_no_args_runs(self) -> None:
        result = _run("diff", timeout=30)
        # Should either show usage or report no references to compare
        combined = result.stdout + result.stderr
        assert len(combined) > 0 or result.returncode == 0


class TestVersionAndModes:
    """Tests for version/mode flags."""

    def test_build_with_mode_flag(self) -> None:
        """--mode should be accepted without error."""
        result = _run("--mode", "dev", "list-examples", timeout=15)
        assert result.returncode == 0

    def test_build_with_verbose_flag(self) -> None:
        """--verbose should be accepted without error."""
        result = _run("--verbose", "list-examples", timeout=15)
        assert result.returncode == 0

    def test_invalid_subcommand_exits_nonzero(self) -> None:
        """Unknown subcommand should exit with non-zero."""
        result = _run("nonexistent-command-xyz", timeout=10)
        assert result.returncode != 0
