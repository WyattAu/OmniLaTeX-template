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
