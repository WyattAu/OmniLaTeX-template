"""LaTeX log file parser for actionable error messages.

Parses latexmk/lualatex output into classified, actionable diagnostics
with source line mapping and fix suggestions. Integrates with build.py
output and VS Code diagnostics.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Severity(Enum):
    """Diagnostic severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ErrorClass(Enum):
    """LaTeX error classification for fix suggestion mapping."""
    UNDEFINED_COMMAND = "undefined_command"
    MISSING_BRACE = "missing_brace"
    MISSING_PACKAGE = "missing_package"
    MATH_MODE = "math_mode"
    PACKAGE_ERROR = "package_error"
    PACKAGE_WARNING = "package_warning"
    OVERFULL_HBOX = "overfull_hbox"
    UNDERFULL_HBOX = "underfull_hbox"
    INVALID_CHARACTER = "invalid_character"
    MISSING_END = "missing_end"
    DIMENSION_ERROR = "dimension_error"
    NUMBER_ERROR = "number_error"
    ALIGNMENT_ERROR = "alignment_error"
    FILE_NOT_FOUND = "file_not_found"
    ENCODING_ERROR = "encoding_error"
    GENERAL_ERROR = "general_error"
    GENERAL_WARNING = "general_warning"
    LATEX_ERROR = "latex_error"
    HYPHENATION = "hyphenation"
    FONT_WARNING = "font_warning"
    CITATION_WARNING = "citation_warning"
    CROSS_REFERENCE = "cross_reference"
    RUNAWAY = "runaway"


@dataclass
class Diagnostic:
    """A single parsed diagnostic from a LaTeX log."""
    message: str
    severity: Severity
    error_class: ErrorClass
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    log_line: Optional[int] = None
    suggestion: Optional[str] = None
    context: Optional[str] = None
    raw: Optional[str] = None

    def to_dict(self) -> dict:
        d = {
            "message": self.message,
            "severity": self.severity.value,
            "error_class": self.error_class.value,
        }
        if self.source_file:
            d["source_file"] = self.source_file
        if self.source_line:
            d["source_line"] = self.source_line
        if self.log_line is not None:
            d["log_line"] = self.log_line
        if self.suggestion:
            d["suggestion"] = self.suggestion
        if self.context:
            d["context"] = self.context
        return d


# ---------------------------------------------------------------------------
# Regex patterns for LaTeX log parsing
# ---------------------------------------------------------------------------

# General LaTeX error: "! <message>."
_RE_GENERAL_ERROR = re.compile(r"^!\s+(.+?)\.\s*$")

# LaTeX error: "! LaTeX Error: <message>"
_RE_LATEX_ERROR = re.compile(r"^!\s+LaTeX Error:\s*(.+)$")

# Undefined control sequence: "! Undefined control sequence.\n<recently read> \command"
_RE_UNDEFINED_CMD = re.compile(
    r"^!\s+Undefined control sequence\.\s*$"
)

# Missing character inserted: "! Missing $ inserted."
_RE_MISSING_DOLLAR = re.compile(r"^!\s+Missing \$ inserted\.?\s*$")

# Missing brace: "! Missing } inserted." or "! Missing { inserted."
_RE_MISSING_BRACE = re.compile(r"^!\s+Missing ([{}]) inserted\.?\s*$")

# Missing endgroup: "! Missing \endgroup inserted."
_RE_MISSING_ENDGROUP = re.compile(r"^!\s+Missing \\endgroup inserted\.?\s*$")

# Missing endcsname: "! Missing \endcsname inserted."
_RE_MISSING_ENDCSNAME = re.compile(r"^!\s+Missing \\endcsname inserted\.?\s*$")

# Package error: "! Package <pkg> Error: <message>"
_RE_PACKAGE_ERROR = re.compile(r"^!\s+Package (\S+) Error:\s*(.+)$")

# Package warning: "Package <pkg> Warning: <message>"
_RE_PACKAGE_WARNING = re.compile(r"^Package\s+(\S+)\s+Warning:\s*(.+)$")

# LaTeX warning: "LaTeX Warning: <message>"
_RE_LATEX_WARNING = re.compile(r"^LaTeX Warning:\s*(.+)$")

# Overfull hbox: "Overfull \hbox (<width> too wide) in paragraph at lines <start>--<end>"
_RE_OVERFULL_HBOX = re.compile(
    r"^Overfull\s+\\hbox\s+\(([^)]+) too wide\)\s+in paragraph at lines?\s+(\d+)--(\d+)"
)

