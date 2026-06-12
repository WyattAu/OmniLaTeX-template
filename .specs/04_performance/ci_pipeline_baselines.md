# CI Pipeline Timing Baselines

**Repository:** OmniLaTeX-template
**Generated:** 2026-06-06
**CI Platform:** GitHub Actions (ubuntu-latest)

---

## Pipeline Overview

| Workflow | Trigger | Jobs | Typical Duration |
|----------|---------|------|------------------|
| build.yml | push/PR to main | lint, build, test, performance, determinism | 15-25 min |
| build-examples.yml | push to main | discover, build (50 parallel), collect | 20-35 min |
| lean4-ci.yml | push/PR | verify, proof-gate | 3-8 min |
| docker-ci.yml | push/PR to main | build-push (multi-arch) | 15-25 min |
| visual-regression.yml | push/PR | build, diff | 20-30 min |
| integration-matrix.yml | push/PR | language-matrix (11x3), rtl | 25-40 min |

---

## Job Timing Baselines

### build.yml

| Job | Min | Typical | Max | Notes |
|-----|-----|---------|-----|-------|
| lint | 30s | 1 min | 2 min | black, isort, flake8 |
| dependency-review | 10s | 30s | 1 min | GitHub dependency review |
| build | 5 min | 10 min | 15 min | LuaLaTeX compilation |
| performance | 2 min | 5 min | 8 min | Timing metrics |
| determinism | 3 min | 5 min | 8 min | Reproducible build check |
| test | 1 min | 3 min | 5 min | pytest fast suite |

### build-examples.yml

| Job | Min | Typical | Max | Notes |
|-----|-----|---------|-----|-------|
| discover | 10s | 15s | 30s | List example directories |
| build (per example) | 30s | 2 min | 5 min | LuaLaTeX compilation |
| build (50 parallel) | 5 min | 15 min | 25 min | 4 concurrent workers |
| collect | 30s | 1 min | 2 min | Merge artifacts |

### lean4-ci.yml

| Job | Min | Typical | Max | Notes |
|-----|-----|---------|-----|-------|
| verify | 2 min | 5 min | 8 min | lake build (19 jobs) |
| proof-gate | 5s | 10s | 30s | grep for sorry |

### docker-ci.yml

| Job | Min | Typical | Max | Notes |
|-----|-----|---------|-----|-------|
| build-push | 10 min | 18 min | 30 min | Multi-arch (amd64+arm64) |

---

## Test Suite Timing

| Test Category | Count | Typical | Timeout |
|---------------|-------|---------|---------|
| Fast (no compilation) | 936 | 45s | 60s |
| Slow (LaTeX compilation) | 173 | 30 min | 60 min |
| Lean 4 proofs | 198 | 3 min | 10 min |
| l3build unit tests | 94 | 15 min | 30 min |

---

## Regression Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Build time regression | > 250% of baseline | CI failure |
| Test suite regression | > 200% of baseline | CI warning |
| PDF size regression | > 50% increase | CI warning |
| SSIM score | < 0.95 | Visual regression failure |

---

## Optimization Opportunities

| Area | Current | Target | Strategy |
|------|---------|--------|----------|
| Example builds | 15 min (92 examples) | 8 min | Increase parallelism to 8 workers |
| Docker build | 18 min | 12 min | Better BuildKit cache utilization |
| Lean 4 proofs | 5 min | 3 min | Aggressive .lake caching |
| Fast test suite | 45s | 30s | Parallel pytest execution |

---

## Resource Usage

| Resource | Typical | Peak | Notes |
|----------|---------|------|-------|
| GitHub Actions minutes | 100-200/week | 500/week | Depends on PR frequency |
| Docker image size | 2.5 GB | 3 GB | TeX Live scheme-full |
| Build cache size | 50 MB | 200 MB | PDF + aux files |
| .lake cache size | 100 MB | 300 MB | Lean 4 build artifacts |
