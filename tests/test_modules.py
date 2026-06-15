import pathlib
import re

import pytest

from tests.constants import (
    ALL_DOCTYPE_NAMES,
    ALL_EXAMPLE_NAMES,
    DOCTYPE_ALIASES,
    DOCTYPE_TO_CLASS,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

EXPECTED_LIB_SUBDIRS = [
    "code",
    "core",
    "graphics",
    "language",
    "layout",
    "references",
    "tables",
    "typography",
    "utils",
]

INSTITUTION_NAMES = [
    "aalto",
    "cambridge",
    "chalmers",
    "cmu",
    "columbia",
    "epfl",
    "eth",
    "generic",
    "harvard",
    "imperial",
    "kit",
    "mit",
    "ntnu",
    "oxford",
    "princeton",
    "stanford",
    "tudelft",
    "tuhh",
    "tum",
    "uoft",
    "yale",
]

DOCUMENT_SETTINGS_COMMANDS = [
    r"\setMainFont",
    r"\setSansFont",
    r"\setMonoFont",
    r"\setMathFont",
    r"\setCustomMargins",
]


def _read(path):
    return path.read_text(encoding="utf-8")


def _extract_doctype_from_main(main_tex_path):
    text = _read(main_tex_path)
    m = re.search(r'doctype\s*=\s*["\']?([\w-]+)["\']?', text)
    if m:
        return m.group(1).strip().lower()
    return None


def _extract_institution_from_main(main_tex_path):
    text = _read(main_tex_path)
    m = re.search(r"institution\s*=\s*([\w-]+)", text)
    if m:
        return m.group(1).strip().lower()
    return None


def _resolve_doctype_alias(doctype):
    return DOCTYPE_ALIASES.get(doctype, doctype)


class TestDocumentTypeRegistration:
    def test_cls_file_exists(self, repo_root):
        assert (repo_root / "omnilatex.cls").is_file()

    def test_all_doctypes_registered_in_cls(self, repo_root):
        cls_text = _read(repo_root / "omnilatex.cls")
        for dt in ALL_DOCTYPE_NAMES:
            assert dt in cls_text, f"doctype '{dt}' not found in omnilatex.cls"

    @pytest.mark.parametrize("doctype,baseclass", DOCTYPE_TO_CLASS.items())
    def test_doctype_maps_to_correct_class(self, repo_root, doctype, baseclass):
        cls_text = _read(repo_root / "omnilatex.cls")
        pattern = (
            re.escape(r"\omnilatex@setdoctype{")
            + re.escape(doctype)
            + re.escape("}{")
            + re.escape(baseclass)
            + re.escape("}")
        )
        assert re.search(
            pattern, cls_text
        ), f"doctype '{doctype}' does not map to '{baseclass}' in omnilatex.cls"

    def test_warning_message_lists_all_doctypes(self, repo_root):
        cls_text = _read(repo_root / "omnilatex.cls")
        warning_match = re.search(
            r"ClassWarning\{omnilatex\}.*?Valid options:\s*(.*?)\}",
            cls_text,
            re.DOTALL,
        )
        assert warning_match, "Could not find doctype warning message in omnilatex.cls"
        warning_text = warning_match.group(1)
        for dt in ALL_DOCTYPE_NAMES:
            assert dt in warning_text, f"doctype '{dt}' not listed in warning message"

    def test_doctype_count(self, repo_root):
        cls_text = _read(repo_root / "omnilatex.cls")
        registrations = re.findall(r"omnilatex@setdoctype\{(\w[\w-]*)\}", cls_text)
        unique_primary = set()
        for name in registrations:
            if name != "book":
                unique_primary.add(name)
        unique_primary.add("book")
        assert len(unique_primary) >= 26, (
            f"Expected at least 26 unique doctypes, "
            f"found {len(unique_primary)}: {sorted(unique_primary)}"
        )


class TestModuleFileIntegrity:
    def test_lib_subdirectories_exist(self, repo_root):
        for subdir in EXPECTED_LIB_SUBDIRS:
            assert (
                repo_root / "lib" / subdir
            ).is_dir(), f"lib/{subdir}/ directory missing"

    def test_lib_subdirectories_contain_sty_files(self, repo_root):
        for subdir in EXPECTED_LIB_SUBDIRS:
            sty_files = list((repo_root / "lib" / subdir).glob("*.sty"))
            assert len(sty_files) > 0, f"lib/{subdir}/ contains no .sty files"

    def test_lib_has_no_empty_subdirectories(self, repo_root):
        lib_dir = repo_root / "lib"
        for subdir in sorted(lib_dir.iterdir()):
            if subdir.is_dir() and not subdir.name.startswith((".", "_")):
                contents = list(subdir.iterdir())
                assert len(contents) > 0, f"lib/{subdir.name}/ is empty"

    @pytest.mark.parametrize("doctype", ALL_DOCTYPE_NAMES)
    def test_doctype_sty_files_exist(self, repo_root, doctype):
        path = (
            repo_root / "config" / "document-types" / f"omnilatex-doctype-{doctype}.sty"
        )
        assert (
            path.is_file()
        ), f"config/document-types/omnilatex-doctype-{doctype}.sty missing"

    @pytest.mark.parametrize("doctype", ALL_DOCTYPE_NAMES)
    def test_doctype_sty_has_needs_tex_format(self, repo_root, doctype):
        path = (
            repo_root / "config" / "document-types" / f"omnilatex-doctype-{doctype}.sty"
        )
        text = _read(path)
        assert r"\NeedsTeXFormat" in text, f"{doctype}.sty missing \\NeedsTeXFormat"

    @pytest.mark.parametrize("doctype", ALL_DOCTYPE_NAMES)
    def test_doctype_sty_has_provides_file(self, repo_root, doctype):
        path = (
            repo_root / "config" / "document-types" / f"omnilatex-doctype-{doctype}.sty"
        )
        text = _read(path)
        assert (
            r"\ProvidesPackage" in text or r"\ProvidesFile" in text
        ), f"{doctype}.sty missing \\ProvidesPackage or \\ProvidesFile"

    def test_cls_has_needs_tex_format(self, repo_root):
        text = _read(repo_root / "omnilatex.cls")
        assert r"\NeedsTeXFormat" in text

    def test_cls_has_provides_class(self, repo_root):
        text = _read(repo_root / "omnilatex.cls")
        assert r"\ProvidesClass" in text

    def test_cls_has_load_class(self, repo_root):
        text = _read(repo_root / "omnilatex.cls")
        assert r"\LoadClass" in text


class TestConfigFileValidation:
    def test_document_settings_exists(self, repo_root):
        assert (repo_root / "config" / "omnilatex-document-settings.sty").is_file()

    def test_document_settings_has_override_commands(self, repo_root):
        text = _read(repo_root / "config" / "omnilatex-document-settings.sty")
        for cmd in DOCUMENT_SETTINGS_COMMANDS:
            assert cmd in text, f"document-settings.sty missing {cmd}"

    def test_institution_configs_exist(self, repo_root):
        for inst in INSTITUTION_NAMES:
            path = repo_root / "config" / "institutions" / inst / f"{inst}.sty"
            assert path.is_file(), f"config/institutions/{inst}/{inst}.sty missing"

    @pytest.mark.parametrize("institution", INSTITUTION_NAMES)
    def test_institution_config_has_proper_structure(self, repo_root, institution):
        path = (
            repo_root / "config" / "institutions" / institution / f"{institution}.sty"
        )
        text = _read(path)
        assert r"\NeedsTeXFormat" in text, f"{institution}.sty missing \\NeedsTeXFormat"
        assert (
            r"\ProvidesPackage" in text or r"\ProvidesFile" in text
        ), f"{institution}.sty missing \\ProvidesPackage or \\ProvidesFile"

    def test_at_least_five_institutions(self, repo_root):
        inst_dir = repo_root / "config" / "institutions"
        count = sum(
            1 for d in inst_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        )
        assert count >= 5, f"Expected at least 5 institutions, found {count}"


class TestExampleIntegrity:
    @pytest.mark.parametrize("example", ALL_EXAMPLE_NAMES)
    def test_example_has_main_tex(self, repo_root, example):
        path = repo_root / "examples" / example / "main.tex"
        assert path.is_file(), f"examples/{example}/main.tex missing"

    @pytest.mark.parametrize("example", ALL_EXAMPLE_NAMES)
    def test_example_has_document_settings(self, repo_root, example):
        path = repo_root / "examples" / example / "config" / "document-settings.sty"
        assert (
            path.is_file()
        ), f"examples/{example}/config/document-settings.sty missing"

    @pytest.mark.parametrize("example", ALL_EXAMPLE_NAMES)
    def test_example_doctype_is_valid(self, repo_root, example):
        main_tex = repo_root / "examples" / example / "main.tex"
        doctype = _extract_doctype_from_main(main_tex)
        if doctype is None:
            pytest.skip(f"examples/{example}/main.tex has no doctype= option")
        doctype = _resolve_doctype_alias(doctype)
        doctype_sty = (
            repo_root / "config" / "document-types" / f"omnilatex-doctype-{doctype}.sty"
        )
        assert doctype_sty.is_file(), (
            f"examples/{example} uses doctype='{doctype}' but "
            f"config/document-types/omnilatex-doctype-{doctype}.sty does not exist"
        )

    def test_bib_bibliography_exists(self, repo_root):
        assert (repo_root / "bib" / "bibliography.bib").is_file()

    def test_all_examples_exist(self, repo_root):
        examples_dir = repo_root / "examples"
        actual = sorted(
            d.name
            for d in examples_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )
        expected = sorted(ALL_EXAMPLE_NAMES)
        assert actual == expected, (
            f"Example directories differ.\n"
            f"Missing: {set(expected) - set(actual)}\n"
            f"Extra: {set(actual) - set(expected)}"
        )


class TestCrossReferenceConsistency:
    @pytest.mark.parametrize("example", ALL_EXAMPLE_NAMES)
    def test_example_doctype_sty_exists(self, repo_root, example):
        main_tex = repo_root / "examples" / example / "main.tex"
        doctype = _extract_doctype_from_main(main_tex)
        if doctype is None:
            pytest.skip(f"examples/{example}/main.tex has no doctype= option")
        doctype = _resolve_doctype_alias(doctype)
        sty = (
            repo_root / "config" / "document-types" / f"omnilatex-doctype-{doctype}.sty"
        )
        assert sty.is_file(), (
            f"examples/{example} references doctype='{doctype}' "
            f"but config/document-types/omnilatex-doctype-{doctype}.sty missing"
        )

    @pytest.mark.parametrize("example", ALL_EXAMPLE_NAMES)
    def test_example_institution_config_exists(self, repo_root, example):
        main_tex = repo_root / "examples" / example / "main.tex"
        institution = _extract_institution_from_main(main_tex)
        if institution is None or institution == "none":
            pytest.skip(f"examples/{example} uses institution=none or not set")
        inst_sty = (
            repo_root / "config" / "institutions" / institution / f"{institution}.sty"
        )
        assert inst_sty.is_file(), (
            f"examples/{example} references institution='{institution}' "
            f"but config/institutions/{institution}/{institution}.sty missing"
        )

    @pytest.mark.parametrize("doctype", ALL_DOCTYPE_NAMES)
    def test_doctype_lib_references_exist(self, repo_root, doctype):
        sty_path = (
            repo_root / "config" / "document-types" / f"omnilatex-doctype-{doctype}.sty"
        )
        text = _read(sty_path)
        lib_refs = re.findall(r"\\(?:RequirePackage|input)\{((?:lib/)[^}]+)\}", text)
        missing = []
        for ref in lib_refs:
            ref_path = repo_root / (ref if ref.endswith(".sty") else f"{ref}.sty")
            if not ref_path.is_file():
                ref_lua = repo_root / ref
                if not (ref.endswith(".lua") and ref_lua.is_file()):
                    missing.append(ref)
        assert (
            not missing
        ), f"omnilatex-doctype-{doctype}.sty refs missing lib files: {missing}"


class TestOverleafPackage:
    def test_overleaf_zip_script_exists(self, repo_root):
        assert (repo_root / "scripts" / "make-overleaf-zip.sh").is_file()

    def test_overleaf_zip_script_executable(self, repo_root):
        script = repo_root / "scripts" / "make-overleaf-zip.sh"
        import os

        assert os.access(script, os.X_OK), "make-overleaf-zip.sh is not executable"

    def test_overleaf_script_references_existing_files(self, repo_root):
        script_text = _read(repo_root / "scripts" / "make-overleaf-zip.sh")
        cp_targets = re.findall(r'cp\s+"?\$REPO_ROOT/([^" ]+)"?', script_text)
        cp_targets += re.findall(r'cp\s+-r\s+"?\$REPO_ROOT/([^" ]+)"?', script_text)
        missing = []
        seen = set()
        for target in cp_targets:
            if target in seen:
                continue
            seen.add(target)
            target_path = repo_root / target
            if not target_path.exists():
                missing.append(target)
        assert not missing, f"make-overleaf-zip.sh references missing files: {missing}"