# Underfull hbox: "Underfull \hbox (badness <n>) in paragraph at lines <start>--<end>"
_RE_UNDERFULL_HBOX = re.compile(
    r"^Underfull\s+\\hbox\s+\(badness\s+(\d+)\)\s+in paragraph at lines?\s+(\d+)--(\d+)"
)

# Invalid character: "! Text line contains an invalid character."
_RE_INVALID_CHAR = re.compile(r"^!\s+Text line contains an invalid character\.?\s*$")

# Dimension error: "! Illegal unit of measure."
_RE_DIMENSION_ERROR = re.compile(r"^!\s+Illegal unit of measure\.?\s*$")

# Number error: "! Missing number, treated as zero."
_RE_NUMBER_ERROR = re.compile(r"^!\s+Missing number,\s+treated as zero\.?\s*$")

# Alignment error: "! Misplaced alignment tab character &."
_RE_ALIGNMENT_ERROR = re.compile(r"^!\s+Misplaced alignment tab character &\.?\s*$")

# File not found: "! LaTeX Error: File `<file>' not found."
_RE_FILE_NOT_FOUND = re.compile(
    r"^!\s+LaTeX Error:\s+File `([^']+)'\s+not found\.?\s*$"
)

# Encoding error: "! Package inputenc Error: Invalid UTF-8 byte sequence"
_RE_ENCODING_ERROR = re.compile(
    r"^!\s+Package inputenc Error:.*Invalid UTF-8"
)

# Runaway argument: "! Runaway argument?"
_RE_RUNAWAY = re.compile(r"^!\s+Runaway argument\?")

# Font warning: "Font Warning: ... size substitutions" or "Font shape ... not available"
_RE_FONT_WARNING = re.compile(r"^Font\s+Warning:", re.IGNORECASE)

# Citation warning: "Package biblatex Warning: Citation ... undefined"
_RE_CITATION_WARNING = re.compile(
    r"^Package\s+biblatex\s+Warning.*Citation.*undefined", re.IGNORECASE
)

# Cross-reference warning: "LaTeX Warning: Reference `...' on page ... undefined"
_RE_CROSSREF_WARNING = re.compile(
    r"^LaTeX Warning:\s+Reference `[^']*'\s+on page.*undefined"
)

# Hyphenation warning: "TeX capacity exceeded, sorry [pattern memory=...]"
_RE_HYPHENATION = re.compile(r"^TeX capacity exceeded", re.IGNORECASE)

# Source file hint: "(./filename.tex ..." or "<filename.tex ..." or "(filename.tex ..."
_RE_SOURCE_HINT = re.compile(
    r"[(<](?:\./)?([^\s()<>]+\.(?:tex|sty|cls|bib|def))"
)

# Line number hint: "l.<number>" or "line <number>"
_RE_LINE_HINT = re.compile(r"(?:^|\s)l\.(\d+)(?:\s|$)")
_RE_LINE_HINT2 = re.compile(r"(?:^|\s)line\s+(\d+)(?:\s|$)")

# Recent read context: "<recently read> \command"
_RE_RECENTLY_READ = re.compile(r"<recently read>\s+(\\?\S+)")


# ---------------------------------------------------------------------------
# Fix suggestions mapping
# ---------------------------------------------------------------------------

