"""LaTeX compilation profiling and performance analysis.

Profiles compilation times, tracks memory usage, identifies slow examples,
and generates optimization recommendations.
"""

from __future__ import annotations

import json
import os
import resource
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

from buildlib.config import MAIN_TEX_FILENAME, REPO_ROOT, ProjectConfig

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ExampleProfile:
    """Profiling result for a single example."""

    name: str
    wall_time_s: float = 0.0
    user_time_s: float = 0.0
    system_time_s: float = 0.0
    peak_memory_kb: int = 0
    pdf_size_bytes: int = 0
    package_count: int = 0
    total_time_s: float | None = None
    success: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProfilingSummary:
    """Aggregated profiling results across all examples."""

    generated: str = ""
    profiles: list[ExampleProfile] = field(default_factory=list)
    total_examples: int = 0
    successful: int = 0
    failed: int = 0
    total_wall_time_s: float = 0.0
    mean_wall_time_s: float = 0.0
    median_wall_time_s: float = 0.0
    stdev_wall_time_s: float = 0.0
    min_wall_time_s: float = 0.0
    max_wall_time_s: float = 0.0
    peak_memory_kb: int = 0
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["profiles"] = [
            p.to_dict() if isinstance(p, ExampleProfile) else p for p in self.profiles
        ]
        return d


# ---------------------------------------------------------------------------
# Memory tracking helpers
# ---------------------------------------------------------------------------


