"""Unit tests for buildlib.runner module."""

from __future__ import annotations

import os

import pytest

from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput


@pytest.fixture
def runner():
    ui = TerminalOutput(use_color=False)
    return CommandRunner(ui=ui, build_mode="dev", verbose=False)


@pytest.fixture
def verbose_runner():
    ui = TerminalOutput(use_color=False)
    return CommandRunner(ui=ui, build_mode="dev", verbose=True)


class TestCommandRunner:
    """Test CommandRunner subprocess execution."""

    def test_default_timeout(self):
        assert CommandRunner.DEFAULT_TIMEOUT == 3600

    def test_run_success(self, runner):
        exit_code, logs = runner.run(["echo", "hello world"])
        assert exit_code == 0
        assert any("hello world" in line for line in logs)

    def test_run_failure(self, runner):
        exit_code, logs = runner.run(["false"])
        assert exit_code == 1

    def test_run_command_not_found(self, runner):
        exit_code, logs = runner.run(["nonexistent_command_xyz_12345"])
        assert exit_code == -1
        assert any("Command not found" in line for line in logs)

    def test_run_permission_denied(self, runner, tmp_path):
        if os.getuid() == 0:
            pytest.skip("Cannot test permission denied when running as root")
        script = tmp_path / "noperm.sh"
        script.write_text("#!/bin/bash\necho hi")
        script.chmod(0o000)
        exit_code, logs = runner.run([str(script)])
        assert exit_code == -1

    def test_run_with_cwd(self, runner, tmp_path):
        exit_code, logs = runner.run(["pwd"], cwd=tmp_path)
        assert exit_code == 0
        assert any(str(tmp_path) in line for line in logs)

    def test_run_sets_build_mode_env(self, runner, monkeypatch):
        monkeypatch.delenv("BUILD_MODE", raising=False)
        exit_code, logs = runner.run(["printenv", "BUILD_MODE"])
        assert exit_code == 0
        assert any("dev" in line for line in logs)

    def test_run_with_extra_env(self, runner):
        exit_code, logs = runner.run(
            ["printenv", "CUSTOM_VAR"],
            extra_env={"CUSTOM_VAR": "test_value"},
        )
        assert exit_code == 0
        assert any("test_value" in line for line in logs)

    def test_run_callback_receives_lines(self, runner):
        received_lines = []
        exit_code, logs = runner.run(
            ["echo", "callback_test"],
            on_line=lambda line: received_lines.append(line),
        )
        assert exit_code == 0
        assert any("callback_test" in line for line in received_lines)

    @pytest.mark.slow
    def test_run_timeout(self, runner):
        """Test timeout handling with a command that hangs.

        Marked slow because it depends on process timing which varies
        across Python versions and CI environments.
        """
        exit_code, logs = runner.run(
            ["sleep", "60"],
            timeout=2,
        )
        assert exit_code == -1
        assert any("timed out" in line.lower() for line in logs)

    def test_run_verbose_debug_output(self, verbose_runner, capsys):
        verbose_runner.run(["echo", "verbose_test"])
        captured = capsys.readouterr()
        assert "RUN" in captured.out

    def test_run_os_error_handling(self, runner):
        """Test OSError handling for invalid command paths."""
        exit_code, logs = runner.run([""])
        assert exit_code == -1