_FIX_SUGGESTIONS: dict[ErrorClass, str] = {
    ErrorClass.UNDEFINED_COMMAND: (
        "Check for typos in the command name. If it requires a package, "
        "add \\usepackage{<package>} in the preamble."
    ),
    ErrorClass.MISSING_BRACE: (
        "Check matching braces { } in the surrounding code. "
        "Count opening and closing braces to find the mismatch."
    ),
    ErrorClass.MISSING_PACKAGE: (
        "Add \\usepackage{<package>} to the preamble before \\begin{document}."
    ),
    ErrorClass.MATH_MODE: (
        "Wrap math expressions in $...$ (inline) or \\[...\\] (display). "
        "Check for unescaped special characters: _ ^ & % #."
    ),
    ErrorClass.PACKAGE_ERROR: (
        "Check the package documentation for the specific error. "
        "Try updating the package or resolving option conflicts."
    ),
    ErrorClass.OVERFULL_HBOX: (
        "The text is too wide for the line width. Try: "
        "\\sloppy, \\emergencystretch, reducing font size, "
        "or rewording the paragraph."
    ),
    ErrorClass.UNDERFULL_HBOX: (
        "The line is too loose. Try \\raggedright, adjusting word spacing, "
        "or adding \\looseness=-1 to the paragraph."
    ),
    ErrorClass.INVALID_CHARACTER: (
        "The file contains a non-ASCII character not handled by inputenc. "
        "Use \\usepackage[utf8]{inputenc} or check file encoding."
    ),
    ErrorClass.MISSING_END: (
        "Check for matching \\begin{...} and \\end{...} environments. "
        "Count environment opens and closes."
    ),
    ErrorClass.DIMENSION_ERROR: (
        "A dimension value is missing or invalid. Check for typos in "
        "length specifications (e.g., \\textwidth, 10pt)."
    ),
    ErrorClass.NUMBER_ERROR: (
        "A numeric argument was expected but not found. Check for "
        "missing or malformed numeric values."
    ),
    ErrorClass.ALIGNMENT_ERROR: (
        "The & character must be inside a tabular, array, or matrix "
        "environment. Check environment boundaries."
    ),
    ErrorClass.FILE_NOT_FOUND: (
        "The referenced file does not exist. Check the filename and path. "
        "Ensure the file is in the same directory or in TEXINPUTS."
    ),
    ErrorClass.ENCODING_ERROR: (
        "The file contains bytes not valid in the declared encoding. "
        "Use \\usepackage[utf8]{inputenc} or re-save the file as UTF-8."
    ),
    ErrorClass.RUNAWAY: (
        "A macro argument was never closed. Check for matching braces "
        "and ensure no unescaped special characters in arguments."
    ),
    ErrorClass.GENERAL_ERROR: (
        "Review the error message above and check the surrounding code."
    ),
    ErrorClass.LATEX_ERROR: (
        "A core LaTeX error occurred. Check the specific error message "
        "and review the surrounding document structure."
    ),
    ErrorClass.PACKAGE_WARNING: (
        "This is a package warning, not an error. Review the message "
        "to determine if action is needed."
    ),
    ErrorClass.GENERAL_WARNING: (
        "This is a LaTeX warning. It typically does not prevent compilation "
        "but may indicate a formatting issue."
    ),
    ErrorClass.FONT_WARNING: (
        "A font size substitution occurred. The requested font size may "
        "not be available; LaTeX is using the nearest size."
    ),
    ErrorClass.CITATION_WARNING: (
        "A citation reference is undefined. Run biber/bibtex again, "
        "or check that the citation key exists in your .bib file."
    ),
    ErrorClass.CROSS_REFERENCE: (
        "A cross-reference is undefined. Run LaTeX again (usually 2-3 times) "
        "to resolve all references."
    ),
    ErrorClass.HYPHENATION: (
        "TeX ran out of memory. Reduce complexity, simplify macros, "
        "or split the document into smaller files."
    ),
}


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

