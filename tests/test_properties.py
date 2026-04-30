"""Property-based testing for OmniLaTeX document class options.

Validates that all valid option combinations compile successfully.
Uses hypothesis for fuzzing of option strings.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

try:
    from hypothesis import given, settings, HealthCheck
    from hypothesis.strategies import sampled_from
except ImportError:
    pytest.skip("hypothesis not installed", allow_module_level=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCTYPE_ALIASES = [
    "book",
    "thesis",
    "theses",
    "dissertation",
    "dissertations",
    "manual",
    "manuals",
    "guide",
    "guides",
    "handbook",
    "handbooks",
    "report",
    "reports",
    "technicalreport",
    "technical-report",
    "technicalreports",
    "technical-reports",
    "techreport",
    "tech-report",
    "techreports",
    "standard",
    "standards",
    "patent",
    "patents",
    "article",
    "articles",
    "paper",
    "papers",
    "inlinepaper",
    "inlinepapers",
    "inline-research",
    "inline-research-paper",
    "journal",
    "journals",
    "magazine",
    "magazines",
    "dictionary",
    "dictionaries",
    "lexicon",
    "lexicons",
    "cv",
    "resume",
    "resumes",
    "curriculumvitae",
    "cover-letter",
    "coverletter",
]

LANGUAGES = ["english", "german"]

TEMPLATE = r"""
\documentclass[{options}]{{omnilatex}}
\begin{{document}}
Test content for {{doctype}}.
\end{{document}}
"""


def compile_tex(tex_content: str, timeout: int = 180) -> tuple:
    """Compile tex content. Returns (success, log_excerpt)."""
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
        pdf_exists = (Path(tmpdir) / "test.pdf").exists()
        return (
            result.returncode == 0 and pdf_exists,
            result.stdout[-500:] if result.stdout else "",
        )


class TestDoctypeCompilation:
    """Test that every valid doctype compiles."""

    @pytest.mark.timeout(120)
    @pytest.mark.parametrize("doctype", DOCTYPE_ALIASES)
    @pytest.mark.parametrize("language", LANGUAGES)
    def test_doctype_language_combination(self, doctype, language):
        options = f"doctype={doctype},language={language}"
        tex = TEMPLATE.format(options=options, doctype=doctype)
        success, log = compile_tex(tex)
        assert success, f"Failed: {doctype}/{language}\nLog tail: {log}"


class TestPropertyBasedFuzzing:
    """Fuzz test with hypothesis."""

    @pytest.mark.timeout(300)
    @given(doctype=sampled_from(DOCTYPE_ALIASES))
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_random_doctype_compiles(self, doctype):
        tex = TEMPLATE.format(options=f"doctype={doctype}", doctype=doctype)
        success, _ = compile_tex(tex)
        assert success
