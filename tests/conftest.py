"""Root-level pytest configuration for OmniLaTeX test suite."""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m not slow')"
    )


def pytest_collection_modifyitems(config, items):
    """Add timeout marker to slow tests if pytest-timeout is available."""
    try:
        import pytest_timeout

        has_timeout = True
    except ImportError:
        has_timeout = False

    if not has_timeout:
        for item in items:
            if item.get_closest_marker("timeout"):
                # Strip the marker so pytest doesn't complain about unknown marker
                item.remove_marker("timeout")
