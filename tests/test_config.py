#!/usr/bin/env python3
"""Comprehensive config validation tests.

Tests that verify structural properties of config files, options,
document types, institutions, and module contracts without compilation.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestOptionSchema:
    """Validate specs/option_schema.toml against actual code."""

    def test_option_schema_exists(self):
        schema = REPO_ROOT / "specs" / "option_schema.toml"
        assert schema.is_file(), "option_schema.toml must exist"

    def test_option_schema_has_options_section(self):
        schema = (REPO_ROOT / "specs" / "option_schema.toml").read_text(encoding="utf-8")
        assert "[[option]]" in schema or "[options]" in schema

    @pytest.mark.parametrize("section", ["meta", "option"])
    def test_option_schema_sections_exist(self, section):
        schema = (REPO_ROOT / "specs" / "option_schema.toml").read_text(encoding="utf-8")
        assert (
            f"[{section}]" in schema or f"[[{section}]]" in schema
        ), f"Missing [{section}] section"

    def test_version_schema_exists(self):
        version_file = REPO_ROOT / "VERSION.md"
        assert version_file.is_file()
        content = version_file.read_text(encoding="utf-8")
        assert re.search(r"v\d+\.\d+\.\d+", content)


class TestDocumentTypes:
    """Validate config/document-types/ directory structure."""

    DOCTYPE_DIR = REPO_ROOT / "config" / "document-types"

    def test_doctype_dir_exists(self):
        assert self.DOCTYPE_DIR.is_dir()

    def test_doctype_count(self):
        sty_files = list(self.DOCTYPE_DIR.glob("*.sty"))
        assert (
            len(sty_files) >= 26
        ), f"Expected >= 26 doctype configs, got {len(sty_files)}"

    @pytest.mark.parametrize(
        "doctype",
        [
            "thesis",
            "article",
            "book",
            "cv",
            "presentation",
            "cover-letter",
            "letter",
            "memo",
            "invoice",
            "recipe",
            "homework",
            "exam",
            "syllabus",
            "handout",
            "lecture-notes",
            "journal",
            "technicalreport",
            "standard",
            "patent",
            "white-paper",
            "poster",
            "dissertation",
            "manual",
            "research-proposal",
            "inlinepaper",
            "dictionary",
        ],
    )
    def test_canonical_doctype_exists(self, doctype):
        sty = self.DOCTYPE_DIR / f"omnilatex-doctype-{doctype}.sty"
        assert sty.is_file(), f"Missing doctype config: omnilatex-{doctype}.sty"

    @pytest.mark.parametrize(
        "doctype",
        [
            "thesis",
            "article",
            "book",
            "cv",
            "presentation",
        ],
    )
    def test_doctype_has_providespackage(self, doctype):
        sty = (self.DOCTYPE_DIR / f"omnilatex-doctype-{doctype}.sty").read_text(encoding="utf-8")
        assert (
            "\\ProvidesPackage" in sty or "\\ProvidesFile" in sty
        ), f"{doctype}.sty missing ProvidesPackage"

    @pytest.mark.parametrize(
        "doctype",
        [
            "thesis",
            "article",
            "book",
            "cv",
            "presentation",
        ],
    )
    def test_doctype_has_provides_date(self, doctype):
        sty = (self.DOCTYPE_DIR / f"omnilatex-doctype-{doctype}.sty").read_text(encoding="utf-8")
        assert "\\ProvidesPackage" in sty, f"{doctype}.sty missing ProvidesPackage"
        # ProvidesPackage should include a date
        assert re.search(
            r"\d{4}[-/]\d{2}[-/]\d{2}", sty
        ), f"{doctype}.sty missing date in ProvidesPackage"

    @pytest.mark.parametrize(
        "doctype",
        [
            "thesis",
            "article",
            "book",
            "cv",
            "presentation",
            "cover-letter",
            "letter",
            "memo",
            "invoice",
            "recipe",
        ],
    )
    def test_doctype_has_citationstyle(self, doctype):
        sty = (self.DOCTYPE_DIR / f"omnilatex-doctype-{doctype}.sty").read_text(encoding="utf-8")
        assert "\\citationstyle" in sty, f"{doctype}.sty missing \\citationstyle"


class TestInstitutions:
    """Validate config/institutions/ directory."""

    INSTITUTION_DIR = REPO_ROOT / "config" / "institutions"

    def test_institution_count(self):
        dirs = [d for d in self.INSTITUTION_DIR.iterdir() if d.is_dir()]
        assert len(dirs) >= 21, f"Expected >= 21 institutions, got {len(dirs)}"

    @pytest.mark.parametrize(
        "institution",
        [
            "tuhh",
            "tum",
            "eth",
            "mit",
            "stanford",
            "cambridge",
            "oxford",
            "harvard",
            "yale",
            "princeton",
            "columbia",
            "epfl",
            "cmu",
            "imperial",
            "tudelft",
            "aalto",
            "chalmers",
            "kit",
            "ntnu",
            "uoft",
            "generic",
        ],
    )
    def test_institution_dir_exists(self, institution):
        inst_dir = self.INSTITUTION_DIR / institution
        assert inst_dir.is_dir(), f"Missing institution dir: {institution}"

    @pytest.mark.parametrize(
        "institution",
        [
            "tuhh",
            "tum",
            "eth",
            "mit",
            "stanford",
            "cambridge",
            "aalto",
            "chalmers",
            "kit",
            "ntnu",
            "uoft",
        ],
    )
    def test_institution_has_sty_file(self, institution):
        sty = self.INSTITUTION_DIR / institution / f"{institution}.sty"
        assert sty.is_file(), f"Missing {institution}.sty"

    @pytest.mark.parametrize(
        "institution",
        [
            "eth",
            "mit",
            "stanford",
            "cambridge",
            "aalto",
            "chalmers",
            "kit",
            "ntnu",
            "uoft",
        ],
    )
    def test_institution_has_color_definitions(self, institution):
        sty = (self.INSTITUTION_DIR / institution / f"{institution}.sty").read_text(encoding="utf-8")
        has_colors = (
            "\\definecolor" in sty or "\\textcolor" in sty or "\\colorlet" in sty
        )
        assert has_colors, f"{institution}.sty has no color definitions"


class TestModuleStructure:
    """Validate lib/ module directory structure."""

    def test_lib_dir_exists(self):
        assert (REPO_ROOT / "lib").is_dir()

    @pytest.mark.parametrize(
        "subdir",
        [
            "core",
            "layout",
            "typography",
            "references",
            "language",
            "graphics",
            "code",
            "tables",
            "utils",
        ],
    )
    def test_lib_subdir_exists(self, subdir):
        assert (REPO_ROOT / "lib" / subdir).is_dir(), f"Missing lib/{subdir}/"

    def test_module_count(self):
        sty_files = list(REPO_ROOT.glob("lib/**/*.sty"))
        assert (
            len(sty_files) >= 28
        ), f"Expected >= 28 module files, got {len(sty_files)}"

    @pytest.mark.parametrize(
        "module",
        [
            "lib/core/omnilatex-base",
            "lib/layout/omnilatex-page",
            "lib/typography/omnilatex-fonts",
            "lib/references/omnilatex-biblio",
            "lib/language/omnilatex-i18n",
            "lib/graphics/omnilatex-graphics",
            "lib/code/omnilatex-listings",
            "lib/tables/omnilatex-tables",
            "lib/utils/omnilatex-utils",
        ],
    )
    def test_core_module_exists(self, module):
        sty = REPO_ROOT / f"{module}.sty"
        assert sty.is_file(), f"Missing module: {module}.sty"


class TestI18n:
    """Validate language/i18n configuration."""

    I18N_FILE = REPO_ROOT / "lib" / "language" / "omnilatex-i18n.sty"

    def test_i18n_file_exists(self):
        assert self.I18N_FILE.is_file()

    def test_has_setotherlanguages(self):
        content = self.I18N_FILE.read_text(encoding="utf-8")
        assert "\\setotherlanguages" in content

    @pytest.mark.parametrize(
        "lang",
        [
            "english",
            "german",
            "french",
            "spanish",
            "russian",
            "italian",
            "portuguese",
            "dutch",
            "polish",
            "czech",
            "greek",
            "turkish",
            "simplifiedchinese",
            "traditionalchinese",
            "japanese",
            "korean",
            "arabic",
            "hebrew",
            "vietnamese",
            "hindi",
            "swedish",
            "finnish",
            "danish",
            "norsk",
        ],
    )
    def test_polyglossia_language_configured(self, lang):
        content = self.I18N_FILE.read_text(encoding="utf-8")
        assert lang in content, f"Language '{lang}' not in setotherlanguages"

    @pytest.mark.parametrize(
        "lang",
        [
            "english",
            "german",
            "french",
            "spanish",
            "russian",
            "italian",
            "portuguese",
            "dutch",
            "polish",
            "czech",
            "greek",
            "turkish",
            "vietnamese",
            "hindi",
            "swedish",
            "finnish",
            "danish",
            "norsk",
        ],
    )
    def test_translation_block_exists(self, lang):
        content = self.I18N_FILE.read_text(encoding="utf-8")
        assert (
            f"\\DeclareTranslation{{{lang}}}" in content
        ), f"No DeclareTranslation for {lang}"


class TestExamples:
    """Validate examples/ directory structure."""

    def test_examples_dir_exists(self):
        assert (REPO_ROOT / "examples").is_dir()

    def test_example_count(self):
        dirs = [d for d in (REPO_ROOT / "examples").iterdir() if d.is_dir()]
        assert len(dirs) >= 47, f"Expected >= 47 examples, got {len(dirs)}"

    @pytest.mark.parametrize(
        "example",
        [
            "minimal-starter",
            "thesis",
            "article",
            "book",
            "cv",
            "presentation",
            "cover-letter",
            "letter",
            "memo",
            "invoice",
            "recipe",
            "beamer-academic",
            "beamer-defense",
            "beamer-corporate",
            "beamer-minimal",
        ],
    )
    def test_example_dir_exists(self, example):
        assert (
            REPO_ROOT / "examples" / example
        ).is_dir(), f"Missing example: {example}"

    @pytest.mark.parametrize(
        "example",
        [
            "minimal-starter",
            "thesis",
            "article",
            "cv",
        ],
    )
    def test_example_has_main_tex(self, example):
        tex = REPO_ROOT / "examples" / example / "main.tex"
        assert tex.is_file(), f"{example}/main.tex missing"

    @pytest.mark.parametrize(
        "example",
        [
            "minimal-starter",
            "thesis",
            "article",
            "cv",
        ],
    )
    def test_example_uses_omnilatex_class(self, example):
        tex = (REPO_ROOT / "examples" / example / "main.tex").read_text(encoding="utf-8")
        assert "omnilatex" in tex, f"{example}/main.tex doesn't use omnilatex class"


class TestLeanProofs:
    """Validate Lean 4 proof structure."""

    PROOFS_DIR = REPO_ROOT / "specs" / "proofs" / "OmniLaTeXProofs"

    def test_proofs_dir_exists(self):
        assert self.PROOFS_DIR.is_dir()

    def test_lean_file_count(self):
        lean_files = list(self.PROOFS_DIR.glob("*.lean"))
        assert (
            len(lean_files) >= 16
        ), f"Expected >= 16 Lean files, got {len(lean_files)}"

    @pytest.mark.parametrize(
        "lean_file",
        [
            "DocumentSettings.lean",
            "DoctypeResolution.lean",
            "ModuleIntegrity.lean",
            "BuildModes.lean",
            "FontHierarchy.lean",
            "LanguageFallback.lean",
        ],
    )
    def test_lean_file_exists(self, lean_file):
        assert (self.PROOFS_DIR / lean_file).is_file()

    def test_no_sorry_in_proofs(self):
        """All Lean 4 proofs must be complete (no 'sorry')."""
        for lean_file in self.PROOFS_DIR.glob("*.lean"):
            content = lean_file.read_text(encoding="utf-8")
            assert (
                "sorry" not in content
            ), f"{lean_file.name} contains 'sorry' (incomplete proof)"


class TestReproducibility:
    """Validate reproducibility configuration."""

    def test_latexmkrc_exists(self):
        assert (REPO_ROOT / ".latexmkrc").is_file()

    def test_latexmkrc_has_sde(self):
        content = (REPO_ROOT / ".latexmkrc").read_text(encoding="utf-8")
        assert "source_date_epoch" in content.lower() or "SDE" in content

    def test_version_consistent(self):
        version_file = (REPO_ROOT / "VERSION.md").read_text(encoding="utf-8")
        build_lua = (REPO_ROOT / "build.lua").read_text(encoding="utf-8")
        v_md = re.search(r"(\d+\.\d+\.\d+)", version_file)
        v_lua = re.search(r"(\d+\.\d+\.\d+)", build_lua)
        assert v_md and v_lua, "Version not found in VERSION.md or build.lua"
        assert v_md.group(1) == v_lua.group(1), (
            f"Version mismatch: VERSION.md={v_md.group(1)}, "
            f"build.lua={v_lua.group(1)}"
        )

    def test_docker_env_exists(self):
        assert (REPO_ROOT / ".env.docker").is_file()
        content = (REPO_ROOT / ".env.docker").read_text(encoding="utf-8")
        assert "sha256:" in content, ".env.docker must contain SHA-256 digest"


class TestCICD:
    """Validate CI/CD configuration files."""

    GITHUB_WORKFLOWS = REPO_ROOT / ".github" / "workflows"

    def test_github_workflows_dir_exists(self):
        assert self.GITHUB_WORKFLOWS.is_dir()

    def test_workflow_count(self):
        workflows = list(self.GITHUB_WORKFLOWS.glob("*.yml"))
        assert len(workflows) >= 11, f"Expected >= 11 workflows, got {len(workflows)}"

    @pytest.mark.parametrize(
        "workflow",
        [
            "build.yml",
            "docker-ci.yml",
            "lean4-ci.yml",
            "ctan.yml",
            "integration-matrix.yml",
            "visual-regression.yml",
            "performance-regression.yml",
            "docker-digest-sync.yml",
        ],
    )
    def test_workflow_exists(self, workflow):
        assert (
            self.GITHUB_WORKFLOWS / workflow
        ).is_file(), f"Missing workflow: {workflow}"

    def test_docker_digest_consistency(self):
        """All CI configs must use the same Docker digest as .env.docker."""
        env_docker = (REPO_ROOT / ".env.docker").read_text(encoding="utf-8").strip()
        digest = re.search(r"(sha256:[a-f0-9]+)", env_docker)
        assert digest, "No sha256 digest in .env.docker"
        digest_str = digest.group(1)

        checked = 0
        for yml in REPO_ROOT.rglob("*.yml"):
            content = yml.read_text(encoding="utf-8")
            if "sha256:" in content and digest_str not in content:
                # Skip digest-sync workflow (it references old digests for replacement)
                if "digest-sync" in str(yml):
                    continue
                # Only check CI config files
                if any(
                    p in str(yml)
                    for p in [
                        ".github",
                        ".gitea",
                        ".forgejo",
                        ".gitlab",
                        ".woodpecker",
                        ".devcontainer",
                    ]
                ):
                    pytest.fail(f"{yml} has different digest than .env.docker")
            if digest_str in content:
                checked += 1
        assert checked >= 3, f"Digest only found in {checked} files (expected >= 3)"


class TestDocumentation:
    """Validate documentation files."""

    def test_readme_exists(self):
        assert (REPO_ROOT / "README.md").is_file()

    def test_contributing_exists(self):
        assert (REPO_ROOT / "CONTRIBUTING.md").is_file()

    def test_changelog_exists(self):
        assert (REPO_ROOT / "CHANGELOG.md").is_file()

    def test_license_exists(self):
        assert (REPO_ROOT / "LICENSE").is_file()

    def test_security_md_exists(self):
        assert (REPO_ROOT / "SECURITY.md").is_file()

    def test_support_md_exists(self):
        assert (REPO_ROOT / "SUPPORT.md").is_file()

    def test_codeowners_exists(self):
        assert (REPO_ROOT / "CODEOWNERS").is_file()

    def test_docs_dir_exists(self):
        assert (REPO_ROOT / "docs").is_dir()

    @pytest.mark.parametrize(
        "doc",
        [
            "USER_GUIDE.md",
            "API_REFERENCE.md",
            "gallery.md",
            "accessibility.md",
            "editor-integration.md",
            "BREAKING_CHANGES.md",
            "API_STABILITY.md",
        ],
    )
    def test_doc_file_exists(self, doc):
        assert (REPO_ROOT / "docs" / doc).is_file(), f"Missing docs/{doc}"

    def test_ctan_readme_exists(self):
        assert (REPO_ROOT / "CTAN_README.txt").is_file()


class TestTranslationPlaceholders:
    """Ensure no untranslated '???' placeholders in committed .sty files.

    The scaffold-language command generates guide files with '???' stubs.
    Those stubs must be replaced before the translations are integrated
    into the actual .sty files in lib/language/.
    """

    def test_no_placeholder_values_in_sty_files(self):
        """No DeclareTranslation{...}{???} in any .sty file."""
        hits: list[str] = []
        for sty in sorted(REPO_ROOT.glob("lib/**/*.sty")):
            content = sty.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(content.splitlines(), 1):
                if "DeclareTranslation" in line and "{???}" in line:
                    rel = sty.relative_to(REPO_ROOT)
                    hits.append(f"{rel}:{lineno}: {line.strip()}")
        assert hits == [], (
            f"Found {len(hits)} untranslated placeholder(s) in .sty files:\n"
            + "\n".join(hits)
        )
