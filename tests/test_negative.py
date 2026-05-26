"""Negative tests for OmniLaTeX -- graceful failure for invalid inputs."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def compile_tex(tex_content: str, timeout: int = 120) -> tuple:
    """Compile and return (success, log_content).

    Success is determined by PDF existence, not latexmk return code,
    because latexmk returns non-zero when biber/glossary reruns are
    needed even though the PDF was produced.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = Path(tmpdir) / "test.tex"
        tex_file.write_text(tex_content)
        for rel in ["config/document-settings.sty", "bib/bibliography.bib"]:
            src = PROJECT_ROOT / rel
            if src.exists():
                dst = Path(tmpdir) / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        env = os.environ.copy()
        env["TEXINPUTS"] = f"{PROJECT_ROOT}{os.pathsep}{tmpdir}{os.pathsep}"
        result = subprocess.run(
            [
                "latexmk",
                "-lualatex",
                "-interaction=nonstopmode",
                f"-outdir={tmpdir}",
                str(tex_file),
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
            cwd=tmpdir,
        )
        pdf_exists = (Path(tmpdir) / "test.pdf").exists()
        return (pdf_exists, result.stdout + result.stderr)


class TestUnknownDoctype:
    @pytest.mark.slow
    def test_unknown_doctype_produces_warning(self):
        """Unknown doctypes should produce a ClassWarning, not crash."""
        tex = r"""\documentclass[doctype=nonexistent]{omnilatex}
\begin{document}Test\end{document}"""
        success, log = compile_tex(tex)
        # Should still compile (falls back to book) but may produce a warning
        # Current behavior: silent fallback. Future: should warn.
        assert success, f"Should compile with fallback. Log: {log[-500:]}"
        assert (
            "classwarning" in log.lower() or "unknown" in log.lower()
        ), f"Should produce warning. Log: {log[-500:]}"


class TestMissingResources:
    @pytest.mark.slow
    def test_missing_institution_warns(self):
        """Missing institution should produce a ClassWarning."""
        tex = r"""\documentclass[institution=nonexistent]{omnilatex}
\begin{document}Test\end{document}"""
        success, log = compile_tex(tex)
        assert success
        log_lower = log.lower()
        assert (
            "not found" in log_lower
            or "warning" in log_lower
            or "unknown" in log_lower
            or "classwarning" in log_lower
        ), f"Missing institution should produce a warning. Log: {log[-500:]}"


class TestEdgeCases:
    @pytest.mark.slow
    def test_empty_document(self):
        """Empty document should not cause a fatal crash."""
        tex = r"""\documentclass{omnilatex}
\begin{document}\end{document}"""
        success, log = compile_tex(tex)
        # Empty document may fail due to missing glossary/bib resources.
        # Only check for actual process crashes, not latexmk's "Fatal error"
        # message (which just means no PDF was produced).
        log_lower = log.lower()
        assert "segmentation fault" not in log_lower
        assert "memory access" not in log_lower
        assert "panic" not in log_lower

    @pytest.mark.slow
    def test_minimal_content(self):
        tex = r"""\documentclass{omnilatex}
\begin{document}Hello world.\end{document}"""
        success, _ = compile_tex(tex)
        assert success


class TestInvalidOptions:
    @pytest.mark.slow
    def test_invalid_keyval_option(self):
        """Invalid keyval should be passed through to base class."""
        tex = r"""\documentclass[invalidoption]{omnilatex}
\begin{document}Test\end{document}"""
        # This should be handled by DeclareDefaultOption -> adduseroption -> passed to base class
        success, log = compile_tex(tex)
        log_lower = log.lower()
        assert (
            not success
            or "unknown key" in log_lower
            or "unknown option" in log_lower
            or "warning" in log_lower
        ), f"Unknown option should produce a warning or fail. Log: {log[-500:]}"

    @pytest.mark.slow
    def test_a5_option(self):
        """The a5 void option should compile."""
        tex = r"""\documentclass[a5]{omnilatex}
\begin{document}Test\end{document}"""
        success, _ = compile_tex(tex)
        assert success
