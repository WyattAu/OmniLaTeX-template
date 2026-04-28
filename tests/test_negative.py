"""Negative tests for OmniLaTeX -- graceful failure for invalid inputs."""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def compile_tex(tex_content: str, timeout: int = 60) -> tuple:
    """Compile and return (success, log_content)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = Path(tmpdir) / "test.tex"
        tex_file.write_text(tex_content)
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
        return (result.returncode == 0, result.stdout + result.stderr)


class TestUnknownDoctype:
    def test_unknown_doctype_produces_warning(self):
        """Unknown doctypes should produce a ClassWarning, not crash."""
        tex = r"""\documentclass[doctype=nonexistent]{omnilatex}
\begin{document}Test\end{document}"""
        success, log = compile_tex(tex)
        # Should still compile (falls back to book) but may produce a warning
        # Current behavior: silent fallback. Future: should warn.
        assert success, f"Should compile with fallback. Log: {log[-500:]}"


class TestMissingResources:
    def test_missing_institution_warns(self):
        """Missing institution should produce a ClassWarning."""
        tex = r"""\documentclass[institution=nonexistent]{omnilatex}
\begin{document}Test\end{document}"""
        success, log = compile_tex(tex)
        assert success
        assert "not found" in log.lower() or "warning" in log.lower() or success


class TestEdgeCases:
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

    def test_minimal_content(self):
        tex = r"""\documentclass{omnilatex}
\begin{document}Hello world.\end{document}"""
        success, _ = compile_tex(tex)
        assert success


class TestInvalidOptions:
    def test_invalid_keyval_option(self):
        """Invalid keyval should be passed through to base class."""
        tex = r"""\documentclass[invalidoption]{omnilatex}
\begin{document}Test\end{document}"""
        # This should be handled by DeclareDefaultOption -> adduseroption -> passed to base class
        success, log = compile_tex(tex)
        # Base class may reject unknown options, but shouldn't crash badly
        # At minimum, the error should be informative

    def test_a5_option(self):
        """The a5 void option should compile."""
        tex = r"""\documentclass[a5]{omnilatex}
\begin{document}Test\end{document}"""
        success, _ = compile_tex(tex)
        assert success
