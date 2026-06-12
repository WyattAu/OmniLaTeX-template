"""Unit tests for buildlib.latex_errors module."""

from __future__ import annotations

import pytest

from buildlib.latex_errors import (
    Diagnostic,
    ErrorClass,
    Severity,
    format_diagnostics,
    parse_latex_log,
)


class TestParseLatexLog:
    """Test LaTeX log parsing for various error patterns."""

    def test_empty_log(self):
        result = parse_latex_log("")
        assert result == []

    def test_no_errors(self):
        log = "This is pdfTeX, version 3.14159265-2.6-1.40.21\nOutput written on main.pdf."
        result = parse_latex_log(log)
        assert result == []

    def test_general_error(self):
        log = "! Undefined control sequence.\n<recently read> \\foo\nl.5"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].severity == Severity.ERROR
        assert result[0].error_class == ErrorClass.UNDEFINED_COMMAND
        assert "\\foo" in result[0].message
        assert result[0].source_line == 5

    def test_latex_error(self):
        log = "! LaTeX Error: File `missing.sty' not found."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].severity == Severity.ERROR
        assert result[0].error_class == ErrorClass.FILE_NOT_FOUND
        assert "missing.sty" in result[0].message

    def test_latex_error_general(self):
        log = "! LaTeX Error: Something went wrong."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.LATEX_ERROR

    def test_package_error(self):
        log = "! Package hyperref Error: Driver file `pdftex.def' not found."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].severity == Severity.ERROR
        assert result[0].error_class == ErrorClass.PACKAGE_ERROR
        assert "[hyperref]" in result[0].message

    def test_missing_dollar(self):
        log = "! Missing $ inserted.\nl.3 \\textbf{x_i}"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.MATH_MODE
        assert result[0].source_line == 3

    def test_missing_brace_close(self):
        log = "! Missing } inserted.\nl.10 \\end{document}"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.MISSING_BRACE

    def test_missing_endgroup(self):
        log = "! Missing \\endgroup inserted.\nl.20 \\end{itemize}"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.MISSING_END

    def test_invalid_character(self):
        log = "! Text line contains an invalid character.\nl.7 \x00"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.INVALID_CHARACTER

    def test_dimension_error(self):
        log = "! Illegal unit of measure.\nl.12 \\setlength{\\foo}{bar}"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.DIMENSION_ERROR

    def test_number_error(self):
        log = "! Missing number, treated as zero.\nl.8 \\count0="
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.NUMBER_ERROR

    def test_alignment_error(self):
        log = "! Misplaced alignment tab character &.\nl.15 a & b"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.ALIGNMENT_ERROR

    def test_runaway_argument(self):
        log = "! Runaway argument?\n{unclosed argument\nl.5 \\end{document}"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.RUNAWAY

    def test_encoding_error(self):
        log = "! Package inputenc Error: Invalid UTF-8 byte sequence."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.ENCODING_ERROR

    def test_package_warning(self):
        log = "Package hyperref Warning: Token not allowed in a PDF string."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].severity == Severity.WARNING
        assert result[0].error_class == ErrorClass.PACKAGE_WARNING

    def test_latex_warning(self):
        log = "LaTeX Warning: Reference `fig:test' on page 1 undefined."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].severity == Severity.WARNING
        assert result[0].error_class == ErrorClass.CROSS_REFERENCE

    def test_overfull_hbox(self):
        log = "Overfull \\hbox (10.5pt too wide) in paragraph at lines 20--25"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].severity == Severity.WARNING
        assert result[0].error_class == ErrorClass.OVERFULL_HBOX

    def test_underfull_hbox(self):
        log = "Underfull \\hbox (badness 10000) in paragraph at lines 30--35"
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].severity == Severity.WARNING
        assert result[0].error_class == ErrorClass.UNDERFULL_HBOX

    def test_citation_warning(self):
        log = "Package biblatex Warning: Citation `key123' undefined."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.CITATION_WARNING

    def test_cross_reference_warning(self):
        log = "LaTeX Warning: Reference `sec:intro' on page 2 undefined."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.CROSS_REFERENCE

    def test_font_warning(self):
        log = "Font Warning: Font shape `T1/cmr/bx/sc' in size <17.28> not available."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].severity == Severity.WARNING
        assert result[0].error_class == ErrorClass.FONT_WARNING

    def test_multiple_errors(self):
        log = (
            "! Undefined control sequence.\n"
            "<recently read> \\foo\n"
            "l.5\n"
            "! Missing $ inserted.\n"
            "l.10"
        )
        result = parse_latex_log(log)
        assert len(result) == 2
        assert result[0].error_class == ErrorClass.UNDEFINED_COMMAND
        assert result[1].error_class == ErrorClass.MATH_MODE

    def test_source_file_tracking(self):
        log = (
            "(./chapter1.tex\n"
            "! Undefined control sequence.\n"
            "<recently read> \\bar\n"
            "l.12"
        )
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].source_file == "chapter1.tex"

    def test_exclude_warnings(self):
        log = (
            "! Undefined control sequence.\n"
            "Package hyperref Warning: Token not allowed."
        )
        result = parse_latex_log(log, include_warnings=False)
        assert len(result) == 1
        assert result[0].severity == Severity.ERROR

    def test_suggestion_attached(self):
        log = "! Undefined control sequence.\n<recently read> \\foo\nl.5"
        result = parse_latex_log(log)
        assert result[0].suggestion is not None
        assert "typos" in result[0].suggestion.lower() or "package" in result[0].suggestion.lower()

    def test_teX_capacity_exceeded(self):
        log = "TeX capacity exceeded, sorry [pattern memory=75000]."
        result = parse_latex_log(log)
        assert len(result) == 1
        assert result[0].error_class == ErrorClass.HYPHENATION


