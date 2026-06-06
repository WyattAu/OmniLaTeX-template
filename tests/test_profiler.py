"""Unit tests for buildlib.profiler module."""

from __future__ import annotations

import json

from buildlib.profiler import (
    BuildProfiler,
    ExampleProfile,
    ProfilingSummary,
    compare_profiles,
    get_slowest_examples,
)

# ---------------------------------------------------------------------------
# ExampleProfile
# ---------------------------------------------------------------------------


class TestExampleProfile:
    def test_default_values(self):
        p = ExampleProfile(name="test")
        assert p.name == "test"
        assert p.wall_time_s == 0.0
        assert p.success is False
        assert p.error is None

    def test_to_dict(self):
        p = ExampleProfile(
            name="demo", wall_time_s=1.5, success=True, pdf_size_bytes=1024
        )
        d = p.to_dict()
        assert d["name"] == "demo"
        assert d["wall_time_s"] == 1.5
        assert d["success"] is True
        assert d["pdf_size_bytes"] == 1024
        assert isinstance(d, dict)


# ---------------------------------------------------------------------------
# ProfilingSummary
# ---------------------------------------------------------------------------


class TestProfilingSummary:
    def test_default_values(self):
        s = ProfilingSummary()
        assert s.total_examples == 0
        assert s.profiles == []
        assert s.recommendations == []

    def test_to_dict(self):
        p = ExampleProfile(name="a", wall_time_s=2.0, success=True)
        s = ProfilingSummary(
            total_examples=1,
            successful=1,
            profiles=[p],
        )
        d = s.to_dict()
        assert d["total_examples"] == 1
        assert len(d["profiles"]) == 1
        assert d["profiles"][0]["name"] == "a"


# ---------------------------------------------------------------------------
# get_slowest_examples
# ---------------------------------------------------------------------------


class TestGetSlowestExamples:
    def test_returns_n_slowest(self):
        profiles = [
            ExampleProfile(name="fast", wall_time_s=1.0, success=True),
            ExampleProfile(name="medium", wall_time_s=5.0, success=True),
            ExampleProfile(name="slow", wall_time_s=10.0, success=True),
            ExampleProfile(name="slowest", wall_time_s=20.0, success=True),
        ]
        result = get_slowest_examples(profiles, n=2)
        assert len(result) == 2
        assert result[0].name == "slowest"
        assert result[1].name == "slow"

    def test_excludes_failed(self):
        profiles = [
            ExampleProfile(name="ok", wall_time_s=5.0, success=True),
            ExampleProfile(name="bad", wall_time_s=100.0, success=False),
        ]
        result = get_slowest_examples(profiles, n=5)
        assert len(result) == 1
        assert result[0].name == "ok"

    def test_empty_list(self):
        assert get_slowest_examples([]) == []


# ---------------------------------------------------------------------------
# compare_profiles
# ---------------------------------------------------------------------------


class TestCompareProfiles:
    def test_regression_detection(self):
        baseline = ProfilingSummary(
            profiles=[
                ExampleProfile(name="a", wall_time_s=5.0, success=True),
                ExampleProfile(name="b", wall_time_s=10.0, success=True),
            ]
        )
        current = ProfilingSummary(
            profiles=[
                ExampleProfile(
                    name="a", wall_time_s=15.0, success=True
                ),  # 200% regression
                ExampleProfile(name="b", wall_time_s=10.5, success=True),  # ~stable
            ]
        )
        results = compare_profiles(baseline, current)
        by_name = {r["name"]: r for r in results}

        assert by_name["a"]["status"] == "regression"
        assert by_name["a"]["delta_pct"] > 100
        assert by_name["b"]["status"] == "stable"

    def test_improvement_detection(self):
        baseline = ProfilingSummary(
            profiles=[ExampleProfile(name="x", wall_time_s=20.0, success=True)]
        )
        current = ProfilingSummary(
            profiles=[ExampleProfile(name="x", wall_time_s=10.0, success=True)]
        )
        results = compare_profiles(baseline, current)
        assert results[0]["status"] == "improvement"
        assert results[0]["delta_pct"] < -20

    def test_new_example(self):
        baseline = ProfilingSummary(profiles=[])
        current = ProfilingSummary(
            profiles=[ExampleProfile(name="new", wall_time_s=3.0, success=True)]
        )
        results = compare_profiles(baseline, current)
        assert results[0]["status"] == "new"

    def test_removed_example(self):
        baseline = ProfilingSummary(
            profiles=[ExampleProfile(name="old", wall_time_s=3.0, success=True)]
        )
        current = ProfilingSummary(profiles=[])
        results = compare_profiles(baseline, current)
        assert results[0]["status"] == "removed"