def parse_latex_log(
    log_content: str,
    *,
    source_dir: Optional[Path] = None,
    include_warnings: bool = True,
    include_info: bool = False,
) -> list[Diagnostic]:
    """Parse a LaTeX log file into classified diagnostics.

    Args:
        log_content: Raw log file content.
        source_dir: Directory containing .tex files for line mapping.
        include_warnings: Include warning-level diagnostics.
        include_info: Include info-level diagnostics.

    Returns:
        List of Diagnostic objects sorted by log line number.
    """
    diagnostics: list[Diagnostic] = []
    lines = log_content.split("\n")
    i = 0
    pending_source: Optional[str] = None

    while i < len(lines):
        line = lines[i]
        log_line_num = i + 1

        # --- Source file hints (for line mapping) ---
        source_match = _RE_SOURCE_HINT.search(line)
        if source_match:
            pending_source = source_match.group(1)
            i += 1
            continue

        # --- LaTeX Error: "! LaTeX Error: <message>" (check before general !) ---
        m = _RE_LATEX_ERROR.match(line)
        if m:
            msg = m.group(1)
            error_class = ErrorClass.LATEX_ERROR
            # Check for file not found
            fnf = _RE_FILE_NOT_FOUND.match(line)
            if fnf:
                error_class = ErrorClass.FILE_NOT_FOUND
                msg = f"File '{fnf.group(1)}' not found"
            diag = Diagnostic(
                message=msg,
                severity=Severity.ERROR,
                error_class=error_class,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS.get(error_class),
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Package error: "! Package <pkg> Error: <message>" (check before general !) ---
        m = _RE_PACKAGE_ERROR.match(line)
        if m:
            pkg, msg = m.group(1), m.group(2)
            error_class = _classify_package_error(pkg, msg)
            diag = Diagnostic(
                message=f"[{pkg}] {msg}",
                severity=Severity.ERROR,
                error_class=error_class,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS.get(error_class),
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Undefined control sequence (check before general !) ---
        if _RE_UNDEFINED_CMD.match(line):
            cmd = ""
            # Look ahead for "<recently read> \command"
            if i + 1 < len(lines):
                rm = _RE_RECENTLY_READ.search(lines[i + 1])
                if rm:
                    cmd = rm.group(1)
            msg = f"Undefined command: {cmd}" if cmd else "Undefined control sequence"
            diag = Diagnostic(
                message=msg,
                severity=Severity.ERROR,
                error_class=ErrorClass.UNDEFINED_COMMAND,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.UNDEFINED_COMMAND],
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Missing $ inserted (check before general !) ---
        if _RE_MISSING_DOLLAR.match(line):
            diag = Diagnostic(
                message="Missing $ inserted (math mode required here)",
                severity=Severity.ERROR,
                error_class=ErrorClass.MATH_MODE,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.MATH_MODE],
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Missing brace (check before general !) ---
        m = _RE_MISSING_BRACE.match(line)
        if m:
            brace = m.group(1)
            diag = Diagnostic(
                message=f"Missing '{brace}' inserted",
                severity=Severity.ERROR,
                error_class=ErrorClass.MISSING_BRACE,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.MISSING_BRACE],
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Missing endgroup (check before general !) ---
        if _RE_MISSING_ENDGROUP.match(line):
            diag = Diagnostic(
                message="Missing \\endgroup inserted",
                severity=Severity.ERROR,
                error_class=ErrorClass.MISSING_END,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.MISSING_END],
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Missing endcsname (check before general !) ---
        if _RE_MISSING_ENDCSNAME.match(line):
            diag = Diagnostic(
                message="Missing \\endcsname inserted",
                severity=Severity.ERROR,
                error_class=ErrorClass.MISSING_END,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.MISSING_END],
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Invalid character (check before general !) ---
        if _RE_INVALID_CHAR.match(line):
            diag = Diagnostic(
                message="Text line contains an invalid character",
                severity=Severity.ERROR,
                error_class=ErrorClass.INVALID_CHARACTER,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.INVALID_CHARACTER],
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Dimension error (check before general !) ---
        if _RE_DIMENSION_ERROR.match(line):
            diag = Diagnostic(
                message="Illegal unit of measure",
                severity=Severity.ERROR,
                error_class=ErrorClass.DIMENSION_ERROR,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.DIMENSION_ERROR],
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Number error (check before general !) ---
        if _RE_NUMBER_ERROR.match(line):
            diag = Diagnostic(
                message="Missing number, treated as zero",
                severity=Severity.ERROR,
                error_class=ErrorClass.NUMBER_ERROR,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.NUMBER_ERROR],
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Alignment error ---
        if _RE_ALIGNMENT_ERROR.match(line):
            diag = Diagnostic(
                message="Misplaced alignment tab character &",
                severity=Severity.ERROR,
                error_class=ErrorClass.ALIGNMENT_ERROR,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.ALIGNMENT_ERROR],
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Runaway argument ---
        if _RE_RUNAWAY.match(line):
            diag = Diagnostic(
                message="Runaway argument (unclosed macro argument)",
                severity=Severity.ERROR,
                error_class=ErrorClass.RUNAWAY,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.RUNAWAY],
            )
            diagnostics.append(diag)
            i += 1
            continue

        # --- Encoding error ---
        if _RE_ENCODING_ERROR.match(line):
            diag = Diagnostic(
                message="Invalid UTF-8 byte sequence",
                severity=Severity.ERROR,
                error_class=ErrorClass.ENCODING_ERROR,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.ENCODING_ERROR],
            )
            diagnostics.append(diag)
            i += 1
            continue

        # --- General LaTeX error (fallback after specific checks): "! <message>." ---
        m = _RE_GENERAL_ERROR.match(line)
        if m:
            msg = m.group(1)
            error_class = _classify_general_error(msg)
            diag = Diagnostic(
                message=msg,
                severity=Severity.ERROR,
                error_class=error_class,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS.get(error_class),
            )
            _attach_line_number(diag, lines, i)
            diagnostics.append(diag)
            i += 1
            continue

        # --- Package warning ---
        if include_warnings:
            m = _RE_PACKAGE_WARNING.match(line)
            if m:
                pkg, msg = m.group(1), m.group(2)
                # Check if it's a citation warning
                if _RE_CITATION_WARNING.match(line):
                    error_class = ErrorClass.CITATION_WARNING
                else:
                    error_class = ErrorClass.PACKAGE_WARNING
                diag = Diagnostic(
                    message=f"[{pkg}] {msg}",
                    severity=Severity.WARNING,
                    error_class=error_class,
                    log_line=log_line_num,
                    source_file=pending_source,
                    raw=line,
                    suggestion=_FIX_SUGGESTIONS.get(error_class),
                )
                diagnostics.append(diag)
                i += 1
                continue

        # --- LaTeX warning ---
        if include_warnings:
            m = _RE_LATEX_WARNING.match(line)
            if m:
                msg = m.group(1)
                if _RE_CROSSREF_WARNING.match(line):
                    error_class = ErrorClass.CROSS_REFERENCE
                else:
                    error_class = ErrorClass.GENERAL_WARNING
                diag = Diagnostic(
                    message=msg,
                    severity=Severity.WARNING,
                    error_class=error_class,
                    log_line=log_line_num,
                    source_file=pending_source,
                    raw=line,
                    suggestion=_FIX_SUGGESTIONS.get(error_class),
                )
                diagnostics.append(diag)
                i += 1
                continue

        # --- Overfull hbox ---
        if include_warnings:
            m = _RE_OVERFULL_HBOX.match(line)
            if m:
                width, start, end = m.group(1), m.group(2), m.group(3)
                diag = Diagnostic(
                    message=f"Overfull \\hbox ({width} too wide) at lines {start}--{end}",
                    severity=Severity.WARNING,
                    error_class=ErrorClass.OVERFULL_HBOX,
                    log_line=log_line_num,
                    source_file=pending_source,
                    raw=line,
                    suggestion=_FIX_SUGGESTIONS[ErrorClass.OVERFULL_HBOX],
                )
                diagnostics.append(diag)
                i += 1
                continue

        # --- Underfull hbox ---
        if include_warnings:
            m = _RE_UNDERFULL_HBOX.match(line)
            if m:
                badness, start, end = m.group(1), m.group(2), m.group(3)
                diag = Diagnostic(
                    message=f"Underfull \\hbox (badness {badness}) at lines {start}--{end}",
                    severity=Severity.WARNING,
                    error_class=ErrorClass.UNDERFULL_HBOX,
                    log_line=log_line_num,
                    source_file=pending_source,
                    raw=line,
                    suggestion=_FIX_SUGGESTIONS[ErrorClass.UNDERFULL_HBOX],
                )
                diagnostics.append(diag)
                i += 1
                continue

        # --- Font warning ---
        if include_warnings and _RE_FONT_WARNING.match(line):
            diag = Diagnostic(
                message=line.strip(),
                severity=Severity.WARNING,
                error_class=ErrorClass.FONT_WARNING,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.FONT_WARNING],
            )
            diagnostics.append(diag)
            i += 1
            continue

        # --- TeX capacity exceeded ---
        if _RE_HYPHENATION.match(line):
            diag = Diagnostic(
                message=line.strip(),
                severity=Severity.ERROR,
                error_class=ErrorClass.HYPHENATION,
                log_line=log_line_num,
                source_file=pending_source,
                raw=line,
                suggestion=_FIX_SUGGESTIONS[ErrorClass.HYPHENATION],
            )
            diagnostics.append(diag)
            i += 1
            continue

        i += 1

    return diagnostics


