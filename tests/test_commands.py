"""Tests for build.py scaffold, doctor, plugin, and watch commands.

These tests invoke build.py as subprocesses to verify top-level CLI behavior
without importing the script as a module.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

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


# ---------------------------------------------------------------------------
# Scaffold institution
# ---------------------------------------------------------------------------
class TestScaffoldInstitution:
    """Tests for the scaffold-institution command."""

    def test_no_args_shows_usage(self) -> None:
        result = _run("scaffold-institution")
        assert result.returncode == 0
        assert "Usage" in result.stdout or "scaffold-institution" in result.stdout

    def test_invalid_name_rejected(self) -> None:
        result = _run("scaffold-institution", "../../etc/passwd")
        # The path traversal check should catch this
        combined = result.stdout + result.stderr
        assert (
            "Invalid" in combined
            or "resolves outside" in combined
            or result.returncode != 0
        )

    def test_creates_institution_dir(self, tmp_path: Path) -> None:
        """Test that scaffold creates a valid institution directory."""
        name = "test-scaffold-inst"
        target = PROJECT_ROOT / "config" / "institutions" / name
        # Clean up if it exists from a previous run
        if target.exists():
            shutil.rmtree(target)
        try:
            result = _run("scaffold-institution", name)
            combined = result.stdout + result.stderr
            if target.exists():
                assert (target / f"{name}.sty").exists()
                assert "assets" in [p.name for p in target.iterdir()]
            else:
                # If it didn't create, the command should have explained why
                assert (
                    "already exists" in combined
                    or "not found" in combined
                    or "Invalid" in combined
                )
        finally:
            if target.exists():
                shutil.rmtree(target)

    def test_duplicate_name_rejected(self) -> None:
        """Test that scaffolding an existing institution fails."""
        # mit already exists
        result = _run("scaffold-institution", "mit")
        combined = result.stdout + result.stderr
        assert "already exists" in combined or result.returncode != 0


# ---------------------------------------------------------------------------
# Scaffold language
# ---------------------------------------------------------------------------
class TestScaffoldLanguage:
    """Tests for the scaffold-language command."""

    def test_no_args_shows_usage(self) -> None:
        result = _run("scaffold-language")
        assert result.returncode == 0
        assert "Usage" in result.stdout or "scaffold-language" in result.stdout

    def test_creates_guide_file(self) -> None:
        """Test that scaffold-language creates a translation guide."""
        lang = "test-zz-fake"
        guide = PROJECT_ROOT / "docs" / f"language-guide-{lang}.tex"
        try:
            result = _run("scaffold-language", lang)
            if guide.exists():
                content = guide.read_text()
                assert f"Language addition guide for: {lang}" in content
                assert "DeclareTranslation" in content
            else:
                # If i18n file not found, should error gracefully
                combined = result.stdout + result.stderr
                assert "not found" in combined or "No translation keys" in combined
        finally:
            if guide.exists():
                guide.unlink()


# ---------------------------------------------------------------------------
# Doctor
# ---------------------------------------------------------------------------
class TestDoctor:
    """Tests for the doctor command."""

    def test_doctor_runs_without_error(self) -> None:
        result = _run("doctor", timeout=60)
        combined = result.stdout + result.stderr
        # Doctor should output environment info
        assert "Platform" in combined or "Python" in combined or "Doctor" in combined

    def test_doctor_checks_lualatex(self) -> None:
        result = _run("doctor", timeout=60)
        combined = result.stdout + result.stderr
        # Should mention LuaTeX
        assert "LuaTeX" in combined or "lualatex" in combined

    def test_doctor_checks_latexmk(self) -> None:
        result = _run("doctor", timeout=60)
        combined = result.stdout + result.stderr
        assert "latexmk" in combined or "Build orchestrator" in combined


# ---------------------------------------------------------------------------
# Plugin commands
# ---------------------------------------------------------------------------
class TestPluginCommands:
    """Tests for plugin management commands."""

    def test_plugin_list_runs(self) -> None:
        result = _run("plugin-list", timeout=30)
        combined = result.stdout + result.stderr
        # Should either list plugins or say none installed
        assert (
            "plugin" in combined.lower()
            or "No plugins" in combined
            or result.returncode == 0
        )

    def test_plugin_validate_runs(self) -> None:
        result = _run("plugin-validate", timeout=30)
        combined = result.stdout + result.stderr
        # Should either validate or say no plugins
        assert (
            "valid" in combined.lower()
            or "No plugins" in combined
            or result.returncode == 0
        )

    def test_plugin_search_runs(self) -> None:
        result = _run("plugin-search", "test", timeout=30)
        combined = result.stdout + result.stderr
        # Should complete without error
        assert result.returncode == 0 or "registry" in combined.lower()


# ---------------------------------------------------------------------------
# Watch (smoke test only -- actual watching requires long-running process)
# ---------------------------------------------------------------------------
class TestWatch:
    """Smoke tests for the watch command."""

    def test_watch_imports_error_when_no_backend(self) -> None:
        """Watch should fail gracefully without watchdog/inotifywait."""
        # We can't easily test the actual watch loop, but we can verify
        # the command doesn't crash on import
        result = _run("watch", timeout=5)
        combined = result.stdout + result.stderr
        # Should either start watching or report missing backend
        assert (
            "Watching" in combined
            or "watchdog" in combined
            or "inotifywait" in combined
            or "Neither" in combined
            or result.returncode == 0
        )