def _get_peak_memory_kb() -> int:
    """Return peak resident set size in KB (Linux/macOS)."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    # ru_maxrss is in KB on Linux, bytes on macOS
    if os.uname().sysname == "Darwin":
        return usage.ru_maxrss // 1024
    return usage.ru_maxrss


def _current_memory_kb() -> int:
    """Return current RSS in KB by reading /proc/self/statm (Linux)."""
    try:
        with open("/proc/self/statm") as f:
            parts = f.read().split()
            # pages * page_size_kb
            page_size_kb = os.sysconf("SC_PAGE_SIZE") // 1024
            return int(parts[1]) * page_size_kb
    except (FileNotFoundError, OSError, IndexError, ValueError):
        return _get_peak_memory_kb()


# ---------------------------------------------------------------------------
# Profiler
# ---------------------------------------------------------------------------


class BuildProfiler:
    """Profile LaTeX builds and generate performance reports."""

    def __init__(self, config: ProjectConfig | None = None):
        self.config = config or ProjectConfig()
        self.profiles: list[ExampleProfile] = []

    def discover_examples(self) -> list[Path]:
        """Find all example directories containing main.tex."""
        examples_dir = REPO_ROOT / "examples"
        if not examples_dir.is_dir():
            return []
        return sorted(
            p
            for p in examples_dir.iterdir()
            if p.is_dir() and (p / MAIN_TEX_FILENAME).is_file()
        )

    def profile_example(
        self,
        example_name: str,
        *,
        runner: Any | None = None,
        force: bool = False,
    ) -> ExampleProfile:
        """Profile a single example build, capturing timing and memory."""
        example_dir = REPO_ROOT / "examples" / example_name
        if not example_dir.is_dir():
            return ExampleProfile(
                name=example_name, error=f"Example directory not found: {example_dir}"
            )

        profile = ExampleProfile(name=example_name)
        mem_before = _current_memory_kb()

        start_wall = time.perf_counter()
        start_cpu = time.process_time()

        try:
            if runner is not None:
                self._build_with_runner(example_name, runner, force)
            else:
                self._build_with_subprocess(example_name, force)

            profile.success = (example_dir / "main.pdf").exists()
            if profile.success:
                profile.pdf_size_bytes = (example_dir / "main.pdf").stat().st_size
        except Exception as exc:
            profile.error = str(exc)
            profile.success = False

        end_cpu = time.process_time()
        end_wall = time.perf_counter()

        profile.wall_time_s = round(end_wall - start_wall, 4)
        profile.user_time_s = round(end_cpu - start_cpu, 4)
        profile.system_time_s = round(
            (end_wall - start_wall) - (end_cpu - start_cpu), 4
        )
        profile.peak_memory_kb = _get_peak_memory_kb()

        # Parse log for package counts and LaTeX-reported time
        log_path = example_dir / "main.log"
        if log_path.exists():
            try:
                from buildlib.builder import parse_log_for_package_times

                log_content = log_path.read_text(encoding="utf-8", errors="replace")
                info = parse_log_for_package_times(log_content)
                profile.package_count = info.get("package_count", 0)
                profile.total_time_s = info.get("total_time_s")
            except Exception:
                pass

        return profile

    def _build_with_runner(self, example_name: str, runner: Any, force: bool) -> None:
        """Build using the project's CommandRunner."""
        import os

        from buildlib.builder import (
            INTERACTION_NONSTOP,
            LATEXMK_COMMAND,
            LATEXMK_FORCE_CONTINUE,
        )

        example_dir = REPO_ROOT / "examples" / example_name
        cmd = [LATEXMK_COMMAND, INTERACTION_NONSTOP, LATEXMK_FORCE_CONTINUE]
        if force:
            cmd.append("-g")
        cmd.append(MAIN_TEX_FILENAME)

        extra_env = {
            "TEXINPUTS": os.pathsep.join([".", str(REPO_ROOT), ""]),
            "LC_ALL": "C.utf8",
        }
        runner.run(cmd, extra_env=extra_env, cwd=example_dir)

    def _build_with_subprocess(self, example_name: str, force: bool) -> None:
        """Build using a direct subprocess call."""
        import subprocess

        example_dir = REPO_ROOT / "examples" / example_name
        cmd = ["latexmk", "-interaction=nonstopmode", "-f"]
        if force:
            cmd.append("-g")
        cmd.append(MAIN_TEX_FILENAME)

        env = os.environ.copy()
        env["TEXINPUTS"] = os.pathsep.join([".", str(REPO_ROOT), ""])
        env["LC_ALL"] = "C.utf8"

        subprocess.run(
            cmd,
            cwd=example_dir,
            env=env,
            capture_output=True,
            timeout=600,
        )

    def profile_all(
        self,
        *,
        names: list[str] | None = None,
        runner: Any | None = None,
        force: bool = False,
    ) -> ProfilingSummary:
        """Profile all (or selected) examples and return a summary."""
        examples = self.discover_examples()
        if names:
            examples = [e for e in examples if e.name in set(names)]

        self.profiles = []
        for ex in examples:
            profile = self.profile_example(ex.name, runner=runner, force=force)
            self.profiles.append(profile)

        return self._build_summary()

    def _build_summary(self) -> ProfilingSummary:
        """Aggregate profiles into a summary with recommendations."""
        summary = ProfilingSummary()
        summary.generated = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        summary.profiles = self.profiles
        summary.total_examples = len(self.profiles)
        summary.successful = sum(1 for p in self.profiles if p.success)
        summary.failed = summary.total_examples - summary.successful

        wall_times = [
            p.wall_time_s for p in self.profiles if p.success and p.wall_time_s > 0
        ]
        if wall_times:
            summary.total_wall_time_s = round(sum(wall_times), 4)
            summary.mean_wall_time_s = round(mean(wall_times), 4)
            summary.median_wall_time_s = round(median(wall_times), 4)
            summary.min_wall_time_s = round(min(wall_times), 4)
            summary.max_wall_time_s = round(max(wall_times), 4)
            if len(wall_times) > 1:
                summary.stdev_wall_time_s = round(stdev(wall_times), 4)

        mem_values = [p.peak_memory_kb for p in self.profiles if p.peak_memory_kb > 0]
        if mem_values:
            summary.peak_memory_kb = max(mem_values)

        summary.recommendations = self._generate_recommendations(summary)
        return summary

    def _generate_recommendations(self, summary: ProfilingSummary) -> list[str]:
        """Generate actionable optimization recommendations."""
        recs: list[str] = []
        if not summary.profiles:
            return recs

        successful = [p for p in summary.profiles if p.success]
        if not successful:
            recs.append("All builds failed. Check LaTeX installation and log files.")
            return recs

        # Slowest examples
        sorted_by_time = sorted(successful, key=lambda p: p.wall_time_s, reverse=True)
        if sorted_by_time:
            slowest = sorted_by_time[0]
            if slowest.wall_time_s > 30:
                recs.append(
                    f"Slowest example '{slowest.name}' took {slowest.wall_time_s:.1f}s. "
                    "Consider simplifying or splitting it."
                )
            if summary.stdev_wall_time_s > 0 and summary.mean_wall_time_s > 0:
                cv = summary.stdev_wall_time_s / summary.mean_wall_time_s
                if cv > 0.5:
                    recs.append(
                        f"High variance in build times (CV={cv:.2f}). "
                        "Some examples are disproportionately slow."
                    )

        # Memory
        if summary.peak_memory_kb > 500_000:
            recs.append(
                f"Peak memory usage ({summary.peak_memory_kb // 1024} MB) is high. "
                "Consider reducing image resolutions or package loads."
            )

        # Package counts
        heavy = [p for p in successful if p.package_count > 50]
        if heavy:
            names = ", ".join(p.name for p in heavy[:3])
            recs.append(
                f"Examples with >50 packages: {names}. "
                "Audit package dependencies for unnecessary loads."
            )

        # PDF size
        large_pdfs = [p for p in successful if p.pdf_size_bytes > 5_000_000]
        if large_pdfs:
            names = ", ".join(p.name for p in large_pdfs[:3])
            recs.append(
                f"Large PDFs (>5 MB): {names}. "
                "Consider compressing images or using draft mode."
            )

        # Failed builds
        if summary.failed > 0:
            failed_names = [p.name for p in self.profiles if not p.success]
            recs.append(
                f"{summary.failed} build(s) failed: {', '.join(failed_names[:5])}. "
                "Review logs for errors."
            )

        if not recs:
            recs.append("Build performance looks good. No optimization needed.")

        return recs

    def export_json(self, output_path: Path | str) -> Path:
        """Write profiling results to a JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        summary = self._build_summary()
        output_path.write_text(
            json.dumps(summary.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
        return output_path


def get_slowest_examples(
    profiles: list[ExampleProfile], n: int = 5
) -> list[ExampleProfile]:
    """Return the *n* slowest successful examples."""
    successful = [p for p in profiles if p.success and p.wall_time_s > 0]
    return sorted(successful, key=lambda p: p.wall_time_s, reverse=True)[:n]


def compare_profiles(
    baseline: ProfilingSummary, current: ProfilingSummary
) -> list[dict[str, Any]]:
    """Compare two profiling summaries and return regressions/improvements."""
    baseline_map = {p.name: p for p in baseline.profiles if p.success}
    current_map = {p.name: p for p in current.profiles if p.success}

    results = []
    all_names = sorted(set(baseline_map) | set(current_map))

    for name in all_names:
        b = baseline_map.get(name)
        c = current_map.get(name)
        entry: dict[str, Any] = {"name": name}

        if b and c:
            delta = c.wall_time_s - b.wall_time_s
            pct = (delta / b.wall_time_s * 100) if b.wall_time_s > 0 else 0
            entry["baseline_s"] = b.wall_time_s
            entry["current_s"] = c.wall_time_s
            entry["delta_s"] = round(delta, 4)
            entry["delta_pct"] = round(pct, 1)
            entry["status"] = (
                "regression" if pct > 20 else ("improvement" if pct < -20 else "stable")
            )
        elif c:
            entry["status"] = "new"
            entry["current_s"] = c.wall_time_s
        else:
            entry["status"] = "removed"
            entry["baseline_s"] = b.wall_time_s if b else 0

        results.append(entry)

    return results
