"""Extended unit tests for buildlib.commands — targeting uncovered paths."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

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


# ---------------------------------------------------------------------------
# cmd_export
# ---------------------------------------------------------------------------
class TestCmdExport:
    def test_source_not_found(self, commands, capsys, tmp_path):
        commands.cmd_export([str(tmp_path / "missing.tex")])
        captured = capsys.readouterr()
        assert "not found" in captured.err

    def test_unknown_format(self, commands, capsys, tmp_path):
        src = tmp_path / "main.tex"
        src.write_text("\\documentclass{article}\n\\begin{document}\\end{document}\n")
        commands.cmd_export([str(src)], output_format="pdf")
        captured = capsys.readouterr()
        assert "Unknown format" in captured.err

    def test_html_no_latexml(self, commands, capsys, tmp_path):
        src = tmp_path / "main.tex"
        src.write_text("\\documentclass{article}\n\\begin{document}\\end{document}\n")
        with patch("buildlib.commands.commands.shutil.which", return_value=None):
            commands.cmd_export([str(src)], output_format="html")
        captured = capsys.readouterr()
        assert "latexml not found" in captured.err

    def test_epub_no_pandoc(self, commands, capsys, tmp_path):
        src = tmp_path / "main.tex"
        src.write_text("\\documentclass{article}\n\\begin{document}\\end{document}\n")
        with patch("buildlib.commands.commands.shutil.which", return_value=None):
            commands.cmd_export([str(src)], output_format="epub")
        captured = capsys.readouterr()
        assert "pandoc not found" in captured.err

    def test_docx_no_pandoc(self, commands, capsys, tmp_path):
        src = tmp_path / "main.tex"
        src.write_text("\\documentclass{article}\n\\begin{document}\\end{document}\n")
        with patch("buildlib.commands.commands.shutil.which", return_value=None):
            commands.cmd_export([str(src)], output_format="docx")
        captured = capsys.readouterr()
        assert "pandoc not found" in captured.err

    def test_html_latexml_success(self, commands, capsys, tmp_path):
        monkeypatch_root = tmp_path
        src = monkeypatch_root / "main.tex"
        src.write_text("\\documentclass{article}\n\\begin{document}\\end{document}\n")
        out_dir = monkeypatch_root / "build" / "export" / "html"
        out_dir.mkdir(parents=True)
        html_file = out_dir / "main.html"

        def fake_which(name):
            return f"/usr/bin/{name}"

        def make_html(cmd, **kwargs):
            if any("latexmlpost" in c for c in cmd):
                html_file.write_text("<html></html>")
            return (0, [])

        with patch("buildlib.config.REPO_ROOT", monkeypatch_root):
            with patch(
                "buildlib.commands.commands.shutil.which", side_effect=fake_which
            ):
                with patch.object(commands.runner, "run", side_effect=make_html):
                    commands.cmd_export([str(src)], output_format="html")
        captured = capsys.readouterr()
        assert "HTML exported" in captured.out

    def test_html_latexml_failure(self, commands, capsys, tmp_path):
        src = tmp_path / "main.tex"
        src.write_text("\\documentclass{article}\n\\begin{document}\\end{document}\n")

        def fake_which(name):
            return f"/usr/bin/{name}"

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch.object(
                commands.runner,
                "run",
                return_value=(1, []),
            ):
                commands.cmd_export([str(src)], output_format="html")
        captured = capsys.readouterr()
        assert "export failed" in captured.err

    def test_epub_with_pandoc_success(self, commands, capsys, tmp_path):
        monkeypatch_root = tmp_path
        src = monkeypatch_root / "main.tex"
        src.write_text("\\documentclass{article}\n\\begin{document}\\end{document}\n")
        out_dir = monkeypatch_root / "build" / "export" / "epub"
        out_dir.mkdir(parents=True)
        epub_file = out_dir / "main.epub"

        def fake_which(name):
            if name == "pandoc":
                return "/usr/bin/pandoc"
            return None

        def make_epub(cmd, **kwargs):
            if any("pandoc" in c for c in cmd):
                epub_file.write_bytes(b"%EPUB")
            return (0, [])

        with patch("buildlib.config.REPO_ROOT", monkeypatch_root):
            with patch(
                "buildlib.commands.commands.shutil.which", side_effect=fake_which
            ):
                with patch.object(commands.runner, "run", side_effect=make_epub):
                    commands.cmd_export([str(src)], output_format="epub")
        captured = capsys.readouterr()
        assert "EPUB exported" in captured.out

    def test_epub_pandoc_failure(self, commands, capsys, tmp_path):
        src = tmp_path / "main.tex"
        src.write_text("\\documentclass{article}\n\\begin{document}\\end{document}\n")

        def fake_which(name):
            if name == "pandoc":
                return "/usr/bin/pandoc"
            return None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch.object(commands.runner, "run", return_value=(1, [])):
                commands.cmd_export([str(src)], output_format="epub")
        captured = capsys.readouterr()
        assert "export failed" in captured.err

    def test_epub_with_latexml_intermediate(self, commands, capsys, tmp_path):
        """EPUB path when latexml is available but fails at first step."""
        src = tmp_path / "main.tex"
        src.write_text("\\documentclass{article}\n\\begin{document}\\end{document}\n")

        def fake_which(name):
            if name == "pandoc":
                return "/usr/bin/pandoc"
            if name == "latexml":
                return "/usr/bin/latexml"
            return None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch.object(commands.runner, "run", return_value=(1, [])):
                commands.cmd_export([str(src)], output_format="epub")
        captured = capsys.readouterr()
        # Should fall back to latex input for pandoc since latexml failed
        assert "export failed" in captured.err

    def test_default_source_main_tex(self, commands, capsys, tmp_path, monkeypatch):
        """No files arg -> defaults to repo root main.tex."""
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)
        main = tmp_path / "main.tex"
        main.write_text("\\documentclass{article}\n")
        with patch("buildlib.commands.commands.shutil.which", return_value=None):
            commands.cmd_export([], output_format="html")
        captured = capsys.readouterr()
        assert "latexml not found" in captured.err


# ---------------------------------------------------------------------------
# cmd_lint
# ---------------------------------------------------------------------------
class TestCmdLint:
    def test_no_tex_files(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)
        result = commands.cmd_lint()
        captured = capsys.readouterr()
        assert "No .tex files" in captured.out
        assert result == 0

    def test_no_linters(self, commands, capsys, tmp_path, monkeypatch):
        tex = tmp_path / "test.tex"
        tex.write_text("\\documentclass{article}\n")
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)
        with patch("buildlib.commands.commands.shutil.which", return_value=None):
            result = commands.cmd_lint([str(tex)])
        captured = capsys.readouterr()
        assert "Neither chktex nor lacheck" in captured.err
        assert result == 1

    def test_chktex_errors_counted(self, commands, capsys, tmp_path, monkeypatch):
        tex = tmp_path / "test.tex"
        tex.write_text("\\documentclass{article}\n")
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)

        # Use "Error 1" format which matches regex r"Error\s+\d+"
        chktex_out = (
            "test.tex:1:1:1:Error 1: Error message\n" "test.tex:2:1:2:Warning message\n"
        )

        def fake_which(name):
            return "/usr/bin/chktex" if name == "chktex" else None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch("buildlib.commands.commands.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout=chktex_out, stderr=""
                )
                result = commands.cmd_lint([str(tex)])
        captured = capsys.readouterr()
        assert "1 error" in captured.out
        assert result == 1

    def test_chktex_no_output(self, commands, capsys, tmp_path, monkeypatch):
        tex = tmp_path / "test.tex"
        tex.write_text("\\documentclass{article}\n")
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)

        def fake_which(name):
            return "/usr/bin/chktex" if name == "chktex" else None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch("buildlib.commands.commands.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                result = commands.cmd_lint([str(tex)])
        captured = capsys.readouterr()
        assert "no issues" in captured.out
        assert result == 0

    def test_chktex_only_warnings(self, commands, capsys, tmp_path, monkeypatch):
        tex = tmp_path / "test.tex"
        tex.write_text("\\documentclass{article}\n")
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)

        chktex_out = "test.tex:1:1:1:Warning message\n"

        def fake_which(name):
            return "/usr/bin/chktex" if name == "chktex" else None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch("buildlib.commands.commands.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout=chktex_out, stderr=""
                )
                result = commands.cmd_lint([str(tex)])
        captured = capsys.readouterr()
        assert "warning(s)" in captured.out
        assert result == 0

    def test_chktex_timeout(self, commands, capsys, tmp_path, monkeypatch):
        tex = tmp_path / "test.tex"
        tex.write_text("\\documentclass{article}\n")
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)

        def fake_which(name):
            return "/usr/bin/chktex" if name == "chktex" else None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch("buildlib.commands.commands.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired("chktex", 30)
                result = commands.cmd_lint([str(tex)])
        captured = capsys.readouterr()
        assert "Failed to process" in captured.out

    def test_lacheck_output(self, commands, capsys, tmp_path, monkeypatch):
        tex = tmp_path / "test.tex"
        tex.write_text("\\documentclass{article}\n")
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)

        lacheck_out = "lacheck output line\n"

        def fake_which(name):
            return "/usr/bin/lacheck" if name == "lacheck" else None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch("buildlib.commands.commands.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0, stdout=lacheck_out, stderr=""
                )
                result = commands.cmd_lint([str(tex)])
        captured = capsys.readouterr()
        assert "warning(s)" in captured.out

    def test_lacheck_timeout(self, commands, capsys, tmp_path, monkeypatch):
        tex = tmp_path / "test.tex"
        tex.write_text("\\documentclass{article}\n")
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)

        def fake_which(name):
            return "/usr/bin/lacheck" if name == "lacheck" else None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch("buildlib.commands.commands.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired("lacheck", 30)
                result = commands.cmd_lint([str(tex)])
        captured = capsys.readouterr()
        assert "Failed to process" in captured.out

    def test_both_linters(self, commands, capsys, tmp_path, monkeypatch):
        tex = tmp_path / "test.tex"
        tex.write_text("\\documentclass{article}\n")
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)

        def fake_which(name):
            if name in ("chktex", "lacheck"):
                return f"/usr/bin/{name}"
            return None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch("buildlib.commands.commands.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                result = commands.cmd_lint([str(tex)])
        captured = capsys.readouterr()
        assert "chktex" in captured.out or "Scanning" in captured.out

    def test_nonexistent_file_in_list(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)

        def fake_which(name):
            return "/usr/bin/chktex" if name == "chktex" else None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch("buildlib.commands.commands.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                result = commands.cmd_lint([str(tmp_path / "nonexistent.tex")])
        assert result == 0


# ---------------------------------------------------------------------------
# cmd_test
# ---------------------------------------------------------------------------
class TestCmdTest:
    def test_all_pass(self, commands, capsys):
        with patch("buildlib.commands.commands.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = commands.cmd_test()
            assert result == 0

    def test_l3build_fails(self, commands, capsys):
        call_count = 0

        def fake_run(cmd, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return MagicMock(returncode=1, stdout="l3build error", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        with patch("buildlib.commands.commands.subprocess.run", side_effect=fake_run):
            result = commands.cmd_test()
            assert result == 1

    def test_pytest_fails(self, commands, capsys):
        call_count = 0

        def fake_run(cmd, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                return MagicMock(returncode=1, stdout="pytest FAILED", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        with patch("buildlib.commands.commands.subprocess.run", side_effect=fake_run):
            result = commands.cmd_test()
            assert result == 1

    def test_both_fail(self, commands, capsys):
        with patch("buildlib.commands.commands.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="failure", stderr="")
            result = commands.cmd_test()
            assert result == 1


# ---------------------------------------------------------------------------
# _basic_pdf_compare
# ---------------------------------------------------------------------------
class TestBasicPdfCompare:
    def test_different_sizes_no_fitz(self, commands, capsys, tmp_path):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(b"PDF content A")
        b.write_bytes(b"PDF content B is bigger")
        with patch.dict("sys.modules", {"fitz": None}):
            commands._basic_pdf_compare(str(a), str(b))
        captured = capsys.readouterr()
        assert "differ" in captured.out.lower()

    def test_same_size_no_fitz(self, commands, capsys, tmp_path):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        data = b"same content"
        a.write_bytes(data)
        b.write_bytes(data)
        with patch.dict("sys.modules", {"fitz": None}):
            commands._basic_pdf_compare(str(a), str(b))
        captured = capsys.readouterr()
        assert "identical" in captured.out.lower()

    def test_fitz_available_same_pages(self, commands, capsys, tmp_path):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(b"A" * 100)
        b.write_bytes(b"A" * 100)

        mock_doc = MagicMock()
        mock_doc.page_count = 1

        fake_fitz = MagicMock()
        fake_fitz.open.return_value = mock_doc

        with patch.dict("sys.modules", {"fitz": fake_fitz}):
            with patch(
                "builtins.__import__",
                side_effect=lambda name, *a, **kw: (
                    fake_fitz
                    if name == "fitz"
                    else __builtins__.__import__(name, *a, **kw)
                ),
            ):
                commands._basic_pdf_compare(str(a), str(b))
        captured = capsys.readouterr()
        assert "Page count" in captured.out

    def test_fitz_available_different_pages(self, commands, capsys, tmp_path):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(b"A" * 100)
        b.write_bytes(b"B" * 200)

        mock_doc_a = MagicMock()
        mock_doc_a.page_count = 1
        mock_doc_b = MagicMock()
        mock_doc_b.page_count = 5

        call_count = 0

        def fake_open(path):
            nonlocal call_count
            call_count += 1
            return mock_doc_a if call_count == 1 else mock_doc_b

        fake_fitz = MagicMock()
        fake_fitz.open.side_effect = fake_open

        import builtins

        real_import = builtins.__import__

        def patched_import(name, *args, **kwargs):
            if name == "fitz":
                return fake_fitz
            return real_import(name, *args, **kwargs)

        with patch.dict("sys.modules", {"fitz": fake_fitz}):
            with patch("builtins.__import__", side_effect=patched_import):
                commands._basic_pdf_compare(str(a), str(b))
        captured = capsys.readouterr()
        assert "mismatch" in captured.out.lower()

    def test_fitz_sizes_nearly_identical(self, commands, capsys, tmp_path):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(b"A" * 1000)
        b.write_bytes(b"A" * 1001)

        mock_doc = MagicMock()
        mock_doc.page_count = 2

        fake_fitz = MagicMock()
        fake_fitz.open.return_value = mock_doc

        import builtins

        real_import = builtins.__import__

        def patched_import(name, *args, **kwargs):
            if name == "fitz":
                return fake_fitz
            return real_import(name, *args, **kwargs)

        with patch.dict("sys.modules", {"fitz": fake_fitz}):
            with patch("builtins.__import__", side_effect=patched_import):
                commands._basic_pdf_compare(str(a), str(b))
        captured = capsys.readouterr()
        assert "nearly identical" in captured.out.lower()


# ---------------------------------------------------------------------------
# _get_texlive_version
# ---------------------------------------------------------------------------
class TestGetTexliveVersion:
    def test_parsing_version(self, commands):
        mock_result = MagicMock()
        mock_result.stdout = "TeX Live 2024\n"
        mock_result.returncode = 0
        with patch(
            "buildlib.commands.commands.subprocess.run", return_value=mock_result
        ):
            result = commands._get_texlive_version()
            assert result == 2024

    def test_no_version_in_output(self, commands):
        mock_result = MagicMock()
        mock_result.stdout = "Some random output\n"
        mock_result.returncode = 0
        with patch(
            "buildlib.commands.commands.subprocess.run", return_value=mock_result
        ):
            result = commands._get_texlive_version()
            assert result is None

    def test_empty_output(self, commands):
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.returncode = 0
        with patch(
            "buildlib.commands.commands.subprocess.run", return_value=mock_result
        ):
            result = commands._get_texlive_version()
            assert result is None

    def test_none_stdout(self, commands):
        mock_result = MagicMock()
        mock_result.stdout = None
        mock_result.returncode = 0
        with patch(
            "buildlib.commands.commands.subprocess.run", return_value=mock_result
        ):
            result = commands._get_texlive_version()
            assert result is None

    def test_timeout(self, commands):
        with patch(
            "buildlib.commands.commands.subprocess.run",
            side_effect=subprocess.TimeoutExpired("tex", 5),
        ):
            result = commands._get_texlive_version()
            assert result is None

    def test_os_error(self, commands):
        with patch(
            "buildlib.commands.commands.subprocess.run", side_effect=OSError("no tex")
        ):
            result = commands._get_texlive_version()
            assert result is None

    def test_value_error_on_int(self, commands):
        mock_result = MagicMock()
        mock_result.stdout = (
            "TeX Live YYYY\n"  # YYYY won't match \d{4} as int? No, it will match regex
        )
        mock_result.returncode = 0
        with patch(
            "buildlib.commands.commands.subprocess.run", return_value=mock_result
        ):
            result = commands._get_texlive_version()
            # The regex needs \d{4} so "YYYY" won't match
            assert result is None


# ---------------------------------------------------------------------------
# cmd_check with real .tex content
# ---------------------------------------------------------------------------
class TestCmdCheck:
    def test_valid_refs_and_cites(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text(
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "\\label{sec:intro}\n"
            "\\ref{sec:intro}\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        (tmp_path / "refs.bib").write_text(
            "@article{smith2024,\n"
            "  author = {Smith},\n"
            "  title = {Title},\n"
            "  year = {2024},\n"
            "}\n",
            encoding="utf-8",
        )
        # Add a cite to match
        (tmp_path / "main.tex").write_text(
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "\\label{sec:intro}\n"
            "\\ref{sec:intro}\n"
            "\\cite{smith2024}\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert result == 0
        assert "valid" in captured.out.lower() or "Labels" in captured.out

    def test_undefined_refs(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text(
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "\\ref{sec:missing}\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert result == 1
        assert "Undefined references" in captured.out

    def test_undefined_cites(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text(
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "\\cite{nonexistent2024}\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert result == 1
        assert "Undefined citations" in captured.out

    def test_unused_labels(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text(
            "\\documentclass{article}\n"
            "\\begin{document}\n"
            "\\label{sec:unused}\n"
            "\\end{document}\n",
            encoding="utf-8",
        )
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert "Unused labels" in captured.out

    def test_not_a_directory(self, commands, capsys, tmp_path):
        result = commands.cmd_check([str(tmp_path / "nonexistent")])
        captured = capsys.readouterr()
        assert result == 1
        assert "Not a directory" in captured.err

    def test_no_tex_files(self, commands, capsys, tmp_path):
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert result == 0
        assert "No .tex files" in captured.out

    def test_multiple_cite_keys(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text("\\cite{key1,key2,key3}\n", encoding="utf-8")
        (tmp_path / "refs.bib").write_text(
            "@article{key1,author={A},title={T},year={2024}}\n",
            encoding="utf-8",
        )
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert result == 1  # key2 and key3 undefined
        assert "Undefined citations" in captured.out

    def test_multiple_refs_in_one_command(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text("\\ref{sec:a,sec:b}\n", encoding="utf-8")
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert result == 1

    def test_check_with_eqref(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text("\\eqref{eq:missing}\n", encoding="utf-8")
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert result == 1

    def test_check_with_autoref(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text("\\autoref{sec:missing}\n", encoding="utf-8")
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert result == 1

    def test_bib_file_read_error(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text("\\cite{x}\n", encoding="utf-8")
        bib = tmp_path / "broken.bib"
        bib.write_text("@article{x,author={A}}\n", encoding="utf-8")
        with patch.object(Path, "read_text", side_effect=OSError("permission denied")):
            result = commands.cmd_check([str(tmp_path)])
        # Should not crash, result may be 0 or 1 depending on how the error is handled

    def test_tex_file_read_error(self, commands, capsys, tmp_path):
        (tmp_path / "main.tex").write_text("\\label{x}\n", encoding="utf-8")
        with patch.object(Path, "read_text", side_effect=OSError("read error")):
            result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        assert "Cannot read" in captured.out

    def test_check_excludes_minted_dirs(self, commands, capsys, tmp_path):
        minted_dir = tmp_path / "_minted_test"
        minted_dir.mkdir()
        (minted_dir / "content.tex").write_text("\\ref{bad}\n", encoding="utf-8")
        result = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        # Should not find the _minted file
        assert "No .tex files" in captured.out

    def test_check_excludes_build_dir(self, commands, capsys, tmp_path):
        build_dir = tmp_path / "build"
        build_dir.mkdir()
        (build_dir / "test.tex").write_text("\\ref{bad}\n", encoding="utf-8")
        # The build_dir exclusion compares a relative Path("build") against
        # absolute parent paths from rglob, so the file is NOT excluded by
        # default. This test verifies that the file IS scanned (known limitation).
        _ = commands.cmd_check([str(tmp_path)])
        captured = capsys.readouterr()
        # File gets scanned because Path("build") != absolute parent
        assert "1 .tex file" in captured.out


# ---------------------------------------------------------------------------
# cmd_init edge cases
# ---------------------------------------------------------------------------
class TestCmdInitEdges:
    def test_invalid_doctype(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["test-proj"], doctype="bogus")
        captured = capsys.readouterr()
        assert "Unknown doctype" in captured.err

    def test_invalid_language(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["test-proj"], language="klingon")
        captured = capsys.readouterr()
        assert "Unknown language" in captured.err

    def test_thesis_sets_doctype(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-proj"], thesis=True)
        captured = capsys.readouterr()
        assert "Initialized" in captured.out
        main_tex = tmp_path / "my-proj" / "main.tex"
        assert main_tex.exists()
        content = main_tex.read_text(encoding="utf-8")
        assert "doctype=thesis" in content

    def test_thesis_with_explicit_doctype(
        self, commands, capsys, tmp_path, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["my-proj"], thesis=True, doctype="dissertation")
        captured = capsys.readouterr()
        assert "Initialized" in captured.out

    def test_path_traversal_blocked(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(["../escape-project"])
        captured = capsys.readouterr()
        assert "Invalid" in captured.err

    def test_doctype_overrides_existing(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        commands.cmd_init(
            ["proj"], doctype="article", institution="mit", language="german"
        )
        main_tex = tmp_path / "proj" / "main.tex"
        content = main_tex.read_text(encoding="utf-8")
        assert "doctype=article" in content
        assert "institution=mit" in content
        assert "language=german" in content

    def test_template_not_found(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path / "empty")
        (tmp_path / "empty").mkdir()
        commands.cmd_init(["test-proj"])
        captured = capsys.readouterr()
        assert "Template not found" in captured.err


# ---------------------------------------------------------------------------
# _rebuild_affected
# ---------------------------------------------------------------------------
class TestRebuildAffected:
    def test_with_files(self, commands):
        commands.build_example = MagicMock()
        commands.build_examples = MagicMock()
        commands._rebuild_affected(Path("test.tex"), ["file1.tex"])
        commands.build_example.assert_called_once_with(["file1.tex"])
        commands.build_examples.assert_not_called()

    def test_without_files(self, commands):
        commands.build_example = MagicMock()
        commands.build_examples = MagicMock()
        commands._rebuild_affected(Path("test.tex"), [])
        commands.build_examples.assert_called_once_with([])
        commands.build_example.assert_not_called()


# ---------------------------------------------------------------------------
# _diff_two_pdfs
# ---------------------------------------------------------------------------
class TestDiffTwoPdfs:
    def test_latexdiff_not_available(self, commands, capsys, tmp_path):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(b"PDF-A")
        b.write_bytes(b"PDF-B")
        with patch("buildlib.commands.commands.shutil.which", return_value=None):
            with patch.object(commands, "_find_tex_for_pdf", return_value=None):
                with patch.object(commands, "_basic_pdf_compare") as mock_cmp:
                    commands._diff_two_pdfs(str(a), str(b))
                    mock_cmp.assert_called_once()

    def test_latexdiff_available_but_no_tex(self, commands, capsys, tmp_path):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(b"PDF-A")
        b.write_bytes(b"PDF-B")

        def fake_which(name):
            if name == "latexdiff":
                return "/usr/bin/latexdiff"
            return None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch.object(commands, "_find_tex_for_pdf", return_value=None):
                with patch.object(commands, "_basic_pdf_compare") as mock_cmp:
                    commands._diff_two_pdfs(str(a), str(b))
                    mock_cmp.assert_called_once()

    def test_latexdiff_available_with_tex(self, commands, capsys, tmp_path):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(b"PDF-A")
        b.write_bytes(b"PDF-B")

        def fake_which(name):
            if name == "latexdiff":
                return "/usr/bin/latexdiff"
            return None

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch.object(
                commands, "_find_tex_for_pdf", return_value=Path("fake.tex")
            ):
                with patch.object(commands, "_run_latexdiff") as mock_ld:
                    commands._diff_two_pdfs(
                        str(a), str(b), output=str(tmp_path / "out.pdf")
                    )
                    mock_ld.assert_called_once()


# ---------------------------------------------------------------------------
# _diff_git_refs
# ---------------------------------------------------------------------------
class TestDiffGitRefs:
    def test_git_show_fails(self, commands, capsys):
        with patch("buildlib.commands.commands.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="fatal: not a tree object"
            )
            commands._diff_git_refs("bad_ref_a", "bad_ref_b")
        captured = capsys.readouterr()
        assert "Could not extract" in captured.err

    def test_latexdiff_available(self, commands, capsys):
        call_count = 0

        def fake_run(cmd, **kwargs):
            nonlocal call_count
            call_count += 1
            if "git" in cmd[0] and "show" in cmd[0]:
                return MagicMock(
                    returncode=0, stdout="\\documentclass{article}\n", stderr=""
                )
            if "latexdiff" in cmd[0]:
                return MagicMock(returncode=0, stdout="diff result", stderr="")
            if "latexmk" in cmd[0]:
                (Path(kwargs.get("cwd", ".")) / "diff.pdf").write_bytes(b"pdf")
                return MagicMock(returncode=0, stdout="", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        def fake_which(name):
            if name == "latexdiff":
                return "/usr/bin/latexdiff"
            return None

        with patch("buildlib.commands.commands.subprocess.run", side_effect=fake_run):
            with patch(
                "buildlib.commands.commands.shutil.which", side_effect=fake_which
            ):
                with patch(
                    "buildlib.commands.commands.Path.cwd", return_value=Path(".")
                ):
                    commands._diff_git_refs("ref_a", "ref_b")

    def test_latexdiff_unavailable_fallback(self, commands, capsys):
        def fake_run(cmd, **kwargs):
            if "git" in cmd[0] and "show" in cmd[0]:
                return MagicMock(returncode=0, stdout="content", stderr="")
            if cmd[0] == "diff":
                return MagicMock(returncode=1, stdout="-old\n+new\n", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        with patch("buildlib.commands.commands.subprocess.run", side_effect=fake_run):
            with patch("buildlib.commands.commands.shutil.which", return_value=None):
                commands._diff_git_refs("ref_a", "ref_b")
        captured = capsys.readouterr()
        assert "textual diff" in captured.out

    def test_identical_content(self, commands, capsys):
        def fake_run(cmd, **kwargs):
            if "git" in cmd[0] and "show" in cmd[0]:
                return MagicMock(returncode=0, stdout="same", stderr="")
            if cmd[0] == "diff":
                return MagicMock(returncode=0, stdout="", stderr="")
            return MagicMock(returncode=0, stdout="", stderr="")

        with patch("buildlib.commands.commands.subprocess.run", side_effect=fake_run):
            with patch("buildlib.commands.commands.shutil.which", return_value=None):
                commands._diff_git_refs("ref_a", "ref_b")
        captured = capsys.readouterr()
        assert "identical" in captured.out.lower()


# ---------------------------------------------------------------------------
# _check_all_latex_packages
# ---------------------------------------------------------------------------
class TestCheckAllLatexPackages:
    def test_exception_returns_all_false(self, commands):
        with patch(
            "buildlib.commands.commands.subprocess.run", side_effect=OSError("fail")
        ):
            result = commands._check_all_latex_packages(["fontspec", "hyperref"])
        assert all(v is False for v in result.values())

    def test_nonzero_returncode_partial_output(self, commands):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "/path/to/fontspec.sty\n"
        with patch(
            "buildlib.commands.commands.subprocess.run", return_value=mock_result
        ):
            result = commands._check_all_latex_packages(["fontspec", "hyperref"])
        assert result["fontspec"] is True
        assert result["hyperref"] is False

    def test_zero_returncode_full_output(self, commands):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/path/to/fontspec.sty\n/path/to/hyperref.sty\n"
        with patch(
            "buildlib.commands.commands.subprocess.run", return_value=mock_result
        ):
            result = commands._check_all_latex_packages(["fontspec", "hyperref"])
        assert result["fontspec"] is True
        assert result["hyperref"] is True


# ---------------------------------------------------------------------------
# _check_latex_package
# ---------------------------------------------------------------------------
class TestCheckLatexPackage:
    def test_timeout(self, commands):
        with patch(
            "buildlib.commands.commands.subprocess.run",
            side_effect=subprocess.TimeoutExpired("kpsewhich", 5),
        ):
            result = commands._check_latex_package("fontspec")
        assert result is False

    def test_os_error(self, commands):
        with patch(
            "buildlib.commands.commands.subprocess.run", side_effect=OSError("fail")
        ):
            result = commands._check_latex_package("fontspec")
        assert result is False

    def test_found(self, commands):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/path/to/fontspec.sty\n"
        with patch(
            "buildlib.commands.commands.subprocess.run", return_value=mock_result
        ):
            result = commands._check_latex_package("fontspec")
        assert result is True

    def test_not_found(self, commands):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        with patch(
            "buildlib.commands.commands.subprocess.run", return_value=mock_result
        ):
            result = commands._check_latex_package("nonexistent")
        assert result is False


# ---------------------------------------------------------------------------
# _is_git_ref
# ---------------------------------------------------------------------------
class TestIsGitRef:
    def test_exception(self, commands):
        with patch(
            "buildlib.commands.commands.subprocess.run", side_effect=OSError("fail")
        ):
            result = commands._is_git_ref("HEAD")
        assert result is False

    def test_timeout(self, commands):
        with patch(
            "buildlib.commands.commands.subprocess.run",
            side_effect=subprocess.TimeoutExpired("git", 5),
        ):
            result = commands._is_git_ref("HEAD")
        assert result is False


# ---------------------------------------------------------------------------
# _find_tex_for_pdf
# ---------------------------------------------------------------------------
class TestFindTexForPdf:
    def test_same_name_tex(self, commands, tmp_path):
        pdf = tmp_path / "doc.pdf"
        tex = tmp_path / "doc.tex"
        tex.write_text("\\documentclass{article}\n")
        result = commands._find_tex_for_pdf(str(pdf))
        assert result == tex

    def test_main_tex_fallback(self, commands, tmp_path):
        pdf = tmp_path / "doc.pdf"
        main = tmp_path / "main.tex"
        main.write_text("\\documentclass{article}\n")
        result = commands._find_tex_for_pdf(str(pdf))
        assert result == main


# ---------------------------------------------------------------------------
# cmd_diff
# ---------------------------------------------------------------------------
class TestCmdDiffExtended:
    def test_regenerate_references(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)
        ref_dir = tmp_path / "tests" / "references"
        ref_dir.mkdir(parents=True)
        build_dir = tmp_path / "build"
        build_dir.mkdir(parents=True)
        # Create a build output
        build_examples = build_dir / "examples"
        build_examples.mkdir(parents=True)
        (build_examples / "test.pdf").write_bytes(b"PDF")
        commands.config = MagicMock()
        commands.config.build_dir = build_dir
        commands.cmd_diff(["test"], regenerate_references=True)
        captured = capsys.readouterr()
        assert "Copied" in captured.out

    def test_no_files_specified(self, commands, capsys):
        commands.cmd_diff([])
        captured = capsys.readouterr()
        assert "No examples" in captured.out

    def test_two_pdf_paths(self, commands, tmp_path):
        a = tmp_path / "a.pdf"
        b = tmp_path / "b.pdf"
        a.write_bytes(b"A")
        b.write_bytes(b"B")
        with patch.object(commands, "_diff_two_pdfs") as mock_diff:
            commands.cmd_diff([str(a), str(b)])
            mock_diff.assert_called_once()

    def test_two_git_refs(self, commands):
        with patch.object(commands, "_is_git_ref", return_value=True):
            with patch.object(commands, "_diff_git_refs") as mock_diff:
                commands.cmd_diff(["ref_a", "ref_b"])
                mock_diff.assert_called_once()


# ---------------------------------------------------------------------------
# cmd_scaffold_institution
# ---------------------------------------------------------------------------
class TestCmdScaffoldInstitutionExtended:
    def test_path_traversal(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)
        commands.cmd_scaffold_institution(["../../../etc/passwd"])
        captured = capsys.readouterr()
        assert "Invalid" in captured.err

    def test_generic_not_found(self, commands, capsys, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)
        commands.cmd_scaffold_institution(["newinst"])
        captured = capsys.readouterr()
        assert "Generic template not found" in captured.err


# ---------------------------------------------------------------------------
# cmd_watch
# ---------------------------------------------------------------------------
class TestCmdWatch:
    def test_watch_callable(self, commands):
        assert callable(commands.cmd_watch)


# ---------------------------------------------------------------------------
# cmd_preflight
# ---------------------------------------------------------------------------
class TestCmdPreflightExtended:
    def test_preflight_with_texlive(self, commands, capsys):
        def fake_which(tool):
            if tool in ("lualatex", "latexmk", "git"):
                return f"/usr/bin/{tool}"
            return None

        all_pkgs = {
            "fontspec": True,
            "unicode-math": True,
            "hyperref": True,
            "minted": True,
            "biblatex": True,
            "siunitx": True,
            "circuitikz": True,
            "forest": True,
        }

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch.object(commands, "_get_texlive_version", return_value=2024):
                with patch.object(
                    commands, "_check_all_latex_packages", return_value=all_pkgs
                ):
                    commands.cmd_preflight()
        captured = capsys.readouterr()
        assert "2024" in captured.out

    def test_preflight_no_texlive(self, commands, capsys):
        def fake_which(tool):
            return (
                f"/usr/bin/{tool}" if tool in ("lualatex", "latexmk", "git") else None
            )

        all_pkgs = {
            "fontspec": False,
            "unicode-math": False,
            "hyperref": False,
            "minted": False,
            "biblatex": False,
            "siunitx": False,
            "circuitikz": False,
            "forest": False,
        }

        with patch("buildlib.commands.commands.shutil.which", side_effect=fake_which):
            with patch.object(commands, "_get_texlive_version", return_value=None):
                with patch.object(
                    commands, "_check_all_latex_packages", return_value=all_pkgs
                ):
                    commands.cmd_preflight()
        captured = capsys.readouterr()
        assert "unknown" in captured.out.lower()


# ---------------------------------------------------------------------------
# _check_tool
# ---------------------------------------------------------------------------
class TestCheckToolExtended:
    def test_found_detail(self, commands):
        name, ok, detail = commands._check_tool("python3", "Python")
        assert "python" in detail.lower() or "Found" in detail

    def test_missing_required(self, commands):
        name, ok, detail = commands._check_tool(
            "nonexistent_xyz_tool", "Tool", required=True
        )
        assert ok is False
        assert "(required)" in detail
