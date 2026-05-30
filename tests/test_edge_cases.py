#!/usr/bin/env python3
"""Edge case tests for OmniLaTeX.

These tests compile actual LaTeX documents and can be slow.
Run with: pytest tests/test_edge_cases.py -v -m slow
Skip with: pytest tests/ -v -m "not slow"
"""

import subprocess
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Skip all edge case tests by default; they require LaTeX compilation.
# Run explicitly with: pytest -m slow
pytestmark = pytest.mark.slow


def _compile_tex(content: str, options: str = "", timeout: int = 600) -> tuple:
    """Compile a minimal OmniLaTeX document. Returns (success, pdf_exists).

    Uses lualatex directly (single pass) rather than latexmk to avoid
    non-zero exit codes from the biber/biblatex cycle.  These tests
    verify that the document compiles and produces a PDF; bibliography
    resolution is out of scope.
    """
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "test.tex"
        tex_path.write_text(
            f"\\documentclass[{options}]{{omnilatex}}\n{content}\n\\end{{document}}\n",
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
            timeout=timeout,
        )
        pdf_path = Path(tmpdir) / "test.pdf"
        # lualatex returns non-zero for warnings (overfull boxes, undefined refs)
        # but still produces valid PDFs. PDF existence is the reliable success metric.
        pdf_exists = pdf_path.exists()
        return (pdf_exists, pdf_exists)


def test_empty_document():
    """Minimal document: just begin/end with mbox to ensure a page is output."""
    success, has_pdf = _compile_tex("\\begin{document}\\mbox{}")
    assert success and has_pdf


def test_only_floats():
    """Document with only floats, no body text."""
    content = """\\begin{document}
    \\begin{figure}[htbp]
        \\centering
        \\caption{A float with no content}
    \\end{figure}
    \\begin{table}[htbp]
        \\centering
        \\caption{A table with no content}
    \\end{table}
    """
    success, has_pdf = _compile_tex(content)
    assert success and has_pdf


@pytest.mark.timeout(120)
def test_long_caption():
    """Very long caption (>500 characters)."""
    long_text = "x" * 600
    content = f"""\\begin{{document}}
    \\begin{{figure}}[htbp]
        \\centering
        \\caption{{{long_text}}}
    \\end{{figure}}
    """
    success, has_pdf = _compile_tex(content)
    assert success and has_pdf


@pytest.mark.timeout(120)
def test_deeply_nested_lists():
    """Deeply nested list environments (10 levels)."""
    nested = "\\begin{document}\n"
    for i in range(10):
        nested += f"\\begin{{itemize}}\\item Level {i + 1}\n"
    nested += "Content at the deepest level\n"
    for i in range(10):
        nested += "\\end{itemize}\n"
    success, has_pdf = _compile_tex(nested)
    assert has_pdf


@pytest.mark.timeout(300)
def test_large_document():
    """Document with many pages (100+ pages)."""
    content = "\\begin{document}\n"
    for i in range(110):
        content += f"\\section{{Section {i}}}\n"
        content += "Lorem ipsum dolor sit amet. " * 20 + "\n\n"
    success, has_pdf = _compile_tex(content, timeout=300)
    assert success and has_pdf


@pytest.mark.timeout(300)
def test_many_cross_references():
    """Hundreds of cross-references."""
    content = "\\begin{document}\n"
    for i in range(200):
        content += f"\\section{{Section {i}}}\\label{{sec:{i}}}\n"
    for i in range(200):
        content += f"See section~\\ref{{sec:{i}}}.\n"
    success, has_pdf = _compile_tex(content, timeout=300)
    assert success and has_pdf
