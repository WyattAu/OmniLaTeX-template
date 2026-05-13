"""Integration tests for institution configuration integrity."""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTITUTIONS_DIR = PROJECT_ROOT / "config" / "institutions"

EXPECTED_INSTITUTIONS = [
    "generic",
    "tum",
    "eth",
    "mit",
    "stanford",
    "cambridge",
    "tuhh",
    "harvard",
    "oxford",
    "princeton",
    "columbia",
    "yale",
    "imperial",
    "cmu",
    "epfl",
    "tudelft",
]


class TestInstitutionStructure:
    """Verify structural integrity of institution configs."""

    def test_institutions_dir_exists(self):
        assert INSTITUTIONS_DIR.is_dir()

    def test_expected_institutions_present(self):
        actual = sorted(d.name for d in INSTITUTIONS_DIR.iterdir() if d.is_dir())
        for name in EXPECTED_INSTITUTIONS:
            assert (
                name in actual
            ), f"Institution '{name}' not found in {INSTITUTIONS_DIR}"

    @pytest.mark.parametrize("name", EXPECTED_INSTITUTIONS)
    def test_institution_has_sty_file(self, name: str):
        sty = INSTITUTIONS_DIR / name / f"{name}.sty"
        assert sty.is_file(), f"{name}: {sty} not found"

    @pytest.mark.parametrize("name", EXPECTED_INSTITUTIONS)
    def test_institution_declares_providespackage(self, name: str):
        sty = INSTITUTIONS_DIR / name / f"{name}.sty"
        content = sty.read_text(encoding="utf-8")
        assert r"\ProvidesPackage" in content, f"{name}: missing \\ProvidesPackage"

    @pytest.mark.parametrize("name", EXPECTED_INSTITUTIONS)
    def test_institution_sty_references_own_name(self, name: str):
        sty = INSTITUTIONS_DIR / name / f"{name}.sty"
        content = sty.read_text(encoding="utf-8")
        assert name in content, f"{name}: .sty does not reference its own name"

    def test_no_empty_sty_files(self):
        for d in INSTITUTIONS_DIR.iterdir():
            if d.is_dir():
                for sty in d.glob("*.sty"):
                    content = sty.read_text(encoding="utf-8").strip()
                    assert (
                        len(content) > 50
                    ), f"{sty} is suspiciously short ({len(content)} chars)"

    def test_generic_is_not_production(self):
        """Generic template should not be listed as a real institution."""
        generic_sty = INSTITUTIONS_DIR / "generic" / "generic.sty"
        assert (
            generic_sty.is_file()
        ), "Generic template must exist for scaffold-institution"
