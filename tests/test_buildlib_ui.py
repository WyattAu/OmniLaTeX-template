"""Unit tests for buildlib.ui module."""

from __future__ import annotations

from buildlib.ui import TerminalOutput


class TestTerminalOutput:
    """Test TerminalOutput terminal rendering with and without color."""

    def test_color_mode_when_tty(self):
        """When use_color=True, ANSI codes should be present."""
        ui = TerminalOutput(use_color=True)
        assert ui.bold != ""
        assert ui.end != ""
        assert ui.green != ""

    def test_no_color_mode(self):
        """When use_color=False, all ANSI codes should be empty strings."""
        ui = TerminalOutput(use_color=False)
        assert ui.bold == ""
        assert ui.end == ""
        assert ui.green == ""
        assert ui.red == ""
        assert ui.yellow == ""
        assert ui.cyan == ""
        assert ui.blue == ""
        assert ui.gray == ""

    def test_header_output(self, capsys):
        ui = TerminalOutput(use_color=False)
        ui.header("Test Header")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out
        assert "===" in captured.out

    def test_info_output(self, capsys):
        ui = TerminalOutput(use_color=False)
        ui.info("informational message")
        captured = capsys.readouterr()
        assert "[INFO]" in captured.out
        assert "informational message" in captured.out

    def test_success_output(self, capsys):
        ui = TerminalOutput(use_color=False)
        ui.success("all good")
        captured = capsys.readouterr()
        assert "all good" in captured.out

    def test_warning_output(self, capsys):
        ui = TerminalOutput(use_color=False)
        ui.warning("be careful")
        captured = capsys.readouterr()
        assert "be careful" in captured.out

    def test_error_output_goes_to_stderr(self, capsys):
        ui = TerminalOutput(use_color=False)
        ui.error("something broke")
        captured = capsys.readouterr()
        assert "something broke" in captured.err

    def test_debug_output(self, capsys):
        ui = TerminalOutput(use_color=False)
        ui.debug("debugging info")
        captured = capsys.readouterr()
        assert "[DEBUG]" in captured.out
        assert "debugging info" in captured.out

    def test_colorized_header_output(self, capsys):
        ui = TerminalOutput(use_color=True)
        ui.header("Colored Header")
        captured = capsys.readouterr()
        assert "\033[1m" in captured.out  # bold
        assert "\033[94m" in captured.out  # blue
        assert "Colored Header" in captured.out
