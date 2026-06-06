"""Unit tests for buildlib.ssim_benchmark module."""

from __future__ import annotations

import pytest

try:

    _HAS_NUMPY = True
except (ImportError, OSError):
    _HAS_NUMPY = False

from buildlib.ssim_benchmark import (
    BenchmarkResult,
    BenchmarkSuite,
    SSIMBenchmark,
)

pytestmark = pytest.mark.skipif(
    not _HAS_NUMPY,
    reason="numpy unavailable in this environment",
)


# ---------------------------------------------------------------------------
# BenchmarkResult
# ---------------------------------------------------------------------------


class TestBenchmarkResult:
    def test_to_dict(self):
        r = BenchmarkResult(
            method="windowed",
            width=128,
            height=128,
            elapsed_s=0.01,
            images_per_sec=100.0,
            window_size=7,
        )
        d = r.to_dict()
        assert d["method"] == "windowed"
        assert d["width"] == 128
        assert d["height"] == 128
        assert d["elapsed_s"] == 0.01
        assert d["images_per_sec"] == 100.0
        assert d["window_size"] == 7
        assert isinstance(d, dict)


# ---------------------------------------------------------------------------
# BenchmarkSuite
# ---------------------------------------------------------------------------


class TestBenchmarkSuite:
    def test_to_dict(self):
        r = BenchmarkResult(
            method="full_image",
            width=64,
            height=64,
            elapsed_s=0.005,
            images_per_sec=200.0,
        )
        s = BenchmarkSuite(
            results=[r],
            summary={"methods": {"full_image": {"count": 1}}},
        )
        d = s.to_dict()
        assert "generated" in d
        assert len(d["results"]) == 1
        assert d["summary"]["methods"]["full_image"]["count"] == 1

    def test_empty_suite(self):
        s = BenchmarkSuite()
        d = s.to_dict()
        assert d["results"] == []
        assert d["summary"] == {}


# ---------------------------------------------------------------------------
# SSIMBenchmark
# ---------------------------------------------------------------------------


class TestSSIMBenchmark:
    def test_init(self):
        bench = SSIMBenchmark()
        assert bench.iterations == SSIMBenchmark.DEFAULT_ITERATIONS
        assert len(bench.sizes) > 0

    def test_init_custom(self):
        bench = SSIMBenchmark(
            sizes=[(32, 32)],
            window_sizes=[3],
            iterations=1,
        )
        assert bench.sizes == [(32, 32)]
        assert bench.window_sizes == [3]
        assert bench.iterations == 1

    def test_benchmark_windowed_small_image(self):
        bench = SSIMBenchmark(iterations=1)
        result = bench.benchmark_windowed(64, 64, window_size=7)
        assert result.method == "windowed"
        assert result.width == 64
        assert result.height == 64
        assert result.elapsed_s > 0
        assert result.images_per_sec > 0
        assert result.window_size == 7

    def test_benchmark_windowed_different_window_sizes(self):
        bench = SSIMBenchmark(iterations=1)
        r5 = bench.benchmark_windowed(64, 64, window_size=5)
        r7 = bench.benchmark_windowed(64, 64, window_size=7)
        assert r5.window_size == 5
        assert r7.window_size == 7
        assert r5.elapsed_s > 0
        assert r7.elapsed_s > 0

    def test_benchmark_full_image(self):
        bench = SSIMBenchmark(iterations=1)
        result = bench.benchmark_full_image(64, 64)
        assert result.method == "full_image"
        assert result.window_size == 0
        assert result.elapsed_s > 0
        assert result.images_per_sec > 0

    def test_benchmark_non_square(self):
        bench = SSIMBenchmark(iterations=1)
        r = bench.benchmark_windowed(100, 300, window_size=7)
        assert r.width == 300
        assert r.height == 100
        assert r.elapsed_s > 0

    def test_run_all(self):
        bench = SSIMBenchmark(
            sizes=[(64, 64), (128, 128)],
            window_sizes=[7],
            iterations=1,
        )
        suite = bench.run_all()
        assert isinstance(suite, BenchmarkSuite)
        assert len(suite.results) > 0
        assert "methods" in suite.summary
        assert "full_image" in suite.summary["methods"]
        assert "windowed" in suite.summary["methods"]

    def test_compare_methods(self):
        bench = SSIMBenchmark(iterations=1)
        result = bench.compare_methods(128, 128)
        assert "size" in result
        assert result["size"] == "128x128"
        assert "full_image" in result
        assert "windowed" in result
        assert "speedup" in result
        assert isinstance(result["speedup"], float)
        assert isinstance(result["windowed_faster"], bool)

    def test_summary_has_speedup(self):
        bench = SSIMBenchmark(
            sizes=[(64, 64)],
            window_sizes=[7],
            iterations=1,
        )
        suite = bench.run_all()
        if "windowed_vs_full" in suite.summary:
            wvf = suite.summary["windowed_vs_full"]
            assert "speedup_ratio" in wvf
            assert isinstance(wvf["speedup_ratio"], float)

    def test_summary_sizes_tested(self):
        bench = SSIMBenchmark(
            sizes=[(64, 64), (128, 128)],
            window_sizes=[7],
            iterations=1,
        )
        suite = bench.run_all()
        assert "sizes_tested" in suite.summary
        assert len(suite.summary["sizes_tested"]) >= 2

    def test_throughput_positive(self):
        bench = SSIMBenchmark(iterations=1)
        result = bench.benchmark_full_image(64, 64)
        assert result.images_per_sec > 0

    def test_multiple_iterations(self):
        bench = SSIMBenchmark(iterations=3)
        result = bench.benchmark_full_image(64, 64)
        assert result.elapsed_s > 0
        # With 3 iterations, time should reflect averaging
        assert result.images_per_sec > 0

    def test_window_skipped_when_too_large(self):
        """Window size larger than image dimension should be skipped in run_all."""
        bench = SSIMBenchmark(
            sizes=[(4, 4)],
            window_sizes=[7],  # 7 > 4, should be skipped
            iterations=1,
        )
        suite = bench.run_all()
        # Only full_image should be present, no windowed with ws=7
        windowed_results = [r for r in suite.results if r.method == "windowed"]
        # window_size=7 > min(4,4), so no windowed result for this size
        for r in windowed_results:
            assert r.window_size <= min(r.width, r.height)
