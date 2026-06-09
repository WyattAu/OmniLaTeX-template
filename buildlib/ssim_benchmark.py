"""SSIM computation benchmarking.

Benchmarks SSIM performance across image sizes, compares windowed vs
full-image computation, and reports throughput statistics.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from statistics import mean, median
from typing import Any

try:
    import numpy as np

    _HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore[assignment]
    _HAS_NUMPY = False

from buildlib.diff import _compute_ssim_windowed

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""

    method: str
    width: int
    height: int
    elapsed_s: float
    images_per_sec: float
    window_size: int = 7

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkSuite:
    """Aggregated benchmark results."""

    generated: str = ""
    results: list[BenchmarkResult] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated": self.generated,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
        }


# ---------------------------------------------------------------------------
# Benchmark runner
# ---------------------------------------------------------------------------


class SSIMBenchmark:
    """Benchmark SSIM computation across different configurations."""

    DEFAULT_SIZES = [
        (64, 64),
        (128, 128),
        (256, 256),
        (512, 512),
        (1024, 1024),
        (2048, 2048),
        (100, 300),
        (300, 100),
    ]
    DEFAULT_WINDOW_SIZES = [5, 7, 11]
    DEFAULT_ITERATIONS = 3

    def __init__(
        self,
        sizes: list[tuple[int, int]] | None = None,
        window_sizes: list[int] | None = None,
        iterations: int = DEFAULT_ITERATIONS,
    ):
        if not _HAS_NUMPY:
            raise ImportError("numpy is required for SSIM benchmarks")
        self.sizes = sizes or self.DEFAULT_SIZES
        self.window_sizes = window_sizes or self.DEFAULT_WINDOW_SIZES
        self.iterations = iterations

    def _make_pair(self, h: int, w: int) -> tuple["np.ndarray", "np.ndarray"]:
        """Create a pair of random arrays for benchmarking."""
        rng = np.random.default_rng(42)
        arr1 = rng.integers(0, 256, size=(h, w), dtype=np.uint8).astype(np.float64)
        arr2 = arr1 + rng.normal(0, 2, arr1.shape).astype(np.float64)
        arr2 = np.clip(arr2, 0, 255)
        return arr1, arr2

    def benchmark_windowed(
        self, h: int, w: int, window_size: int = 7, iterations: int | None = None
    ) -> BenchmarkResult:
        """Benchmark windowed SSIM for a given image size."""
        iters = iterations or self.iterations
        arr1, arr2 = self._make_pair(h, w)

        times = []
        for _ in range(iters):
            start = time.perf_counter()
            _compute_ssim_windowed(arr1, arr2, window_size=window_size)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg = mean(times)
        throughput = 1.0 / avg if avg > 0 else 0.0
        return BenchmarkResult(
            method="windowed",
            width=w,
            height=h,
            elapsed_s=round(avg, 6),
            images_per_sec=round(throughput, 2),
            window_size=window_size,
        )

    def benchmark_full_image(
        self, h: int, w: int, iterations: int | None = None
    ) -> BenchmarkResult:
        """Benchmark full-image (non-windowed) SSIM as a baseline.

        For images smaller than any window size, delegates to the windowed
        function with the smallest supported window so the results are
        comparable.
        """
        iters = iterations or self.iterations
        arr1, arr2 = self._make_pair(h, w)

        times = []
        for _ in range(iters):
            start = time.perf_counter()
            # Reuse the windowed implementation with a small window as the
            # non-windowed path is already embedded inside
            # _compute_ssim_windowed for undersized images.
            _compute_ssim_windowed(arr1, arr2, window_size=1)
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        avg = mean(times)
        throughput = 1.0 / avg if avg > 0 else 0.0
        return BenchmarkResult(
            method="full_image",
            width=w,
            height=h,
            elapsed_s=round(avg, 6),
            images_per_sec=round(throughput, 2),
            window_size=0,
        )

    def run_all(self) -> BenchmarkSuite:
        """Run the full benchmark suite across all sizes and methods."""
        suite = BenchmarkSuite()
        suite.generated = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        for h, w in self.sizes:
            # Full image baseline
            result = self.benchmark_full_image(h, w)
            suite.results.append(result)

            # Windowed with different window sizes
            for ws in self.window_sizes:
                if ws <= min(h, w):
                    result = self.benchmark_windowed(h, w, window_size=ws)
                    suite.results.append(result)

        suite.summary = self._compute_summary(suite.results)
        return suite

    def _compute_summary(self, results: list[BenchmarkResult]) -> dict[str, Any]:
        """Compute aggregate statistics from benchmark results."""
        if not results:
            return {}

        by_method: dict[str, list[BenchmarkResult]] = {}
        for r in results:
            by_method.setdefault(r.method, []).append(r)

        summary: dict[str, Any] = {"methods": {}}

        for method, method_results in by_method.items():
            throughputs = [r.images_per_sec for r in method_results]
            times = [r.elapsed_s for r in method_results]
            summary["methods"][method] = {
                "count": len(method_results),
                "mean_throughput": round(mean(throughputs), 2),
                "median_throughput": round(median(throughputs), 2),
                "min_throughput": round(min(throughputs), 2),
                "max_throughput": round(max(throughputs), 2),
                "mean_time_s": round(mean(times), 6),
            }

        # Speedup comparison
        if "windowed" in by_method and "full_image" in by_method:
            full_throughputs = [r.images_per_sec for r in by_method["full_image"]]
            win_throughputs = [r.images_per_sec for r in by_method["windowed"]]
            avg_full = mean(full_throughputs) if full_throughputs else 0
            avg_win = mean(win_throughputs) if win_throughputs else 0
            summary["windowed_vs_full"] = {
                "avg_full_throughput": round(avg_full, 2),
                "avg_windowed_throughput": round(avg_win, 2),
                "speedup_ratio": round(avg_win / avg_full, 2) if avg_full > 0 else 0,
            }

        sizes = sorted(set((r.width, r.height) for r in results))
        summary["sizes_tested"] = [f"{w}x{h}" for h, w in sizes]

        return summary

    def compare_methods(
        self, h: int, w: int, iterations: int | None = None
    ) -> dict[str, Any]:
        """Compare windowed vs full-image SSIM for a specific size."""
        full = self.benchmark_full_image(h, w, iterations=iterations)
        windowed = self.benchmark_windowed(h, w, iterations=iterations)

        speedup = full.elapsed_s / windowed.elapsed_s if windowed.elapsed_s > 0 else 0
        return {
            "size": f"{w}x{h}",
            "full_image": full.to_dict(),
            "windowed": windowed.to_dict(),
            "speedup": round(speedup, 2),
            "windowed_faster": windowed.elapsed_s < full.elapsed_s,
        }
