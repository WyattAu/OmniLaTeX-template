"""Root-level pytest configuration for OmniLaTeX test suite."""

import pathlib

import pytest

from tests.constants import ALL_DOCTYPE_NAMES, ALL_EXAMPLE_NAMES


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m not slow')"
    )
    config.addinivalue_line(
        "markers", "timeout: mark test with a timeout (handled by pytest-timeout)"
    )


REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture
def repo_root():
    return REPO_ROOT


@pytest.fixture
def all_doctype_names():
    return list(ALL_DOCTYPE_NAMES)


@pytest.fixture
def all_example_names():
    return list(ALL_EXAMPLE_NAMES)
