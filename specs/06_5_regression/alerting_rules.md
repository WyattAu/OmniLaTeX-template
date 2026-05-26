# Performance Alerting Rules

## Alert Levels

### Critical — >= 50% Degradation

Any metric that degrades by 50% or more relative to its baseline value triggers a **critical** alert.

- **CI behavior**: The workflow fails immediately and blocks merge.
- **Action required**: Investigate and fix before merging. Do not update baselines to suppress.

Trigger examples:

- Single example build goes from 15s to >= 22.5s
- Full suite goes from 180s to >= 270s
- Docker image grows from 2800 MB to >= 4200 MB

### Warning — >= 20% Degradation

Any metric that degrades by 20% or more (but less than 50%) triggers a **warning** alert.

- **CI behavior**: The workflow posts a warning annotation but does not block merge.
- **Action required**: Acknowledge the regression. Update baselines if intentional, or file a follow-up issue.

Trigger examples:

- Cache hit rate drops from 97% to <= 77.6%
- MkDocs build goes from 30s to >= 36s
- Sorry count increases from 0 to >= 1 (any increase is a regression for this metric)

### Info — >= 10% Improvement (Positive Regression)

Any metric that improves by 10% or more triggers an **info** alert.

- **CI behavior**: Posts an informational annotation.
- **Action required**: Consider updating the baseline to reflect the improvement.

Trigger examples:

- Build time drops from 15s to <= 13.5s
- Cache hit rate rises from 97% to >= 100% (capped at 100)
- Docker image shrinks from 2800 MB to <= 2520 MB

## Notification Channels

All alerts are surfaced via **GitHub Actions annotations**:

- `::error` for critical alerts (blocks merge)
- `::warning` for warning alerts
- `::notice` or `::debug` for info alerts

Annotations include:

- Metric name
- Baseline value
- Measured value
- Percentage change
- Link to `baseline_metrics.toml` for reference

### Example Annotation Output

```
::error file=specs/06_5_regression/baseline_metrics.toml,title=Performance Regression (Critical)::build.single_example_avg_seconds: baseline=15.0s, measured=24.1s (+60.7%)
::warning file=specs/06_5_regression/baseline_metrics.toml,title=Performance Regression (Warning)::tests.fast_suite_seconds: baseline=5.0s, measured=6.3s (+26.0%)
::notice file=specs/06_5_regression/baseline_metrics.toml,title=Performance Improvement::cache.hit_rate_percent: baseline=97.0%, measured=99.1% (+2.2%)
```
