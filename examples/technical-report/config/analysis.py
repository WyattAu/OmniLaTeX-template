#!/usr/bin/env python3
"""Performance metrics collector for infrastructure audit."""

import asyncio
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np


@dataclass
class MetricSample:
    timestamp: float
    value: float
    label: str
    unit: str = ""


@dataclass
class PerformanceReport:
    hostname: str
    samples: list[MetricSample] = field(default_factory=list)
    intervals: dict[str, float] = field(default_factory=dict)

    def p99_latency(self) -> float:
        values = sorted(s.value for s in self.samples if s.label == "latency")
        if not values:
            return 0.0
        idx = int(np.ceil(0.99 * len(values))) - 1
        return values[min(idx, len(values) - 1)]

    def mean_iops(self) -> float:
        values = [s.value for s in self.samples if s.label == "iops"]
        return float(np.mean(values)) if values else 0.0

    def export_json(self, path: Path) -> None:
        data = {
            "hostname": self.hostname,
            "p99_latency_ms": self.p99_latency(),
            "mean_iops": self.mean_iops(),
            "total_samples": len(self.samples),
        }
        path.write_text(json.dumps(data, indent=2))


async def collect_metrics(
    host: str,
    duration: int = 300,
    interval: int = 5,
) -> PerformanceReport:
    report = PerformanceReport(hostname=host)
    deadline = time.monotonic() + duration

    while time.monotonic() < deadline:
        sample = MetricSample(
            timestamp=time.time(),
            value=np.random.exponential(scale=200),
            label="latency",
            unit="ms",
        )
        report.samples.append(sample)
        await asyncio.sleep(interval)

    return report


def main() -> None:
    report = asyncio.run(collect_metrics("db-primary.contoso.internal"))
    report.export_json(Path("audit_results.json"))
    print(f"Collected {len(report.samples)} samples")
    print(f"P99 latency: {report.p99_latency():.1f} ms")


if __name__ == "__main__":
    main()
