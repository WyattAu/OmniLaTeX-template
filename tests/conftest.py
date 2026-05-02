"""Root-level pytest configuration for OmniLaTeX test suite."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m not slow')"
    )
    # Always register 'timeout' marker so pytest never complains about unknown
    # markers when pytest-timeout is not installed.  If pytest-timeout IS
    # present it will handle the marker automatically.
    config.addinivalue_line(
        "markers", "timeout: mark test with a timeout (handled by pytest-timeout)"
    )


import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root():
    return REPO_ROOT


ALL_DOCTYPE_NAMES = [
    "thesis",
    "dissertation",
    "article",
    "journal",
    "inlinepaper",
    "book",
    "manual",
    "technicalreport",
    "standard",
    "patent",
    "cv",
    "cover-letter",
    "poster",
    "presentation",
    "letter",
    "dictionary",
    "homework",
    "exam",
    "research-proposal",
    "lecture-notes",
    "syllabus",
    "handout",
    "memo",
]


@pytest.fixture
def all_doctype_names():
    return list(ALL_DOCTYPE_NAMES)


ALL_EXAMPLE_NAMES = [
    "accessibility-test",
    "article-color",
    "article",
    "book",
    "citation-styles",
    "cjk-chinese",
    "cjk-japanese",
    "cjk-korean",
    "color-themes",
    "cover-letter-formal",
    "cover-letter",
    "cv-twopage",
    "cv",
    "dictionary",
    "dissertation",
    "exam",
    "handout",
    "homework",
    "inline-paper",
    "journal",
    "lecture-notes",
    "letter",
    "lua-showcase",
    "manual",
    "memo",
    "minimal-custom",
    "minimal-starter",
    "multi-language",
    "poster",
    "presentation",
    "research-proposal",
    "rtl-arabic",
    "rtl-hebrew",
    "standard",
    "syllabus",
    "technical-report",
    "thesis-spacing",
    "thesis-tuhh",
    "thesis",
]


@pytest.fixture
def all_example_names():
    return list(ALL_EXAMPLE_NAMES)
