"""SSIM-based visual regression diff for PDF comparison."""

from __future__ import annotations

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore[assignment]


def _compute_ssim_windowed(
    arr1: "np.ndarray", arr2: "np.ndarray", window_size: int = 7
) -> float:
    """Sliding-window SSIM (Wang et al. 2004). Returns mean SSIM index."""
    if np is None:
        return 0.0

    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2

    h, w = arr1.shape
    if h < window_size or w < window_size:
        mu1, mu2 = np.mean(arr1), np.mean(arr2)
        sigma1, sigma2 = np.var(arr1), np.var(arr2)
        sigma12 = np.mean((arr1 - mu1) * (arr2 - mu2))
        return ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / (
            (mu1**2 + mu2**2 + C1) * (sigma1 + sigma2 + C2)
        )

    sigma = 1.5
    coords = np.arange(window_size) - window_size // 2
    g1d = np.exp(-(coords**2) / (2 * sigma**2))
    kernel = np.outer(g1d, g1d)
    kernel /= kernel.sum()
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2

    try:
        from scipy.signal import fftconvolve as _scipy_fftconvolve

        def _conv2d(a, k):
            return _scipy_fftconvolve(a, k, mode="same")

    except ImportError:

        def _conv2d(a, k):
            padded = np.pad(a, ((ph, ph), (pw, pw)), mode="constant")
            windows = np.lib.stride_tricks.sliding_window_view(padded, (kh, kw))
            return np.einsum("ijkl,kl->ij", windows, k)

    mu1 = _conv2d(arr1, kernel)
    mu2 = _conv2d(arr2, kernel)
    mu1_sq, mu2_sq, mu12 = mu1 * mu1, mu2 * mu2, mu1 * mu2
    sigma1_sq = _conv2d(arr1 * arr1, kernel) - mu1_sq
    sigma2_sq = _conv2d(arr2 * arr2, kernel) - mu2_sq
    sigma12 = _conv2d(arr1 * arr2, kernel) - mu12

    ssim_map = ((2 * mu12 + C1) * (2 * sigma12 + C2)) / (
        (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
    )
    return float(np.mean(ssim_map))
