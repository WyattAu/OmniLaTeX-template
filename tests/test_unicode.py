#!/usr/bin/env python3
"""Unicode stress tests for OmniLaTeX."""

import subprocess
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UNICODE_TEST_CASES = [
    ("cjk_chinese", "Chinese characters", "中文文本测试"),
    ("cjk_japanese", "Japanese characters", "日本語テスト"),
    ("cjk_korean", "Korean characters", "한국어 테스트"),
    ("arabic_rtl", "Arabic RTL", "العربية"),
    ("math_unicode", "Math Unicode symbols", "∑ ∫ ∂ ∰ 𝕏 √ ∞"),
    ("emoji", "Emoji characters", "📊 🔬 🎓"),
    ("combining", "Combining characters", "e\u0301 cafe\u0301"),
    ("cyrillic", "Cyrillic", "Русский текст"),
    ("greek", "Greek", "Ελληνικό κείμενο"),
    (
        "special_latex",
        "Special LaTeX chars",
        "\\& \\% \\$ \\# \\_ \\{ \\} \\textasciitilde{} \\textasciicircum{} \\textbackslash{}",
    ),
]


def _compile_tex(content: str) -> bool:
    """Compile a minimal OmniLaTeX document with the given content.

    Uses lualatex directly (single pass) rather than latexmk to avoid
    non-zero exit codes from the biber/biblatex cycle.  These tests
    verify that the document compiles and produces a PDF; bibliography
    resolution is out of scope.
    """
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "test.tex"
        tex_path.write_text(
            f"\\documentclass{{omnilatex}}\n"
            f"\\begin{{document}}\n{content}\n\\end{{document}}\n",
            encoding="utf-8",
        )
        subprocess.run(
            [
                "lualatex",
                "-interaction=nonstopmode",
                f"-output-directory={tmpdir}",
                str(tex_path),
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env={
                **os.environ,
                "TEXINPUTS": f".:{PROJECT_ROOT}:{PROJECT_ROOT}/lib:{PROJECT_ROOT}/config:",
            },
            timeout=600,
        )
        pdf_path = Path(tmpdir) / "test.pdf"
        return pdf_path.exists()


@pytest.mark.slow
@pytest.mark.parametrize("name,description,content", UNICODE_TEST_CASES)
def test_unicode_compilation(name, description, content):
    """Test that documents with various Unicode content compile."""
    assert _compile_tex(content), f"Failed to compile with {description}: {content}"
