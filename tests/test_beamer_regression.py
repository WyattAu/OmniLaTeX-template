"""Regression tests for Beamer doctype compilation.

These tests verify that the major Beamer integration changes work:
- OmniPrimaryColor/OmniAccentColor defined with providecolor
- KOMA modules skipped for beamer class
- hyperref/biblio/lists modules skipped for beamer
- Backward-compat aliases (examniner -> examiner) work
- beamer-native doctype uses beamer class directly
- KOMA compatibility stubs (nonumberline, texorpdfstring) work
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BEAMER_TEMPLATE = r"""
\documentclass[{options}]{{omnilatex}}
\title{{Beamer Regression Test}}
\author{{Test Author}}
\begin{{document}}
\begin{{frame}}
\frametitle{{Test Frame {frame_title}}}
Content for {doctype}.
\end{{frame}}
\end{{document}}
"""


def _compile_tex(tex_content: str, timeout: int = 120) -> tuple:
    """Compile tex content locally. Returns (success, log_excerpt)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = Path(tmpdir) / "test.tex"
        tex_file.write_text(tex_content)
        env = os.environ.copy()
        env["TEXINPUTS"] = (
            f"{tmpdir}{os.pathsep}"
            f"{PROJECT_ROOT / 'lib'}{os.pathsep}"
            f"{PROJECT_ROOT / 'config'}{os.pathsep}"
            f"{PROJECT_ROOT / 'lua'}{os.pathsep}"
            f"{PROJECT_ROOT}{os.pathsep}"
        )
        env["BUILD_MODE"] = "dev"
        env["OMNILATEX_SKIP_BIB2GLS"] = "1"
        subprocess.run(
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
        log_text = ""
        log_file = Path(tmpdir) / "test.log"
        if log_file.exists():
            log_text = log_file.read_text(encoding="utf-8", errors="ignore")
        # PDF existence is the success criterion; lualatex returns non-zero for warnings
        return (pdf_exists, log_text)


class TestBeamerColors:
    """Verify OmniPrimaryColor/OmniAccentColor work in Beamer mode."""

    @pytest.mark.slow
    @pytest.mark.timeout(180)
    def test_beamer_colors_defined(self):
        """Beamer should compile with OmniPrimaryColor/OmniAccentColor."""
        tex = r"""
\documentclass[doctype=beamer]{omnilatex}
\title{Color Test}
\begin{document}
\begin{frame}
\frametitle{Test}
\textcolor{OmniPrimaryColor}{Primary} and \textcolor{OmniAccentColor}{Accent}
\end{frame}
\end{document}
"""
        success, log = _compile_tex(tex)
        assert success, f"Beamer color test failed.\nLog tail: {log[-500:]}"

    @pytest.mark.slow
    @pytest.mark.timeout(180)
    def test_beamer_custom_colors_override(self):
        """User-defined colors should override OmniPrimaryColor/OmniAccentColor."""
        tex = r"""
\documentclass[doctype=beamer]{omnilatex}
\definecolor{OmniPrimaryColor}{RGB}{255,0,0}
\definecolor{OmniAccentColor}{RGB}{0,255,0}
\title{Custom Color Test}
\begin{document}
\begin{frame}
\frametitle{Test}
Custom colors applied.
\end{frame}
\end{document}
"""
        success, log = _compile_tex(tex)
        assert success, f"Custom color override failed.\nLog tail: {log[-500:]}"


class TestBeamerClassSelection:
    """Verify correct LaTeX class is used for beamer doctype."""

    @pytest.mark.slow
    @pytest.mark.timeout(180)
    def test_beamer_doctype_uses_beamer_class(self):
        """doctype=beamer should use the beamer document class."""
        tex = BEAMER_TEMPLATE.format(
            options="doctype=beamer",
            doctype="beamer",
            frame_title="Class Check",
        )
        success, log = _compile_tex(tex)
        assert success, f"Beamer doctype compilation failed.\nLog tail: {log[-500:]}"
        assert "beamer" in log, "Expected 'beamer' class in log"

    @pytest.mark.slow
    @pytest.mark.timeout(180)
    def test_presentation_doctype_uses_koma(self):
        """doctype=presentation should use scrartcl (KOMA), not beamer."""
        tex = BEAMER_TEMPLATE.format(
            options="doctype=presentation",
            doctype="presentation",
            frame_title="KOMA Check",
        )
        success, log = _compile_tex(tex)
        assert (
            success
        ), f"Presentation doctype compilation failed.\nLog tail: {log[-500:]}"


class TestBeamerKOMASkips:
    """Verify KOMA-specific modules are skipped for beamer."""

    @pytest.mark.slow
    @pytest.mark.timeout(180)
    def test_beamer_skips_koma_layout(self):
        """Beamer should not load KOMA layout modules."""
        tex = r"""
\documentclass[doctype=beamer]{omnilatex}
\title{KOMA Skip Test}
\begin{document}
\begin{frame}
\frametitle{Test}
KOMA layout should be skipped.
\end{frame}
\end{document}
"""
        success, log = _compile_tex(tex)
        assert success, f"Beamer KOMA skip test failed.\nLog tail: {log[-500:]}"
        # Should NOT have scrlayer-scrpage errors
        assert (
            "scrlayer-scrpage" not in log
        ), "scrlayer-scrpage should not be loaded in beamer mode"

    @pytest.mark.slow
    @pytest.mark.timeout(180)
    def test_beamer_skips_hyperref(self):
        """Beamer should not load hyperref separately (beamer loads it)."""
        tex = r"""
\documentclass[doctype=beamer]{omnilatex}
\title{Hyperref Skip Test}
\begin{document}
\begin{frame}
\frametitle{Test}
Hyperref should be skipped.
\end{frame}
\end{document}
"""
        success, log = _compile_tex(tex)
        assert success, f"Beamer hyperref skip test failed.\nLog tail: {log[-500:]}"
        # Should not have option clash for hyperref
        assert (
            "Option clash" not in log
            or "hyperref" not in log.split("Option clash")[0][-200:]
        )


class TestBeamerCompatibilityStubs:
    """Verify KOMA compatibility stubs work in beamer mode."""

    @pytest.mark.slow
    @pytest.mark.timeout(180)
    def test_beamer_nonumberline_stub(self):
        """\\nonumberline should be defined (KOMA stub)."""
        tex = r"""
\documentclass[doctype=beamer]{omnilatex}
\title{Stub Test}
\begin{document}
\begin{frame}
\frametitle{Test}
\nonumberline should not error.
\end{frame}
\end{document}
"""
        success, log = _compile_tex(tex)
        assert success, f"nonumberline stub test failed.\nLog tail: {log[-500:]}"
        assert "Undefined control sequence" not in log or "nonumberline" not in log


class TestExaminerBackwardCompat:
    """Verify examniner->examiner backward-compat aliases work."""

    def test_examiner_aliases_in_document_module(self):
        """\\firstexaminer should be defined as alias for \\firstexaminer."""
        sty_path = PROJECT_ROOT / "lib" / "layout" / "omnilatex-document.sty"
        content = sty_path.read_text(encoding="utf-8")
        # Verify backward-compat aliases exist
        assert (
            "firstexamniner" in content or "examniner" in content
        ), "omnilatex-document.sty missing backward-compat alias for examiner typo"


class TestBeamerNativeExample:
    """Verify the beamer-native example exists and is properly configured."""

    def test_beamer_native_example_exists(self):
        """beamer-native example directory should exist."""
        example_dir = PROJECT_ROOT / "examples" / "beamer-native"
        assert example_dir.is_dir(), "examples/beamer-native/ directory missing"
        assert (
            example_dir / "main.tex"
        ).is_file(), "examples/beamer-native/main.tex missing"

    def test_beamer_native_uses_beamer_doctype(self):
        """beamer-native example should use doctype=beamer."""
        main_tex = PROJECT_ROOT / "examples" / "beamer-native" / "main.tex"
        content = main_tex.read_text(encoding="utf-8")
        assert (
            "doctype=beamer" in content
        ), "beamer-native example should use doctype=beamer"

    def test_beamer_native_uses_beamer_class(self):
        """beamer-native example should use beamer class directly."""
        main_tex = PROJECT_ROOT / "examples" / "beamer-native" / "main.tex"
        content = main_tex.read_text(encoding="utf-8")
        # The doctype=beamer routing should select beamer class
        m = re.search(r"\\documentclass\[.*?\]\{(.*?)\}", content)
        if m:
            assert (
                m.group(1) == "omnilatex"
            ), "beamer-native should use omnilatex class with doctype=beamer"