# ---------------------------------------------------------------------------
# BuildProfiler (unit tests without actual LaTeX)
# ---------------------------------------------------------------------------


class TestBuildProfiler:
    def test_init_default(self):
        profiler = BuildProfiler()
        assert profiler.config is not None
        assert profiler.profiles == []

    def test_discover_examples_returns_list(self, tmp_path, monkeypatch):
        examples_dir = tmp_path / "examples"
        examples_dir.mkdir()
        ex = examples_dir / "sample"
        ex.mkdir()
        (ex / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}hi\\end{document}"
        )

        monkeypatch.setattr("buildlib.profiler.REPO_ROOT", tmp_path)
        profiler = BuildProfiler()
        found = profiler.discover_examples()
        assert len(found) == 1
        assert found[0].name == "sample"

    def test_discover_examples_empty(self, tmp_path, monkeypatch):
        examples_dir = tmp_path / "examples"
        examples_dir.mkdir()

        monkeypatch.setattr("buildlib.profiler.REPO_ROOT", tmp_path)
        profiler = BuildProfiler()
        found = profiler.discover_examples()
        assert found == []

    def test_profile_example_missing_dir(self, monkeypatch, tmp_path):
        
        monkeypatch.setattr("buildlib.profiler.REPO_ROOT", tmp_path)
        profiler = BuildProfiler()
        result = profiler.profile_example("nonexistent_example")
        assert result.success is False
        assert result.error is not None

    def test_export_json(self, tmp_path, monkeypatch):
        profiler = BuildProfiler()
        profiler.profiles = [
            ExampleProfile(name="a", wall_time_s=1.0, success=True),
        ]
        out = tmp_path / "output.json"
        result_path = profiler.export_json(out)
        assert result_path.exists()
        data = json.loads(result_path.read_text())
        assert data["total_examples"] == 1
        assert data["profiles"][0]["name"] == "a"

    def test_generate_recommendations_empty(self):
        profiler = BuildProfiler()
        summary = ProfilingSummary()
        recs = profiler._generate_recommendations(summary)
        assert recs == []

    def test_generate_recommendations_all_failed(self):
        profiler = BuildProfiler()
        summary = ProfilingSummary(profiles=[ExampleProfile(name="a", success=False)])
        recs = profiler._generate_recommendations(summary)
        assert any("failed" in r.lower() for r in recs)

    def test_generate_recommendations_slow_example(self):
        profiler = BuildProfiler()
        summary = ProfilingSummary(
            total_examples=1,
            successful=1,
            profiles=[ExampleProfile(name="slow", wall_time_s=60.0, success=True)],
        )
        summary.mean_wall_time_s = 60.0
        summary.stdev_wall_time_s = 0.0
        recs = profiler._generate_recommendations(summary)
        assert any("slow" in r.lower() or "60" in r for r in recs)

    def test_generate_recommendations_large_pdf(self):
        profiler = BuildProfiler()
        summary = ProfilingSummary(
            total_examples=1,
            successful=1,
            profiles=[
                ExampleProfile(
                    name="huge",
                    wall_time_s=5.0,
                    success=True,
                    pdf_size_bytes=10_000_000,
                )
            ],
        )
        recs = profiler._generate_recommendations(summary)
        assert any("pdf" in r.lower() or "MB" in r for r in recs)

    def test_generate_recommendations_good_performance(self):
        profiler = BuildProfiler()
        summary = ProfilingSummary(
            total_examples=1,
            successful=1,
            peak_memory_kb=10_000,
            profiles=[
                ExampleProfile(
                    name="fast", wall_time_s=2.0, success=True, package_count=10
                )
            ],
        )
        summary.mean_wall_time_s = 2.0
        summary.stdev_wall_time_s = 0.0
        recs = profiler._generate_recommendations(summary)
        assert any("good" in r.lower() or "no optimization" in r.lower() for r in recs)
