"""Unit tests for buildlib.diff module (SSIM computation).

Tests are skipped when numpy is unavailable (e.g. in Nix environments
missing libstdc++).
"""

from __future__ import annotations

import pytest

# Guard: numpy may fail to import if native libs are missing (Nix, etc.)
try:
    import numpy as np

    from buildlib.diff import _compute_ssim_windowed

    _HAS_SSIM = True
except (ImportError, OSError):
    _HAS_SSIM = False

pytestmark = pytest.mark.skipif(
    not _HAS_SSIM,
    reason="numpy or buildlib.diff unavailable in this environment",
)


class TestComputeSsimWindowed:
    """Test SSIM-based visual regression computation."""

    def test_identical_arrays_give_perfect_ssim(self):
        arr = np.random.rand(100, 100).astype(np.float64) * 255
        ssim = _compute_ssim_windowed(arr, arr)
        assert ssim == pytest.approx(1.0, abs=1e-6)

    def test_similar_arrays_give_high_ssim(self):
        arr1 = np.random.rand(100, 100).astype(np.float64) * 255
        arr2 = arr1 + np.random.normal(0, 1, arr1.shape)
        ssim = _compute_ssim_windowed(arr1, arr2)
        assert 0.8 < ssim <= 1.0

    def test_dissimilar_arrays_give_low_ssim(self):
        arr1 = np.zeros((100, 100), dtype=np.float64)
        arr2 = np.ones((100, 100), dtype=np.float64) * 255
        ssim = _compute_ssim_windowed(arr1, arr2)
        assert ssim < 0.5

    def test_small_arrays_use_direct_computation(self):
        """Arrays smaller than window_size should use the fallback path."""
        arr = np.ones((3, 3), dtype=np.float64) * 128
        ssim = _compute_ssim_windowed(arr, arr, window_size=7)
        assert ssim == pytest.approx(1.0, abs=1e-6)

    def test_single_pixel_arrays(self):
        """1x1 arrays should not crash."""
        arr = np.array([[128.0]])
        ssim = _compute_ssim_windowed(arr, arr)
        assert isinstance(ssim, float)

    def test_constant_arrays(self):
        """Constant arrays (no variance) should produce valid SSIM."""
        arr1 = np.full((50, 50), 100.0)
        arr2 = np.full((50, 50), 100.0)
        ssim = _compute_ssim_windowed(arr1, arr2)
        assert ssim == pytest.approx(1.0, abs=1e-4)

    def test_output_is_float(self):
        arr = np.random.rand(50, 50).astype(np.float64)
        result = _compute_ssim_windowed(arr, arr)
        assert isinstance(result, float)

    def test_symmetry(self):
        """SSIM(a, b) should equal SSIM(b, a)."""
        arr1 = np.random.rand(64, 64).astype(np.float64) * 255
        arr2 = np.random.rand(64, 64).astype(np.float64) * 255
        ssim_12 = _compute_ssim_windowed(arr1, arr2)
        ssim_21 = _compute_ssim_windowed(arr2, arr1)
        assert ssim_12 == pytest.approx(ssim_21, abs=1e-6)

    def test_bounded_output(self):
        """SSIM should always be in [-1, 1] range."""
        for _ in range(10):
            arr1 = np.random.rand(32, 32).astype(np.float64) * 255
            arr2 = np.random.rand(32, 32).astype(np.float64) * 255
            ssim = _compute_ssim_windowed(arr1, arr2)
            assert -1.0 <= ssim <= 1.0

    def test_non_square_arrays(self):
        """Non-square arrays should work."""
        arr = np.random.rand(30, 80).astype(np.float64)
        ssim = _compute_ssim_windowed(arr, arr)
        assert ssim == pytest.approx(1.0, abs=1e-6)

    def test_windowed_path_large_arrays(self):
        """Arrays larger than window_size use the Gaussian windowed path."""
        arr = np.random.rand(64, 64).astype(np.float64) * 255
        ssim = _compute_ssim_windowed(arr, arr, window_size=7)
        assert ssim == pytest.approx(1.0, abs=1e-4)

    def test_windowed_path_with_noise(self):
        """Windowed SSIM should detect similarity in noisy images."""
        rng = np.random.default_rng(42)
        arr1 = rng.integers(0, 256, size=(128, 128)).astype(np.float64)
        arr2 = arr1 + rng.normal(0, 5, arr1.shape)
        arr2 = np.clip(arr2, 0, 255)
        ssim = _compute_ssim_windowed(arr1, arr2, window_size=7)
        assert 0.5 < ssim <= 1.0

    def test_windowed_path_different_sizes(self):
        """Test windowed SSIM with various window sizes."""
        arr = np.random.rand(64, 64).astype(np.float64) * 255
        for ws in [5, 7, 11]:
            ssim = _compute_ssim_windowed(arr, arr, window_size=ws)
            assert ssim == pytest.approx(1.0, abs=1e-4)

    def test_small_array_fallback_different_values(self):
        """Small arrays with different values should produce valid SSIM."""
        arr1 = np.full((4, 4), 50.0)
        arr2 = np.full((4, 4), 200.0)
        ssim = _compute_ssim_windowed(arr1, arr2, window_size=7)
        assert isinstance(ssim, float)
        assert -1.0 <= ssim <= 1.0

    def test_rectangular_arrays(self):
        """Rectangular arrays should work with windowed computation."""
        arr = np.random.rand(20, 100).astype(np.float64) * 255
        ssim = _compute_ssim_windowed(arr, arr, window_size=5)
        assert ssim == pytest.approx(1.0, abs=1e-4)

    def test_min_dimension_boundary(self):
        """Arrays where one dimension equals window_size."""
        arr = np.random.rand(7, 100).astype(np.float64) * 255
        ssim = _compute_ssim_windowed(arr, arr, window_size=7)
        assert ssim == pytest.approx(1.0, abs=1e-4)
