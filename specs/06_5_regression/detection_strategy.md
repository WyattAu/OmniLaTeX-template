# Performance Regression Detection Strategy

## Tracked Metrics

### Build Performance

- `single_example_avg_seconds` — average time to build a single LaTeX example
- `all_examples_48_jobs1_seconds` — full build of all 50 examples with 1 job
- `all_examples_48_jobs4_seconds` — full build of all 50 examples with 4 jobs
- `root_build_seconds` — root project build time

### Test Suite Performance

- `fast_suite_seconds` — fast test suite wall-clock time
- `fast_suite_count` — number of tests in fast suite
- `full_suite_seconds` — full test suite wall-clock time

### Lean 4 Verification

- `proof_verification_seconds` — total proof verification time
- `theorem_count` — number of theorems verified
- `sorry_count` — number of unproven sorries (target: 0)

### Documentation

- `mkdocs_build_seconds` — MkDocs site build time
- `site_size_mb` — generated site size in megabytes

### Docker

- `image_size_mb` — Docker image size in megabytes
- `pull_seconds` — image pull time

### Visual Regression (SSIM)

- `single_comparison_seconds` — single image comparison time
- `full_visual_regression_seconds` — full visual regression suite time

### Cache

- `hit_rate_percent` — cache hit rate percentage
- `cache_size_bytes` — cache directory size
- `cached_examples` — number of cached examples
- `total_examples` — total number of examples

## Regression Threshold

A metric is flagged as a **regression** when its measured value degrades by **>= 20%** relative to the baseline recorded in `baseline_metrics.toml`.

For timing metrics, degradation means the measured time is >= 1.2x the baseline.
For size/count metrics where lower is better, degradation means the value is >= 1.2x the baseline.
For metrics where higher is better (e.g., cache hit rate, theorem count), degradation means the value drops below 0.8x the baseline.

## Baseline Storage

Baseline data is stored in:

- **File**: `specs/06_5_regression/baseline_metrics.toml`
- **Format**: TOML (versioned alongside the project)
- **Version**: Tracked via the `Version` header field in the TOML file

Baselines are committed to the repository so that every branch and PR compares against the same reference points.

## Updating Baselines

Baselines should be updated when:

1. A **deliberate** change alters performance characteristics (e.g., adding examples, upgrading toolchains).
2. The update is committed with a clear message explaining why.

To update:

```bash
# Run benchmarks and capture results
make bench > bench_results.txt

# Edit specs/06_5_regression/baseline_metrics.toml with new values
# Update the Version field and Generated date

git add specs/06_5_regression/baseline_metrics.toml
git commit -m "chore: update performance baselines (<reason>)"
```

## CI Integration

The `performance-regression.yml` workflow:

1. Runs on every push to `main` and on pull requests.
2. Executes the benchmark suite and captures timing/size metrics.
3. Compares results against `baseline_metrics.toml`.
4. Fails the CI job if any metric shows >= 20% degradation.
5. Posts GitHub Actions annotations listing regressed metrics with measured vs. baseline values.
6. On `main` pushes, uploads benchmark results as artifacts for historical tracking.
