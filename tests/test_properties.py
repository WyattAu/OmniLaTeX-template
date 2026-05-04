"""Property-based testing for OmniLaTeX document class options.

Validates that all valid option combinations compile successfully.
Uses hypothesis for fuzzing of option strings.
"""

import os
import re
import subprocess
import tempfile
from collections import Counter
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


class TestStructuralProperties:
    """Static structural property tests for OmniLaTeX configuration."""

    VALID_KOMA_CLASSES = {"scrartcl", "scrbook", "scrreprt"}

    DOCTYPE_TO_CLASS = {
        "book": "scrbook",
        "thesis": "scrbook",
        "dissertation": "scrbook",
        "dictionary": "scrbook",
        "manual": "scrreprt",
        "technicalreport": "scrreprt",
        "technical-report": "scrreprt",
        "standard": "scrreprt",
        "patent": "scrreprt",
        "research-proposal": "scrreprt",
        "white-paper": "scrreprt",
        "article": "scrartcl",
        "journal": "scrartcl",
        "inlinepaper": "scrartcl",
        "cv": "scrartcl",
        "cover-letter": "scrartcl",
        "poster": "scrartcl",
        "presentation": "scrartcl",
        "letter": "scrartcl",
        "homework": "scrartcl",
        "exam": "scrartcl",
        "lecture-notes": "scrartcl",
        "syllabus": "scrartcl",
        "handout": "scrartcl",
        "memo": "scrartcl",
        "invoice": "scrartcl",
        "recipe": "scrartcl",
    }

    CANONICAL_DOCTYPES = [
        "article", "book", "cover-letter", "cv", "dictionary", "dissertation",
        "exam", "handout", "homework", "inlinepaper", "invoice", "journal",
        "lecture-notes", "letter", "manual", "memo", "patent", "poster",
        "presentation", "recipe", "research-proposal", "standard", "syllabus",
        "technicalreport", "thesis", "white-paper",
    ]

    def _get_doctype_names(self) -> list[str]:
        dt_dir = PROJECT_ROOT / "config" / "document-types"
        if not dt_dir.is_dir():
            return []
        return sorted(p.stem for p in dt_dir.glob("*.sty"))

    def _get_institution_names(self) -> list[str]:
        inst_dir = PROJECT_ROOT / "config" / "institutions"
        if not inst_dir.is_dir():
            return []
        return sorted(
            d.name
            for d in inst_dir.iterdir()
            if d.is_dir() and d.name != "README.md"
        )

    def _get_example_doctypes(self) -> dict[str, str]:
        examples_dir = PROJECT_ROOT / "examples"
        result = {}
        if not examples_dir.is_dir():
            return result
        for ex_dir in examples_dir.iterdir():
            main_tex = ex_dir / "main.tex"
            if main_tex.is_file():
                content = main_tex.read_text(encoding="utf-8", errors="replace")
                m = re.search(r"doctype=([a-zA-Z-]+)", content)
                if m:
                    result[ex_dir.name] = m.group(1)
        return result

    def _get_require_packages(self) -> list[str]:
        cls_file = PROJECT_ROOT / "omnilatex.cls"
        if not cls_file.is_file():
            return []
        content = cls_file.read_text(encoding="utf-8", errors="replace")
        packages = []
        for m in re.finditer(r"\\RequirePackage(?:\[[^\]]*\])?\{([^}]+)\}", content):
            packages.append(m.group(1).strip())
        return packages

    def _get_translation_counts(self) -> dict[str, int]:
        i18n_file = PROJECT_ROOT / "lib" / "language" / "omnilatex-i18n.sty"
        if not i18n_file.is_file():
            return {}
        content = i18n_file.read_text(encoding="utf-8", errors="replace")
        counts: dict[str, int] = Counter()
        for m in re.finditer(r"\\DeclareTranslation\{(\w+)\}\{", content):
            counts[m.group(1)] += 1
        return dict(counts)

    def _get_translation_key_dupes(self) -> list[tuple[str, str]]:
        i18n_file = PROJECT_ROOT / "lib" / "language" / "omnilatex-i18n.sty"
        if not i18n_file.is_file():
            return []
        content = i18n_file.read_text(encoding="utf-8", errors="replace")
        seen: dict[tuple[str, str], int] = {}
        dupes = []
        for m in re.finditer(r"\\DeclareTranslation\{(\w+)\}\{(\w+)\}", content):
            lang, key = m.group(1), m.group(2)
            pair = (lang, key)
            if pair in seen:
                dupes.append(pair)
            else:
                seen[pair] = 1
        return dupes

    @given(doctype=sampled_from(list(DOCTYPE_TO_CLASS.keys())))
    @settings(max_examples=50, deadline=None)
    def test_doctype_maps_to_valid_koma_class(self, doctype):
        koma_class = self.DOCTYPE_TO_CLASS[doctype]
        assert koma_class in self.VALID_KOMA_CLASSES, (
            f"doctype '{doctype}' maps to '{koma_class}', not a valid KOMA class"
        )

    def test_all_doctype_files_map_to_koma_classes(self):
        doctype_names = self._get_doctype_names()
        assert len(doctype_names) > 0, "No doctype .sty files found"
        for name in doctype_names:
            assert name in self.DOCTYPE_TO_CLASS, (
                f"Doctype file '{name}.sty' has no mapping in DOCTYPE_TO_CLASS"
            )
            koma_class = self.DOCTYPE_TO_CLASS[name]
            assert koma_class in self.VALID_KOMA_CLASSES, (
                f"Doctype '{name}' maps to invalid KOMA class '{koma_class}'"
            )

    @given(institution=sampled_from(list(_get_institution_names(None) or ["generic"])))
    @settings(max_examples=20, deadline=None)
    def test_institution_has_valid_providespackage(self, institution):
        inst_dir = PROJECT_ROOT / "config" / "institutions" / institution
        sty_files = list(inst_dir.glob("*.sty")) if inst_dir.is_dir() else []
        assert len(sty_files) > 0, f"No .sty file in institution '{institution}'"
        for sty_file in sty_files:
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            assert "\\ProvidesPackage" in content, (
                f"{sty_file.relative_to(PROJECT_ROOT)} missing \\ProvidesPackage"
            )

    def test_all_institutions_have_providespackage(self):
        institutions = self._get_institution_names()
        assert len(institutions) > 0, "No institution directories found"
        for inst in institutions:
            inst_dir = PROJECT_ROOT / "config" / "institutions" / inst
            sty_files = list(inst_dir.glob("*.sty"))
            assert len(sty_files) > 0, f"No .sty in institution '{inst}'"
            for sty_file in sty_files:
                content = sty_file.read_text(encoding="utf-8", errors="replace")
                assert "\\ProvidesPackage" in content, (
                    f"{sty_file.relative_to(PROJECT_ROOT)} missing \\ProvidesPackage"
                )

    def test_translation_key_parity(self):
        counts = self._get_translation_counts()
        assert len(counts) > 0, "No translations found in i18n module"
        values = list(counts.values())
        assert all(v == values[0] for v in values), (
            f"Translation key counts are not equal across languages: {counts}"
        )

    @given(example=sampled_from(list(_get_example_doctypes(None).keys()) or ["thesis"]))
    @settings(max_examples=30, deadline=None)
    def test_example_doctype_is_registered(self, example):
        example_doctypes = self._get_example_doctypes()
        if not example_doctypes:
            pytest.skip("No examples found")
        doctype = example_doctypes[example]
        assert doctype in self.DOCTYPE_TO_CLASS, (
            f"Example '{example}' uses doctype '{doctype}' which is not registered"
        )

    def test_all_examples_use_registered_doctypes(self):
        example_doctypes = self._get_example_doctypes()
        assert len(example_doctypes) > 0, "No examples with doctypes found"
        for ex_name, doctype in example_doctypes.items():
            assert doctype in self.DOCTYPE_TO_CLASS, (
                f"Example '{ex_name}' uses unregistered doctype '{doctype}'"
            )

    def test_all_modules_exist(self):
        packages = self._get_require_packages()
        assert len(packages) > 0, "No \\RequirePackage found in omnilatex.cls"
        for pkg in packages:
            if pkg.startswith("lib/"):
                pkg_path = PROJECT_ROOT / (pkg + ".sty")
                assert pkg_path.is_file(), (
                    f"\\RequirePackage{{{pkg}}} in omnilatex.cls: "
                    f"{pkg_path.relative_to(PROJECT_ROOT)} not found"
                )

    @given(pkg=sampled_from(list(_get_require_packages(None))))
    @settings(max_examples=50, deadline=None)
    def test_each_module_exists(self, pkg):
        if not pkg.startswith("lib/"):
            return
        pkg_path = PROJECT_ROOT / (pkg + ".sty")
        assert pkg_path.is_file(), (
            f"\\RequirePackage{{{pkg}}}: {pkg_path.relative_to(PROJECT_ROOT)} not found"
        )

    def test_no_duplicate_translation_keys(self):
        dupes = self._get_translation_key_dupes()
        assert len(dupes) == 0, (
            f"Duplicate translation keys found: {dupes}"
        )

    @given(doctype=sampled_from(CANONICAL_DOCTYPES))
    @settings(max_examples=50, deadline=None)
    def test_doctype_sty_file_exists(self, doctype):
        sty_path = PROJECT_ROOT / "config" / "document-types" / f"{doctype}.sty"
        assert sty_path.is_file(), f"Doctype config not found: {sty_path}"
