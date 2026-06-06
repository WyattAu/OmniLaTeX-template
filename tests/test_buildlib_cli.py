"""Unit tests for buildlib.cli module (argument parsing)."""

from __future__ import annotations

import os

import pytest

from buildlib.cli import main as cli_main


class TestCLIArgumentParsing:
    """Test CLI argument parsing and dispatch."""

    def test_no_command_shows_help_in_ci(self, monkeypatch, capsys):
        """In CI mode, no command should print help and return."""
        monkeypatch.setenv("CI", "true")
        monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
        monkeypatch.delenv("GITLAB_CI", raising=False)
        monkeypatch.setattr("sys.argv", ["build.py"])
        monkeypatch.setattr("sys.stdout.isatty", lambda: False)
        # Should not raise SystemExit
        cli_main()

    def test_build_root_command(self, monkeypatch):
        """Test build-root command dispatches correctly."""
        monkeypatch.setattr("sys.argv", ["build.py", "build-root"])
        monkeypatch.setattr("buildlib.BuildTasks.build_root", lambda self, _: None)
        # Should not raise
        cli_main()

    def test_list_examples_command(self, monkeypatch):
        """Test list-examples command."""
        monkeypatch.setattr("sys.argv", ["build.py", "list-examples"])
        monkeypatch.setattr(
            "buildlib.BuildTasks.list_examples",
            lambda self, _, output_format="text": None,
        )
        cli_main()

    def test_list_examples_json_format(self, monkeypatch):
        """Test list-examples --format json."""
        monkeypatch.setattr(
            "sys.argv", ["build.py", "list-examples", "--format", "json"]
        )
        monkeypatch.setattr(
            "buildlib.BuildTasks.list_examples",
            lambda self, _, output_format="text": None,
        )
        cli_main()

    def test_preflight_command(self, monkeypatch):
        """Test preflight command."""
        monkeypatch.setattr("sys.argv", ["build.py", "preflight"])
        monkeypatch.setattr("buildlib.BuildTasks.preflight", lambda self, _: None)
        cli_main()

    def test_clean_command(self, monkeypatch):
        """Test clean command."""
        monkeypatch.setattr("sys.argv", ["build.py", "clean"])
        monkeypatch.setattr("buildlib.BuildTasks.clean_all", lambda self, _: None)
        cli_main()

    def test_cache_stats_command(self, monkeypatch):
        """Test cache-stats command."""
        monkeypatch.setattr("sys.argv", ["build.py", "cache-stats"])
        monkeypatch.setattr("buildlib.BuildTasks.cmd_cache_stats", lambda self, _: None)
        cli_main()

    def test_cache_clear_command(self, monkeypatch):
        """Test cache-clear command."""
        monkeypatch.setattr("sys.argv", ["build.py", "cache-clear"])
        monkeypatch.setattr("buildlib.BuildTasks.cmd_cache_clear", lambda self, _: None)
        cli_main()

    def test_mode_argument(self, monkeypatch):
        """Test --mode argument."""
        monkeypatch.setattr("sys.argv", ["build.py", "--mode", "prod", "preflight"])
        monkeypatch.setattr("buildlib.BuildTasks.preflight", lambda self, _: None)
        cli_main()

    def test_verbose_argument(self, monkeypatch):
        """Test --verbose flag."""
        monkeypatch.setattr("sys.argv", ["build.py", "--verbose", "preflight"])
        monkeypatch.setattr("buildlib.BuildTasks.preflight", lambda self, _: None)
        cli_main()

    def test_jobs_argument(self, monkeypatch):
        """Test -j/--jobs argument."""
        monkeypatch.setattr("sys.argv", ["build.py", "-j", "8", "preflight"])
        monkeypatch.setattr("buildlib.BuildTasks.preflight", lambda self, _: None)
        cli_main()

    def test_force_argument(self, monkeypatch):
        """Test --force flag."""
        monkeypatch.setattr("sys.argv", ["build.py", "--force", "preflight"])
        monkeypatch.setattr("buildlib.BuildTasks.preflight", lambda self, _: None)
        cli_main()

    def test_timings_argument(self, monkeypatch):
        """Test --timings flag."""
        monkeypatch.setattr("sys.argv", ["build.py", "--timings", "preflight"])
        monkeypatch.setattr("buildlib.BuildTasks.preflight", lambda self, _: None)
        cli_main()

    def test_source_date_epoch_argument(self, monkeypatch):
        """Test --source-date-epoch sets SOURCE_DATE_EPOCH."""
        monkeypatch.setattr(
            "sys.argv",
            ["build.py", "--source-date-epoch", "1700000000", "preflight"],
        )
        monkeypatch.setattr("buildlib.BuildTasks.preflight", lambda self, _: None)
        cli_main()
        assert os.environ.get("SOURCE_DATE_EPOCH") == "1700000000"

    def test_build_example_command(self, monkeypatch):
        """Test build-example command with file arguments."""
        monkeypatch.setattr(
            "sys.argv", ["build.py", "build-example", "minimal-starter"]
        )
        monkeypatch.setattr("buildlib.BuildTasks.build_example", lambda self, _: None)
        cli_main()

    def test_doctor_command(self, monkeypatch):
        """Test doctor command."""
        monkeypatch.setattr("sys.argv", ["build.py", "doctor"])
        monkeypatch.setattr("buildlib.BuildTasks.cmd_doctor", lambda self, _: None)
        cli_main()

    def test_scaffold_institution_command(self, monkeypatch):
        """Test scaffold-institution command."""
        monkeypatch.setattr(
            "sys.argv", ["build.py", "scaffold-institution", "test-institution"]
        )
        monkeypatch.setattr(
            "buildlib.BuildTasks.cmd_scaffold_institution",
            lambda self, _: None,
        )
        cli_main()

    def test_scaffold_language_command(self, monkeypatch):
        """Test scaffold-language command."""
        monkeypatch.setattr("sys.argv", ["build.py", "scaffold-language", "testlang"])
        monkeypatch.setattr(
            "buildlib.BuildTasks.cmd_scaffold_language",
            lambda self, _: None,
        )
        cli_main()

    def test_init_command(self, monkeypatch):
        """Test init command with project name."""
        monkeypatch.setattr("sys.argv", ["build.py", "init", "test-project"])
        monkeypatch.setattr(
            "buildlib.BuildTasks.cmd_init",
            lambda self, *args, **kwargs: None,
        )
        cli_main()

    def test_init_with_thesis_flag(self, monkeypatch):
        """Test init command with --thesis flag."""
        monkeypatch.setattr("sys.argv", ["build.py", "init", "test-thesis", "--thesis"])
        monkeypatch.setattr(
            "buildlib.BuildTasks.cmd_init",
            lambda self, *args, **kwargs: None,
        )
        cli_main()

    def test_cnf_line_argument(self, monkeypatch):
        """Test --cnf-line argument."""
        monkeypatch.setattr(
            "sys.argv",
            ["build.py", "--cnf-line", "font_size=12pt", "preflight"],
        )
        monkeypatch.setattr("buildlib.BuildTasks.preflight", lambda self, _: None)
        cli_main()

    def test_invalid_command_exits(self, monkeypatch):
        """Test that an unknown command produces an error."""
        monkeypatch.setattr("sys.argv", ["build.py", "nonexistent-cmd"])
        with pytest.raises(SystemExit):
            cli_main()
