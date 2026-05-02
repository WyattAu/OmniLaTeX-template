import os
import pathlib
import shutil
import subprocess
import zipfile

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

CTAN_SCRIPT = REPO_ROOT / "scripts" / "make-ctan-zip.sh"
OVERLEAF_SCRIPT = REPO_ROOT / "scripts" / "make-overleaf-zip.sh"


def _zip_available():
    return shutil.which("zip") is not None


needs_zip = pytest.mark.skipif(not _zip_available(), reason="zip command not available")


def _build_ctan_zip_with_python(output_path):
    pkg_dir = output_path.parent / "omnilatex_pkg"
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    pkg_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(REPO_ROOT / "omnilatex.cls", pkg_dir / "omnilatex.cls")
    shutil.copytree(REPO_ROOT / "lib", pkg_dir / "lib")

    (pkg_dir / "config" / "document-types").mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO_ROOT / "config" / "document-settings.sty",
                 pkg_dir / "config" / "document-settings.sty")
    if (REPO_ROOT / "config" / "document-types").is_dir():
        for item in (REPO_ROOT / "config" / "document-types").iterdir():
            if item.is_file():
                shutil.copy2(str(item), pkg_dir / "config" / "document-types" / item.name)
    (pkg_dir / "bib").mkdir(parents=True, exist_ok=True)
    if (REPO_ROOT / "bib" / "bibliography.bib").is_file():
        shutil.copy2(REPO_ROOT / "bib" / "bibliography.bib",
                     pkg_dir / "bib" / "bibliography.bib")
    for name in ("README.md", "LICENSE", "CHANGELOG.md", "VERSION.md"):
        src = REPO_ROOT / name
        if src.is_file():
            shutil.copy2(src, pkg_dir / name)

    with zipfile.ZipFile(str(output_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(pkg_dir.rglob("*")):
            if file_path.is_file():
                arcname = "omnilatex/" + str(file_path.relative_to(pkg_dir))
                zf.write(str(file_path), arcname)

    shutil.rmtree(pkg_dir)
    return output_path


def _build_overleaf_zip_with_python(example_name, output_path):
    example_dir = REPO_ROOT / "examples" / example_name
    assert example_dir.is_dir(), f"Example '{example_name}' not found"

    pkg_dir = output_path.parent / "omnilatex_overleaf_pkg"
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)
    pkg_dir.mkdir(parents=True, exist_ok=True)

    shutil.copy2(REPO_ROOT / "omnilatex.cls", pkg_dir / "omnilatex.cls")
    shutil.copytree(REPO_ROOT / "lib", pkg_dir / "lib")
    shutil.copytree(REPO_ROOT / "config" / "document-types",
                    pkg_dir / "config" / "document-types")
    if (REPO_ROOT / "config" / "document-settings.sty").is_file():
        shutil.copy2(REPO_ROOT / "config" / "document-settings.sty",
                     pkg_dir / "config" / "document-settings.sty")
    if (REPO_ROOT / "bib").is_dir():
        shutil.copytree(REPO_ROOT / "bib", pkg_dir / "bib")
    if (example_dir / "main.tex").is_file():
        shutil.copy2(example_dir / "main.tex", pkg_dir / "main.tex")
    if (example_dir / "config").is_dir():
        dest_config = pkg_dir / "config"
        dest_config.mkdir(parents=True, exist_ok=True)
        for item in (example_dir / "config").iterdir():
            shutil.copy2(str(item), dest_config / item.name)

    with zipfile.ZipFile(str(output_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(pkg_dir.rglob("*")):
            if file_path.is_file():
                arcname = "omnilatex-overleaf/" + str(file_path.relative_to(pkg_dir))
                zf.write(str(file_path), arcname)

    shutil.rmtree(pkg_dir)
    return output_path


@pytest.fixture(scope="class")
def ctan_zip_path(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("ctan_zip")
    zip_path = tmp / "omnilatex.zip"
    _build_ctan_zip_with_python(zip_path)
    yield zip_path


@pytest.fixture(scope="class")
def overleaf_zip_path(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("overleaf_zip")
    zip_path = tmp / "omnilatex-overleaf.zip"
    _build_overleaf_zip_with_python("thesis", zip_path)
    yield zip_path


class TestCTANZip:
    def test_zip_is_valid(self, ctan_zip_path):
        assert zipfile.is_zipfile(str(ctan_zip_path)), "omnilatex.zip is not a valid zip"

    def test_zip_contains_omnilatex_cls(self, ctan_zip_path):
        with zipfile.ZipFile(str(ctan_zip_path)) as zf:
            names = zf.namelist()
        assert any(n.endswith("omnilatex.cls") for n in names), (
            "omnilatex.zip missing omnilatex.cls"
        )

    def test_zip_contains_lib_directory(self, ctan_zip_path):
        with zipfile.ZipFile(str(ctan_zip_path)) as zf:
            names = zf.namelist()
        lib_files = [n for n in names if n.startswith("omnilatex/lib/")]
        assert len(lib_files) > 0, "omnilatex.zip missing lib/ directory"

    def test_zip_contains_config_document_types(self, ctan_zip_path):
        with zipfile.ZipFile(str(ctan_zip_path)) as zf:
            names = zf.namelist()
        dt_files = [n for n in names if "document-types" in n and n.endswith(".sty")]
        assert len(dt_files) > 0, "omnilatex.zip missing config/document-types/*.sty"

    def test_zip_contains_document_settings(self, ctan_zip_path):
        with zipfile.ZipFile(str(ctan_zip_path)) as zf:
            names = zf.namelist()
        assert any("document-settings.sty" in n for n in names), (
            "omnilatex.zip missing document-settings.sty"
        )

    def test_zip_contains_bib(self, ctan_zip_path):
        with zipfile.ZipFile(str(ctan_zip_path)) as zf:
            names = zf.namelist()
        assert any("bibliography.bib" in n for n in names), (
            "omnilatex.zip missing bibliography.bib"
        )

    def test_zip_contains_readme(self, ctan_zip_path):
        with zipfile.ZipFile(str(ctan_zip_path)) as zf:
            names = zf.namelist()
        assert any(n.endswith("README.md") for n in names), (
            "omnilatex.zip missing README.md"
        )

    def test_zip_contains_license(self, ctan_zip_path):
        with zipfile.ZipFile(str(ctan_zip_path)) as zf:
            names = zf.namelist()
        assert any(n.endswith("LICENSE") for n in names), (
            "omnilatex.zip missing LICENSE"
        )

    def test_zip_omits_examples(self, ctan_zip_path):
        with zipfile.ZipFile(str(ctan_zip_path)) as zf:
            names = zf.namelist()
        example_files = [n for n in names if "/examples/" in n]
        assert len(example_files) == 0, (
            f"omnilatex.zip should not contain examples/ but found: {example_files[:5]}"
        )

    def test_zip_omits_institutions(self, ctan_zip_path):
        with zipfile.ZipFile(str(ctan_zip_path)) as zf:
            names = zf.namelist()
        inst_files = [n for n in names if "/institutions/" in n]
        assert len(inst_files) == 0, (
            f"omnilatex.zip should not contain institutions/ but found: {inst_files[:5]}"
        )


class TestOverleafZip:
    def test_zip_is_valid(self, overleaf_zip_path):
        assert zipfile.is_zipfile(str(overleaf_zip_path)), (
            "omnilatex-overleaf.zip is not a valid zip"
        )

    def test_zip_contains_main_tex(self, overleaf_zip_path):
        with zipfile.ZipFile(str(overleaf_zip_path)) as zf:
            names = zf.namelist()
        assert any(n.endswith("main.tex") for n in names), (
            "omnilatex-overleaf.zip missing main.tex"
        )

    def test_zip_contains_omnilatex_cls(self, overleaf_zip_path):
        with zipfile.ZipFile(str(overleaf_zip_path)) as zf:
            names = zf.namelist()
        assert any(n.endswith("omnilatex.cls") for n in names), (
            "omnilatex-overleaf.zip missing omnilatex.cls"
        )

    def test_zip_contains_lib(self, overleaf_zip_path):
        with zipfile.ZipFile(str(overleaf_zip_path)) as zf:
            names = zf.namelist()
        lib_files = [n for n in names if "/lib/" in n and n.endswith(".sty")]
        assert len(lib_files) > 0, "omnilatex-overleaf.zip missing lib/*.sty"

    def test_zip_omits_dot_git(self, overleaf_zip_path):
        with zipfile.ZipFile(str(overleaf_zip_path)) as zf:
            names = zf.namelist()
        git_files = [n for n in names if ".git" in n]
        assert len(git_files) == 0, (
            f"omnilatex-overleaf.zip should not contain .git files: {git_files[:5]}"
        )
