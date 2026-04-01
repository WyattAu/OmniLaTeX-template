#!/usr/bin/env python3
"""Edge case tests for OmniLaTeX."""

import subprocess
import tempfile
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _compile_tex(content: str, options: str = "", timeout: int = 120) -> tuple:
    """Compile a minimal OmniLaTeX document. Returns (success, pdf_exists)."""
    import os

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "test.tex"
        tex_path.write_text(
            f"\\documentclass[{options}]{{omnilatex}}\n{content}\n\\end{{document}}\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [
                "latexmk",
                "-lualatex",
                "-interaction=nonstopmode",
                f"-outdir={tmpdir}",
                str(tex_path),
            ],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            env={
                **os.environ,
                "TEXINPUTS": f".:{PROJECT_ROOT}:{PROJECT_ROOT}/lib:",
            },
            timeout=timeout,
        )
        pdf_path = Path(tmpdir) / "test.pdf"
        return result.returncode == 0, pdf_path.exists()


def test_empty_document():
    """Minimal document: just begin/end."""
    success, has_pdf = _compile_tex("\\begin{document}")
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
