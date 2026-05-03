# Performance

## Current Benchmarks

CI collects per-example timing data on every push via `--timings`. The performance
workflow is defined in [`.github/workflows/build.yml`](../.github/workflows/build.yml)
and produces a `build/metrics.json` artifact with wall-clock times, PDF sizes,
and LaTeX package load information for each example. A performance summary with
regression detection is posted to the GitHub Actions job summary page.

## Known Bottlenecks

| Bottleneck | Cause | Mitigation |
|---|---|---|
| LuaLaTeX first-run font cache | `luaotfload` scans system fonts (~5-10s) | Pre-warmed in Docker via `luaotfload-tool --update` |
| Font loading per run | Libertinus + Monaspace + Atkinson (~2-3s) | Inherent to font count; no easy reduction |
| LuaTeX-ja CJK setup | Additional engine overhead for CJK examples | Required for CJK support |
| Total CI build time | ~15-20 minutes for 40 examples in Docker | Parallel compilation (`-j N`) mitigates wall time |

## Optimization Recommendations

- **Docker image font cache** -- Already pre-warmed with `luaotfload-tool --update`
  in the Dockerfile. First-run font scanning cost is eliminated.
- **BuildKit layer caching** -- Already configured in CI. Unchanged Docker layers
  are reused across builds.
- **Parallel compilation** -- Supported via `build.py -j N`. CI defaults to 4
  parallel jobs; increase for faster wall-clock times at the cost of CPU/memory.
- **Font subsetting** -- Not recommended. Subsetting breaks reproducibility and
  complicates the build pipeline.
- **fmtutil cache** -- Not needed. The Docker image itself serves as the format
  cache.

## Profile Command

To get per-example timing on your local machine:

```bash
python3 build.py --mode prod --timings build-all
```

This writes `build/metrics.json` and `build/metrics_history/metrics_<timestamp>.json`
with wall-clock time, success status, PDF size, and LaTeX package timing data for
every example.

## Expected Compile Times by Example Type

| Category | Examples | Expected Time |
|---|---|---|
| Simple | article, cv, letter, memo | 15-30s |
| Medium | thesis, book, technical-report | 30-60s |
| Complex | cjk-chinese, cjk-japanese, cjk-korean, rtl-arabic, rtl-hebrew | 45-90s |
| Very complex | dissertation, thesis-tuhh | 60-120s |

Times are approximate and depend on hardware, font availability, and whether the
font cache has been warmed. Docker builds include the cache pre-warm step and
are generally faster on repeated runs.
