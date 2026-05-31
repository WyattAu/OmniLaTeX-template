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

from tests.constants import ALL_DOCTYPE_NAMES
from tests.constants import DOCTYPE_ALIASES as _DOCTYPE_ALIAS_MAP
from tests.constants import DOCTYPE_TO_CLASS

try:
    from hypothesis import HealthCheck, given, settings
    from hypothesis.strategies import sampled_from

    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

    def given(**kwargs):
        def decorator(f):
            return f

        return decorator

    class _DummySettings:
        def __init__(self, **kwargs):
            pass

        def __call__(self, f):
            return f

    settings = _DummySettings

    def sampled_from(items):
        return items

    class HealthCheck:
        too_slow = None


_hypothesis_skip = pytest.mark.skipif(
    not HAS_HYPOTHESIS, reason="hypothesis not installed"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _check_docker() -> bool:
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


DOCKER_AVAILABLE = _check_docker()


def _get_docker_image() -> str:
    env_file = PROJECT_ROOT / ".env.docker"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DOCKER_IMAGE=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip()
    return "ghcr.io/wyattau/omnilatex-docker:latest"


DOCKER_IMAGE = _get_docker_image()


def _check_docker_image() -> bool:
    """Check that the specific Docker image is available and Docker can run containers."""
    if not DOCKER_AVAILABLE:
        return False
    try:
        # First check image exists
        inspect = subprocess.run(
            ["docker", "image", "inspect", DOCKER_IMAGE],
            capture_output=True,
            timeout=15,
        )
        if inspect.returncode != 0:
            return False
        # Then verify Docker can actually start a container
        result = subprocess.run(
            ["docker", "run", "--rm", "--entrypoint", "", DOCKER_IMAGE, "echo", "ok"],
            capture_output=True,
            timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


DOCKER_IMAGE_AVAILABLE = _check_docker_image()

docker_required = pytest.mark.skipif(
    not DOCKER_IMAGE_AVAILABLE,
    reason=f"Docker image not available locally: {DOCKER_IMAGE}",
)

# Use canonical alias list from constants (minus None entries for examples without doctype)
DOCTYPE_ALIASES = [d for d in ALL_DOCTYPE_NAMES]

LANGUAGES = ["english", "german"]

TEMPLATE = r"""
\documentclass[{options}]{{omnilatex}}
\title{{Test Document}}
\begin{{document}}
Test content for {{doctype}}.
\end{{document}}
"""


@pytest.fixture
def docker_available():
    return DOCKER_AVAILABLE


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


def compile_tex_docker(tex_content: str, timeout: int = 180) -> tuple:
    """Compile tex content in Docker. Returns (success, log_excerpt)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = Path(tmpdir) / "test.tex"
        tex_file.write_text(tex_content)
        cmd = [
            "docker",
            "run",
            "--rm",
            "--entrypoint",
            "",
            "-e",
            "TEXINPUTS=/repo:",
            "-v",
            f"{PROJECT_ROOT}:/repo",
            "-v",
            f"{tmpdir}:/work",
            "-w",
            "/work",
            DOCKER_IMAGE,
            "latexmk",
            "-lualatex",
            "-interaction=nonstopmode",
            "-output-directory=/work",
            "test.tex",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        pdf_exists = (Path(tmpdir) / "test.pdf").exists()
        return (
            result.returncode == 0 and pdf_exists,
            result.stdout[-500:] if result.stdout else "",
        )


class TestDoctypeCompilation:
    """Test that every valid doctype compiles."""

    @pytest.mark.slow
    @docker_required
    @pytest.mark.timeout(120)
    @pytest.mark.parametrize("doctype", DOCTYPE_ALIASES)
    @pytest.mark.parametrize("language", LANGUAGES)
    def test_doctype_language_combination(self, doctype, language):
        options = f"doctype={doctype},language={language}"
        tex = TEMPLATE.format(options=options, doctype=doctype)
        success, log = compile_tex_docker(tex)
        assert success, f"Failed: {doctype}/{language}\nLog tail: {log}"


@_hypothesis_skip
class TestPropertyBasedFuzzing:
    """Fuzz test with hypothesis."""

    @pytest.mark.slow
    @docker_required
    @pytest.mark.timeout(300)
    @given(doctype=sampled_from(DOCTYPE_ALIASES))
    @settings(
        max_examples=20, deadline=None, suppress_health_check=[HealthCheck.too_slow]
    )
    def test_random_doctype_compiles(self, doctype):
        tex = TEMPLATE.format(options=f"doctype={doctype}", doctype=doctype)
        success, _ = compile_tex_docker(tex)
        assert success


class TestStructuralProperties:
    """Static structural property tests for OmniLaTeX configuration."""

    VALID_KOMA_CLASSES = {"scrartcl", "scrbook", "scrreprt", "beamer"}

    CANONICAL_DOCTYPES = [
        "article",
        "book",
        "cover-letter",
        "cv",
        "dictionary",
        "dissertation",
        "exam",
        "handout",
        "homework",
        "inlinepaper",
        "invoice",
        "journal",
        "lecture-notes",
        "letter",
        "manual",
        "memo",
        "patent",
        "poster",
        "presentation",
        "recipe",
        "research-proposal",
        "standard",
        "syllabus",
        "technicalreport",
        "thesis",
        "white-paper",
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
            d.name for d in inst_dir.iterdir() if d.is_dir() and d.name != "README.md"
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
                    doctype = m.group(1)
                    # Normalize aliases to canonical doctype names
                    doctype = _DOCTYPE_ALIAS_MAP.get(doctype, doctype)
                    if doctype is not None:
                        result[ex_dir.name] = doctype
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

    @_hypothesis_skip
    @given(doctype=sampled_from(list(DOCTYPE_TO_CLASS.keys())))
    @settings(max_examples=50, deadline=None)
    def test_doctype_maps_to_valid_koma_class(self, doctype):
        koma_class = DOCTYPE_TO_CLASS[doctype]
        assert (
            koma_class in self.VALID_KOMA_CLASSES
        ), f"doctype '{doctype}' maps to '{koma_class}', not a valid KOMA class"

    def test_all_doctype_files_map_to_koma_classes(self):
        doctype_names = self._get_doctype_names()
        assert len(doctype_names) > 0, "No doctype .sty files found"
        for name in doctype_names:
            assert (
                name in DOCTYPE_TO_CLASS
            ), f"Doctype file '{name}.sty' has no mapping in DOCTYPE_TO_CLASS"
            koma_class = DOCTYPE_TO_CLASS[name]
            assert (
                koma_class in self.VALID_KOMA_CLASSES
            ), f"Doctype '{name}' maps to invalid KOMA class '{koma_class}'"

    @_hypothesis_skip
    @given(institution=sampled_from(list(_get_institution_names(None) or ["generic"])))
    @settings(max_examples=20, deadline=None)
    def test_institution_has_valid_providespackage(self, institution):
        inst_dir = PROJECT_ROOT / "config" / "institutions" / institution
        sty_files = list(inst_dir.glob("*.sty")) if inst_dir.is_dir() else []
        assert len(sty_files) > 0, f"No .sty file in institution '{institution}'"
        for sty_file in sty_files:
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            assert (
                "\\ProvidesPackage" in content
            ), f"{sty_file.relative_to(PROJECT_ROOT)} missing \\ProvidesPackage"

    def test_all_institutions_have_providespackage(self):
        institutions = self._get_institution_names()
        assert len(institutions) > 0, "No institution directories found"
        for inst in institutions:
            inst_dir = PROJECT_ROOT / "config" / "institutions" / inst
            sty_files = list(inst_dir.glob("*.sty"))
            assert len(sty_files) > 0, f"No .sty in institution '{inst}'"
            for sty_file in sty_files:
                content = sty_file.read_text(encoding="utf-8", errors="replace")
                assert (
                    "\\ProvidesPackage" in content
                ), f"{sty_file.relative_to(PROJECT_ROOT)} missing \\ProvidesPackage"

    def test_translation_key_parity(self):
        counts = self._get_translation_counts()
        assert len(counts) > 0, "No translations found in i18n module"
        values = list(counts.values())
        assert all(
            v == values[0] for v in values
        ), f"Translation key counts are not equal across languages: {counts}"

    @_hypothesis_skip
    @given(example=sampled_from(list(_get_example_doctypes(None).keys()) or ["thesis"]))
    @settings(max_examples=30, deadline=None)
    def test_example_doctype_is_registered(self, example):
        example_doctypes = self._get_example_doctypes()
        if not example_doctypes:
            pytest.skip("No examples found")
        doctype = example_doctypes[example]
        assert (
            doctype in DOCTYPE_TO_CLASS
        ), f"Example '{example}' uses doctype '{doctype}' which is not registered"

    def test_all_examples_use_registered_doctypes(self):
        example_doctypes = self._get_example_doctypes()
        assert len(example_doctypes) > 0, "No examples with doctypes found"
        for ex_name, doctype in example_doctypes.items():
            assert (
                doctype in DOCTYPE_TO_CLASS
            ), f"Example '{ex_name}' uses unregistered doctype '{doctype}'"

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

    @_hypothesis_skip
    @given(pkg=sampled_from(list(_get_require_packages(None))))
    @settings(max_examples=50, deadline=None)
    def test_each_module_exists(self, pkg):
        if not pkg.startswith("lib/"):
            return
        pkg_path = PROJECT_ROOT / (pkg + ".sty")
        assert (
            pkg_path.is_file()
        ), f"\\RequirePackage{{{pkg}}}: {pkg_path.relative_to(PROJECT_ROOT)} not found"

    def test_i18n_language_coverage_matrix(self):
        """Verify all languages with translations have consistent key counts."""
        i18n_file = PROJECT_ROOT / "lib" / "language" / "omnilatex-i18n.sty"
        content = i18n_file.read_text(encoding="utf-8", errors="replace")
        import re
        from collections import Counter

        counts = Counter()
        for m in re.finditer(r"\\DeclareTranslation\{(\w+)\}\{", content):
            counts[m.group(1)] += 1
        values = list(counts.values())
        assert len(values) > 0, "No translations found"
        assert all(
            v == values[0] for v in values
        ), f"Translation key counts not equal: {dict(counts)}"

    def test_no_duplicate_translation_keys(self):
        dupes = self._get_translation_key_dupes()
        assert len(dupes) == 0, f"Duplicate translation keys found: {dupes}"

    @_hypothesis_skip
    @given(doctype=sampled_from(CANONICAL_DOCTYPES))
    @settings(max_examples=50, deadline=None)
    def test_doctype_sty_file_exists(self, doctype):
        sty_path = PROJECT_ROOT / "config" / "document-types" / f"{doctype}.sty"
        assert sty_path.is_file(), f"Doctype config not found: {sty_path}"


class TestLeanProofConsistency:
    """Verify Lean 4 proof files match repository structure."""

    def test_all_proof_modules_imported(self):
        """Root OmniLaTeXProofs.lean imports all proof modules."""
        root = PROJECT_ROOT / "specs" / "proofs" / "OmniLaTeXProofs.lean"
        assert root.is_file(), "Root proof file not found"
        content = root.read_text(encoding="utf-8")
        proof_dir = PROJECT_ROOT / "specs" / "proofs" / "OmniLaTeXProofs"
        modules = sorted(p.stem for p in proof_dir.glob("*.lean"))
        for mod in modules:
            assert (
                f"import OmniLaTeXProofs.{mod}" in content
            ), f"Module '{mod}' not imported in root proof file"

    def test_no_sorry_in_proofs(self):
        """Zero sorry in all proof files."""
        proof_dir = PROJECT_ROOT / "specs" / "proofs"
        for lean_file in proof_dir.rglob("*.lean"):
            content = lean_file.read_text(encoding="utf-8")
            for i, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("--") or stripped.startswith("/-"):
                    continue
                if "sorry" in stripped and "No " not in stripped:
                    assert (
                        False
                    ), f"{lean_file.relative_to(PROJECT_ROOT)}:{i} contains 'sorry'"

    def test_proof_module_count(self):
        """At least 10 proof modules in OmniLaTeXProofs/."""
        proof_dir = PROJECT_ROOT / "specs" / "proofs" / "OmniLaTeXProofs"
        modules = list(proof_dir.glob("*.lean"))
        assert len(modules) >= 10, f"Expected >= 10 proof modules, found {len(modules)}"

    def test_lakefile_exists(self):
        """lakefile.toml exists in specs/proofs/."""
        lakefile = PROJECT_ROOT / "specs" / "proofs" / "lakefile.toml"
        assert lakefile.is_file(), "lakefile.toml not found"


class TestStyFileConsistency:
    """Verify .sty files in lib/ are well-formed and consistent."""

    def _get_lib_sty_files(self) -> list[Path]:
        lib_dir = PROJECT_ROOT / "lib"
        if not lib_dir.is_dir():
            return []
        return sorted(lib_dir.rglob("*.sty"))

    def _get_cls_version(self) -> str:
        cls_file = PROJECT_ROOT / "omnilatex.cls"
        content = cls_file.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"\\ProvidesClass\{omnilatex\}\[([^\]]+)\]", content)
        return m.group(1) if m else ""

    def _get_lib_packages_from_cls(self) -> set[str]:
        cls_file = PROJECT_ROOT / "omnilatex.cls"
        content = cls_file.read_text(encoding="utf-8", errors="replace")
        packages = set()
        for m in re.finditer(
            r"\\RequirePackage(?:\[[^\]]*\])?\{lib/([^}]+)\}", content
        ):
            packages.add(m.group(1))
        return packages

    def _get_lib_packages_from_doctypes(self) -> set[str]:
        dt_dir = PROJECT_ROOT / "config" / "document-types"
        packages = set()
        if not dt_dir.is_dir():
            return packages
        for sty_file in dt_dir.glob("*.sty"):
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            for m in re.finditer(
                r"\\RequirePackage(?:\[[^\]]*\])?\{lib/([^}]+)\}", content
            ):
                packages.add(m.group(1))
        return packages

    def test_lib_sty_files_have_providespackage(self):
        sty_files = self._get_lib_sty_files()
        assert len(sty_files) > 0, "No .sty files found in lib/"
        for sty_file in sty_files:
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            assert (
                "\\ProvidesPackage" in content
            ), f"{sty_file.relative_to(PROJECT_ROOT)} missing \\ProvidesPackage"

    def test_lib_sty_providespackage_path_matches_file(self):
        for sty_file in self._get_lib_sty_files():
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"\\ProvidesPackage\{([^}]+)\}", content)
            assert m, f"{sty_file.name} has no \\ProvidesPackage"
            pkg_path = m.group(1)
            rel = sty_file.relative_to(PROJECT_ROOT).with_suffix("")
            expected = str(rel)
            assert (
                pkg_path == expected
            ), f"{sty_file.name}: \\ProvidesPackage{{{pkg_path}}} != expected path '{expected}'"

    def test_lib_sty_files_have_version_string(self):
        for sty_file in self._get_lib_sty_files():
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            content = re.sub(r"%\n\s*", " ", content)
            m = re.search(r"\\ProvidesPackage\{[^}]+\}\s*\[([^\]]*)\]", content)
            assert m, f"{sty_file.name}: \\ProvidesPackage has no version bracket"

    def test_lib_sty_files_have_latex2e_header(self):
        for sty_file in self._get_lib_sty_files():
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            assert (
                "\\NeedsTeXFormat{LaTeX2e}" in content
            ), f"{sty_file.relative_to(PROJECT_ROOT)} missing \\NeedsTeXFormat{{LaTeX2e}}"

    def test_no_orphaned_lib_sty_files(self):
        cls_packages = self._get_lib_packages_from_cls()
        dt_packages = self._get_lib_packages_from_doctypes()
        all_referenced = cls_packages | dt_packages
        on_demand = {
            "graphics/omnilatex-beamer",
            "layout/omnilatex-accessibility",
            "references/omnilatex-citations",
            "utils/omnilatex-themes",
            "utils/omnilatex-review",
            "utils/omnilatex-todo",
            "utils/omnilatex-plugin",
        }
        all_known = all_referenced | on_demand
        for sty_file in self._get_lib_sty_files():
            rel = sty_file.relative_to(PROJECT_ROOT / "lib")
            pkg_id = str(rel.with_suffix(""))
            assert pkg_id in all_known, (
                f"{sty_file.name} is not referenced by "
                f"omnilatex.cls, doctypes, or marked as on-demand"
            )

    def test_cls_requirepackage_lib_files_exist(self):
        cls_packages = self._get_lib_packages_from_cls()
        assert len(cls_packages) > 0, "No lib/ \\RequirePackage found in omnilatex.cls"
        for pkg_id in cls_packages:
            pkg_path = PROJECT_ROOT / "lib" / f"{pkg_id}.sty"
            assert (
                pkg_path.is_file()
            ), f"\\RequirePackage{{lib/{pkg_id}}}: {pkg_path.relative_to(PROJECT_ROOT)} not found"


class TestInstitutionConfigs:
    """Verify institution configuration .sty files are consistent."""

    def _get_institution_dirs(self) -> list[Path]:
        inst_dir = PROJECT_ROOT / "config" / "institutions"
        if not inst_dir.is_dir():
            return []
        return sorted(
            d for d in inst_dir.iterdir() if d.is_dir() and not d.name.startswith(".")
        )

    def _get_institution_sty(self, inst_dir: Path) -> Path | None:
        sty_files = list(inst_dir.glob("*.sty"))
        return sty_files[0] if sty_files else None

    @pytest.mark.parametrize(
        "inst_dir",
        _get_institution_dirs(None)
        or [PROJECT_ROOT / "config" / "institutions" / "generic"],
        indirect=False,
    )
    def test_institution_dir_has_sty_file(self, inst_dir):
        assert inst_dir.is_dir(), f"Institution dir missing: {inst_dir}"
        sty_files = list(inst_dir.glob("*.sty"))
        assert len(sty_files) > 0, f"No .sty file in {inst_dir.name}/"

    def test_all_institution_dirs_have_sty_file(self):
        inst_dirs = self._get_institution_dirs()
        assert len(inst_dirs) > 0, "No institution directories found"
        for inst_dir in inst_dirs:
            sty_files = list(inst_dir.glob("*.sty"))
            assert len(sty_files) > 0, f"No .sty in institution '{inst_dir.name}'"

    def test_institution_sty_has_matching_providespackage(self):
        for inst_dir in self._get_institution_dirs():
            sty = self._get_institution_sty(inst_dir)
            assert sty is not None, f"No .sty in {inst_dir.name}/"
            content = sty.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"\\ProvidesPackage\{([^}]+)\}", content)
            assert m, f"{sty.name} missing \\ProvidesPackage"
            expected_suffix = f"/{inst_dir.name}/{inst_dir.name}"
            assert m.group(1).endswith(expected_suffix), (
                f"{sty.name}: \\ProvidesPackage path "
                f"'{m.group(1)}' doesn't end with '{expected_suffix}'"
            )

    def test_institution_sty_has_needs_tex_format(self):
        for inst_dir in self._get_institution_dirs():
            sty = self._get_institution_sty(inst_dir)
            assert sty is not None, f"No .sty in {inst_dir.name}/"
            content = sty.read_text(encoding="utf-8", errors="replace")
            assert (
                "\\NeedsTeXFormat{LaTeX2e}" in content
            ), f"{sty.relative_to(PROJECT_ROOT)} missing \\NeedsTeXFormat{{LaTeX2e}}"

    def test_institution_sty_has_date_in_providespackage(self):
        for inst_dir in self._get_institution_dirs():
            sty = self._get_institution_sty(inst_dir)
            assert sty is not None, f"No .sty in {inst_dir.name}/"
            content = sty.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"\\ProvidesPackage\{[^}]+\}\[([^\]]+)\]", content)
            assert m, f"{sty.name} has no version/date in \\ProvidesPackage"
            date_part = m.group(1).split()[0]
            assert re.match(
                r"\d{4}[-/]\d{2}[-/]\d{2}", date_part
            ), f"{sty.name}: date '{date_part}' doesn't match YYYY-MM-DD or YYYY/MM/DD"

    def test_no_duplicate_institution_names(self):
        inst_dirs = self._get_institution_dirs()
        names = [d.name for d in inst_dirs]
        counts = Counter(names)
        dupes = {name: count for name, count in counts.items() if count > 1}
        assert len(dupes) == 0, f"Duplicate institution names: {dupes}"

    def test_institution_sty_count(self):
        inst_dirs = self._get_institution_dirs()
        assert (
            len(inst_dirs) >= 20
        ), f"Expected >= 20 institution configs, found {len(inst_dirs)}"


class TestDocumentTypeConfigs:
    """Verify document-type configuration .sty files are consistent."""

    def _get_doctype_sty_files(self) -> list[Path]:
        dt_dir = PROJECT_ROOT / "config" / "document-types"
        if not dt_dir.is_dir():
            return []
        return sorted(dt_dir.glob("*.sty"))

    def test_doctype_sty_files_exist(self):
        sty_files = self._get_doctype_sty_files()
        assert len(sty_files) > 0, "No doctype .sty files found"

    def test_doctype_sty_has_matching_providespackage(self):
        for sty_file in self._get_doctype_sty_files():
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"\\ProvidesPackage\{([^}]+)\}", content)
            assert m, f"{sty_file.name} missing \\ProvidesPackage"
            expected = f"config/document-types/{sty_file.stem}"
            assert (
                m.group(1) == expected
            ), f"{sty_file.name}: \\ProvidesPackage path '{m.group(1)}' != expected '{expected}'"

    def test_doctype_sty_has_citationstyle(self):
        for sty_file in self._get_doctype_sty_files():
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            # Beamer skips biblatex entirely (incompatible with beamer's
            # built-in hyperref), so citation style is not required.
            if sty_file.stem == "beamer":
                continue
            assert (
                "\\citationstyle" in content
            ), f"{sty_file.name} missing \\citationstyle{{}} call"

    def test_doctype_sty_ends_with_endinput(self):
        for sty_file in self._get_doctype_sty_files():
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            stripped = content.rstrip()
            assert stripped.endswith(
                "\\endinput"
            ), f"{sty_file.name} does not end with \\endinput"

    def test_doctype_sty_has_needs_tex_format(self):
        for sty_file in self._get_doctype_sty_files():
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            assert (
                "\\NeedsTeXFormat{LaTeX2e}" in content
            ), f"{sty_file.name} missing \\NeedsTeXFormat{{LaTeX2e}}"

    def test_doctype_count_matches_constants(self):
        sty_files = self._get_doctype_sty_files()
        assert len(sty_files) == len(ALL_DOCTYPE_NAMES), (
            f"Doctype .sty count ({len(sty_files)}) != "
            f"ALL_DOCTYPE_NAMES count ({len(ALL_DOCTYPE_NAMES)})"
        )

    def test_all_doctype_names_have_sty_file(self):
        sty_names = {p.stem for p in self._get_doctype_sty_files()}
        for name in ALL_DOCTYPE_NAMES:
            assert (
                name in sty_names
            ), f"ALL_DOCTYPE_NAMES '{name}' has no matching .sty file"


class TestFileStructureIntegrity:
    """Verify project file structure is well-formed."""

    REQUIRED_DIRS = ["lib", "config", "examples", "docs"]

    def test_omnilatex_cls_exists_and_readable(self):
        cls_file = PROJECT_ROOT / "omnilatex.cls"
        assert cls_file.is_file(), "omnilatex.cls not found"
        content = cls_file.read_text(encoding="utf-8")
        assert len(content) > 0, "omnilatex.cls is empty"

    def test_required_directories_exist(self):
        for dirname in self.REQUIRED_DIRS:
            dir_path = PROJECT_ROOT / dirname
            assert dir_path.is_dir(), f"Required directory '{dirname}/' not found"

    def test_all_example_dirs_have_main_tex(self):
        examples_dir = PROJECT_ROOT / "examples"
        assert examples_dir.is_dir(), "examples/ directory not found"
        for ex_dir in examples_dir.iterdir():
            if not ex_dir.is_dir() or ex_dir.name.startswith("."):
                continue
            main_tex = ex_dir / "main.tex"
            assert main_tex.is_file(), f"Example '{ex_dir.name}/' missing main.tex"

    def test_lib_sty_files_use_utf8(self):
        lib_dir = PROJECT_ROOT / "lib"
        for sty_file in lib_dir.rglob("*.sty"):
            try:
                sty_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{sty_file.relative_to(PROJECT_ROOT)} is not valid UTF-8")

    def test_doctype_sty_files_use_utf8(self):
        dt_dir = PROJECT_ROOT / "config" / "document-types"
        for sty_file in dt_dir.glob("*.sty"):
            try:
                sty_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{sty_file.relative_to(PROJECT_ROOT)} is not valid UTF-8")

    def test_institution_sty_files_use_utf8(self):
        inst_dir = PROJECT_ROOT / "config" / "institutions"
        for sty_file in inst_dir.rglob("*.sty"):
            try:
                sty_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                pytest.fail(f"{sty_file.relative_to(PROJECT_ROOT)} is not valid UTF-8")

    def test_omnilatex_cls_has_providesclass(self):
        cls_file = PROJECT_ROOT / "omnilatex.cls"
        content = cls_file.read_text(encoding="utf-8")
        assert (
            "\\ProvidesClass{omnilatex}" in content
        ), "omnilatex.cls missing \\ProvidesClass{omnilatex}"

    def test_omnilatex_cls_has_needs_tex_format(self):
        cls_file = PROJECT_ROOT / "omnilatex.cls"
        content = cls_file.read_text(encoding="utf-8")
        assert (
            "\\NeedsTeXFormat{LaTeX2e}" in content
        ), "omnilatex.cls missing \\NeedsTeXFormat{LaTeX2e}"

    def test_no_circular_input_in_lib_sty(self):
        lib_dir = PROJECT_ROOT / "lib"
        for sty_file in lib_dir.rglob("*.sty"):
            content = sty_file.read_text(encoding="utf-8", errors="replace")
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("%"):
                    continue
                m = re.match(r"\\input\{(.+?)\}", stripped)
                if m:
                    input_path = m.group(1)
                    assert not input_path.startswith("lib/"), (
                        f"{sty_file.relative_to(PROJECT_ROOT)}: "
                        f"\\input{{{input_path}}} creates potential circular dependency in lib/"
                    )

    def test_config_document_settings_sty_exists(self):
        settings = PROJECT_ROOT / "config" / "omnilatex-document-settings.sty"
        assert settings.is_file(), "config/omnilatex-document-settings.sty not found"

    def test_lib_subdirectories_nonempty(self):
        lib_dir = PROJECT_ROOT / "lib"
        for subdir in sorted(lib_dir.iterdir()):
            if not subdir.is_dir() or subdir.name.startswith("."):
                continue
            sty_files = list(subdir.glob("*.sty"))
            assert len(sty_files) > 0, f"lib/{subdir.name}/ has no .sty files"

    @_hypothesis_skip
    @given(doctype=sampled_from(ALL_DOCTYPE_NAMES))
    @settings(max_examples=50, deadline=None)
    def test_doctype_sty_is_self_contained(self, doctype):
        sty_path = PROJECT_ROOT / "config" / "document-types" / f"{doctype}.sty"
        assert sty_path.is_file(), f"Missing {sty_path}"
        content = sty_path.read_text(encoding="utf-8", errors="replace")
        assert "\\NeedsTeXFormat" in content
        assert "\\ProvidesPackage" in content
        # Beamer skips biblatex (incompatible with beamer's hyperref)
        if doctype != "beamer":
            assert "\\citationstyle" in content
        assert "\\endinput" in content


class TestDockerDigestConsistency:
    """Verify Docker image digest is consistent across all CI configs."""

    def _get_digest_from_env(self) -> str:
        env_file = PROJECT_ROOT / ".env.docker"
        if not env_file.is_file():
            return ""
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("DOCKER_IMAGE=") and not line.startswith("#"):
                return line.split("=", 1)[1].strip()
        return ""

    def test_env_docker_has_digest(self):
        digest = self._get_digest_from_env()
        assert digest != "", ".env.docker has no DOCKER_IMAGE"
        assert digest.startswith(
            "ghcr.io/wyattau/omnilatex-docker@"
        ), f"Unexpected image format: {digest}"

    def test_github_workflows_use_consistent_digest(self):
        """All GitHub workflow files reference the same digest as .env.docker."""
        canonical = self._get_digest_from_env()
        if not canonical:
            pytest.skip(".env.docker not found")
        wf_dir = PROJECT_ROOT / ".github" / "workflows"
        for wf in wf_dir.glob("*.yml"):
            content = wf.read_text(encoding="utf-8")
            digests = re.findall(r"sha256:[a-f0-9]{64}", content)
            for d in digests:
                assert d in canonical or canonical.endswith(
                    d
                ), f"{wf.name}: digest {d[:20]}... doesn't match .env.docker"

    def test_no_latest_tag_in_workflows(self):
        """No :latest tag in GitHub workflow files (except digest-sync)."""
        wf_dir = PROJECT_ROOT / ".github" / "workflows"
        for wf in wf_dir.glob("*.yml"):
            if "digest-sync" in wf.name:
                continue
            content = wf.read_text(encoding="utf-8")
            assert ":latest" not in content, f"{wf.name} uses unpinned :latest tag"
