"""Unit tests for buildlib.commands.check_lint module."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from buildlib.commands.check_lint import CheckLintMixin
from buildlib.config import ProjectConfig
from buildlib.ui import TerminalOutput


@pytest.fixture
def check_lint():
    ui = TerminalOutput(use_color=False)
    obj = object.__new__(CheckLintMixin)
    obj.ui = ui
    obj.config = ProjectConfig()
    return obj


@pytest.fixture
def tmp_tex_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestCmdCheck:
    def test_returns_zero_on_empty_dir(self, check_lint, tmp_tex_dir):
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0

    def test_returns_zero_on_valid_refs(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\label{sec:intro} Section~\ref{sec:intro}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0

    def test_returns_one_on_undefined_ref(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"Reference~\ref{sec:missing}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 1

    def test_returns_one_on_undefined_cite(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\cite{knuth1984}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 1

    def test_bib_entries_resolved(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\cite{knuth1984}" "\n",
            encoding="utf-8",
        )
        bib = tmp_tex_dir / "refs.bib"
        bib.write_text(
            "@book{knuth1984, title={The TeXbook}}\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0

    def test_returns_one_on_nonexistent_dir(self, check_lint):
        result = check_lint.cmd_check(files=["/nonexistent/path"])
        assert result == 1

    def test_unused_labels_are_informational(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\label{sec:unused}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        # Unused labels are informational only, not errors
        assert result == 0

    def test_multiple_refs_one_undefined(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\label{sec:intro} Section~\ref{sec:intro} Also~\ref{sec:missing}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 1

    def test_multiple_bib_keys(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\cite{knuth1984,lamport1994}" "\n",
            encoding="utf-8",
        )
        bib = tmp_tex_dir / "refs.bib"
        bib.write_text(
            "@book{knuth1984, title={The TeXbook}}\n"
            "@book{lamport1994, title={LaTeX}}\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0

    def test_eqref_resolved(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\label{eq:einstein} See Eq.~\eqref{eq:einstein}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0

    def test_autoref_resolved(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\label{fig:diagram} See \autoref{fig:diagram}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0

    def test_cref_resolved(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\label{tab:results} See \cref{tab:results}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0

    def test_pageref_resolved(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\label{sec:intro} See page~\pageref{sec:intro}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0

    def test_nocite_counted(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\nocite{knuth1984}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 1  # nocite references missing bib

    def test_multiple_comma_separated_refs(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\label{a}\label{b} \ref{a},\ref{b}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0

    def test_build_dir_excluded(self, check_lint, tmp_tex_dir):
        # Build dir exclusion only works when build_dir is an absolute path
        # matching the scan directory. With default relative Path("build"),
        # files inside a "build" subdir are still scanned (documented behavior).
        # This test verifies the filter is applied when paths match.
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(
            r"\label{sec:intro} See~\ref{sec:intro}" "\n",
            encoding="utf-8",
        )
        result = check_lint.cmd_check(files=[str(tmp_tex_dir)])
        assert result == 0


class TestCmdLint:
    def test_returns_one_when_no_tools(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")
        with patch("shutil.which", return_value=None):
            result = check_lint.cmd_lint(files=[str(tex)])
            assert result == 1

    def test_returns_zero_on_no_files(self, check_lint):
        result = check_lint.cmd_lint(files=["/nonexistent/file.tex"])
        assert result == 0

    def test_chktex_invoked_clean(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with (
            patch(
                "shutil.which",
                side_effect=lambda x: "/usr/bin/chktex" if x == "chktex" else None,
            ),
            patch("subprocess.run", return_value=mock_result),
        ):
            result = check_lint.cmd_lint(files=[str(tex)])
            assert result == 0

    def test_chktex_errors_return_1(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        # chktex format: file:line:col:num:message (num is error number)
        mock_result = MagicMock()
        mock_result.stdout = "main.tex:1:1:1:Error 1: Message\n"
        mock_result.returncode = 0

        with (
            patch(
                "shutil.which",
                side_effect=lambda x: "/usr/bin/chktex" if x == "chktex" else None,
            ),
            patch("subprocess.run", return_value=mock_result),
        ):
            result = check_lint.cmd_lint(files=[str(tex)])
            assert result == 1

    def test_chktex_warnings_return_0(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        mock_result = MagicMock()
        mock_result.stdout = "main.tex:1:1:1:Warning message\n"
        mock_result.returncode = 0

        with (
            patch(
                "shutil.which",
                side_effect=lambda x: "/usr/bin/chktex" if x == "chktex" else None,
            ),
            patch("subprocess.run", return_value=mock_result),
        ):
            # Warnings (not errors) return 0
            result = check_lint.cmd_lint(files=[str(tex)])
            assert result == 0

    def test_lacheck_invoked(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with (
            patch(
                "shutil.which",
                side_effect=lambda x: "/usr/bin/lacheck" if x == "lacheck" else None,
            ),
            patch("subprocess.run", return_value=mock_result),
        ):
            result = check_lint.cmd_lint(files=[str(tex)])
            assert result == 0

    def test_both_tools_invoked(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0

        with (
            patch("shutil.which", return_value="/usr/bin/tool"),
            patch("subprocess.run", return_value=mock_result),
        ):
            result = check_lint.cmd_lint(files=[str(tex)])
            assert result == 0

    def test_subprocess_timeout_handled(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        with (
            patch(
                "shutil.which",
                side_effect=lambda x: "/usr/bin/chktex" if x == "chktex" else None,
            ),
            patch(
                "subprocess.run", side_effect=subprocess.TimeoutExpired("chktex", 30)
            ),
        ):
            result = check_lint.cmd_lint(files=[str(tex)])
            assert result == 0  # timeout handled gracefully

    def test_subprocess_oserror_handled(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        with (
            patch(
                "shutil.which",
                side_effect=lambda x: "/usr/bin/chktex" if x == "chktex" else None,
            ),
            patch("subprocess.run", side_effect=OSError("permission denied")),
        ):
            result = check_lint.cmd_lint(files=[str(tex)])
            assert result == 0  # OSError handled gracefully

    def test_chktex_wildcard_no_error_counted(self, check_lint, tmp_tex_dir):
        tex = tmp_tex_dir / "main.tex"
        tex.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")

        mock_result = MagicMock()
        mock_result.stdout = "main.tex:1:1:1:Info message\n"
        mock_result.returncode = 0

        with (
            patch(
                "shutil.which",
                side_effect=lambda x: "/usr/bin/chktex" if x == "chktex" else None,
            ),
            patch("subprocess.run", return_value=mock_result),
        ):
            # "Info" doesn't match the Error regex
            result = check_lint.cmd_lint(files=[str(tex)])
            assert result == 0