def _classify_general_error(msg: str) -> ErrorClass:
    """Classify a general LaTeX error message."""
    msg_lower = msg.lower()
    if "undefined control sequence" in msg_lower:
        return ErrorClass.UNDEFINED_COMMAND
    if "missing" in msg_lower and ("inserted" in msg_lower):
        if "$" in msg:
            return ErrorClass.MATH_MODE
        if "}" in msg or "{" in msg:
            return ErrorClass.MISSING_BRACE
        if "endgroup" in msg_lower:
            return ErrorClass.MISSING_END
        if "endcsname" in msg_lower:
            return ErrorClass.MISSING_END
    if "runaway" in msg_lower:
        return ErrorClass.RUNAWAY
    if "invalid character" in msg_lower:
        return ErrorClass.INVALID_CHARACTER
    if "illegal unit" in msg_lower:
        return ErrorClass.DIMENSION_ERROR
    if "missing number" in msg_lower:
        return ErrorClass.NUMBER_ERROR
    if "misplaced" in msg_lower and "&" in msg:
        return ErrorClass.ALIGNMENT_ERROR
    if "too many" in msg_lower and "}" in msg:
        return ErrorClass.MISSING_BRACE
    return ErrorClass.GENERAL_ERROR


def _classify_package_error(pkg: str, msg: str) -> ErrorClass:
    """Classify a package error."""
    msg_lower = msg.lower()
    pkg_lower = pkg.lower()
    if pkg_lower == "inputenc" and "utf-8" in msg_lower:
        return ErrorClass.ENCODING_ERROR
    if pkg_lower == "hyperref" and "file not found" in msg_lower:
        return ErrorClass.FILE_NOT_FOUND
    if "undefined" in msg_lower:
        return ErrorClass.UNDEFINED_COMMAND
    return ErrorClass.PACKAGE_ERROR