class TestDiagnostic:
    """Test Diagnostic dataclass."""

    def test_to_dict_minimal(self):
        d = Diagnostic(message="test", severity=Severity.ERROR, error_class=ErrorClass.GENERAL_ERROR)
        result = d.to_dict()
        assert result["message"] == "test"
        assert result["severity"] == "error"
        assert result["error_class"] == "general_error"
        assert "source_file" not in result
        assert "suggestion" not in result

    def test_to_dict_full(self):
        d = Diagnostic(
            message="test",
            severity=Severity.WARNING,
            error_class=ErrorClass.OVERFULL_HBOX,
            source_file="main.tex",
            source_line=42,
            log_line=100,
            suggestion="Try \\sloppy",
            context="some context",
        )
        result = d.to_dict()
        assert result["source_file"] == "main.tex"
        assert result["source_line"] == 42
        assert result["log_line"] == 100
        assert result["suggestion"] == "Try \\sloppy"
        assert result["context"] == "some context"


class TestFormatDiagnostics:
    """Test diagnostic formatting."""

    def test_empty_diagnostics(self):
        result = format_diagnostics([], use_color=False)
        assert "No errors" in result

    def test_single_error_no_color(self):
        diag = Diagnostic(
            message="test error",
            severity=Severity.ERROR,
            error_class=ErrorClass.GENERAL_ERROR,
        )
        result = format_diagnostics([diag], use_color=False)
        assert "ERROR" in result
        assert "test error" in result

    def test_with_suggestion_no_color(self):
        diag = Diagnostic(
            message="test error",
            severity=Severity.ERROR,
            error_class=ErrorClass.UNDEFINED_COMMAND,
            suggestion="Check for typos",
        )
        result = format_diagnostics([diag], use_color=False, show_suggestions=True)
        assert "Hint: Check for typos" in result

    def test_with_source_location(self):
        diag = Diagnostic(
            message="test error",
            severity=Severity.ERROR,
            error_class=ErrorClass.GENERAL_ERROR,
            source_file="main.tex",
            source_line=42,
        )
        result = format_diagnostics([diag], use_color=False)
        assert "main.tex:42" in result

    def test_color_output(self):
        diag = Diagnostic(
            message="test error",
            severity=Severity.ERROR,
            error_class=ErrorClass.GENERAL_ERROR,
        )
        result = format_diagnostics([diag], use_color=True)
        assert "\033[31m" in result  # Red for errors

    def test_mixed_severities(self):
        diags = [
            Diagnostic(message="err", severity=Severity.ERROR, error_class=ErrorClass.GENERAL_ERROR),
            Diagnostic(message="warn", severity=Severity.WARNING, error_class=ErrorClass.OVERFULL_HBOX),
        ]
        result = format_diagnostics(diags, use_color=False)
        assert "1 error(s)" in result
        assert "1 warning(s)" in result