def _attach_line_number(
    diag: Diagnostic, lines: list[str], error_line_idx: int
) -> None:
    """Try to extract a source line number from context around the error."""
    # Look at lines after the error for "l.<number>" hints
    for j in range(error_line_idx + 1, min(error_line_idx + 5, len(lines))):
        m = _RE_LINE_HINT.search(lines[j])
        if m:
            diag.source_line = int(m.group(1))
            return
        m = _RE_LINE_HINT2.search(lines[j])
        if m:
            diag.source_line = int(m.group(1))
            return

    # Look at the error line itself
    m = _RE_LINE_HINT.search(lines[error_line_idx])
    if m:
        diag.source_line = int(m.group(1))


def parse_build_output(
    output: str,
    *,
    include_warnings: bool = True,
) -> list[Diagnostic]:
    """Parse combined stdout+stderr from latexmk/lualatex.

    This is a convenience wrapper that handles both log file content
    and inline build output (which may be interleaved with log content).
    """
    return parse_latex_log(output, include_warnings=include_warnings)


def format_diagnostics(
    diagnostics: list[Diagnostic],
    *,
    use_color: bool = True,
    show_suggestions: bool = True,
    show_context: bool = True,
) -> str:
    """Format diagnostics for terminal output with optional ANSI colors.

    Args:
        diagnostics: List of Diagnostic objects.
        use_color: Enable ANSI color codes.
        show_suggestions: Include fix suggestions.
        show_context: Include source context.

    Returns:
        Formatted string ready for terminal display.
    """
    if not diagnostics:
        if use_color:
            return "\033[32mNo errors or warnings found.\033[0m"
        return "No errors or warnings found."

    parts: list[str] = []
    errors = [d for d in diagnostics if d.severity == Severity.ERROR]
    warnings = [d for d in diagnostics if d.severity == Severity.WARNING]

    # Summary header
    if use_color:
        parts.append(
            f"\033[1m\033[31m{len(errors)} error(s)\033[0m"
            f", \033[1m\033[33m{len(warnings)} warning(s)\033[0m"
        )
    else:
        parts.append(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    parts.append("")

    for diag in diagnostics:
        if diag.severity == Severity.ERROR:
            if use_color:
                prefix = "\033[31mERROR\033[0m"
            else:
                prefix = "ERROR"
        elif diag.severity == Severity.WARNING:
            if use_color:
                prefix = "\033[33mWARN\033[0m"
            else:
                prefix = "WARN"
        else:
            if use_color:
                prefix = "\033[36mINFO\033[0m"
            else:
                prefix = "INFO"

        location = ""
        if diag.source_file:
            location = f" in {diag.source_file}"
        if diag.source_line:
            location += f":{diag.source_line}"

        parts.append(f"  [{prefix}] {diag.message}{location}")

        if show_suggestions and diag.suggestion:
            if use_color:
                parts.append(f"         \033[32mHint: {diag.suggestion}\033[0m")
            else:
                parts.append(f"         Hint: {diag.suggestion}")

    return "\n".join(parts)
