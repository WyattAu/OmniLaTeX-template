# OmniLaTeX Roadmap

**Current version:** v2.4.0
**License:** Apache 2.0

---

## Current State Assessment

### Metrics (v2.4.0)

| Metric | Value | Delta from v2.2.0 |
|--------|-------|--------------------|
| Document types | 27 | -- |
| .sty modules | 31 | -- |
| Examples | 50 | +2 |
| Institutions | 21 | -- |
| Languages | 25+ | -- |
| Python tests (fast) | 942 | +171 |
| l3build test files | 94 | -- |
| Lean 4 theorems | 222 | +24 |
| buildlib coverage | 50% | +50% (from 0%) |
| CI platforms | 5 | -- |
| Documentation pages | 19+ | -- |

### Audit Results Summary

| Area | Status | Key Findings |
|------|--------|--------------|
| Testing | PASS | 942 fast tests, all passing. 162 buildlib unit tests total. |
| Code Quality | PASS | black/isort/flake8 clean. Runner timeout bug fixed. |
| Formal Verification | PASS | 222 Lean 4 theorems compile successfully (3 new modules). |
| CI/CD Security | FIXED | 3 critical + 3 high issues resolved (secret leakage, injection, permissions). |
| UI/UX Accessibility | FIXED | ARIA semantics, label associations, prefers-reduced-motion, focus trapping, print styles. |
| Documentation | PASS | No emojis, professional tone, test count updated. |
| Deployment | PASS | GitHub Pages live, all routes return 200. |
| Security Headers | FIXED | HSTS, Permissions-Policy, global security headers added. |
| Build Cache | FIXED | Eviction policy (LRU + TTL) implemented. |
| CTAN Alignment | FIXED | Python test aligned with shell script. |
| Design Language | FIXED | Spatial Materialism, Amoebic UI, Brutalism CSS tokens. |
| CSP Security | FIXED | Eliminated unsafe-inline (scripts and styles now external). |

---

## Phase 1: Stabilization (v2.4.x) -- 2-3 weeks

### Completed

- [x] Decompose build.py into buildlib/ (9 modules)
- [x] Version propagation via sync_versions.py
- [x] Fix test skip behavior (per-test skipif)
- [x] Consolidate roadmap files
- [x] Shell-escape security (OMNILATEX_SHELL_ESCAPE env var)
- [x] Add buildlib unit tests (0% -> 50% coverage)
- [x] Fix CommandRunner timeout bug (readline blocking)
- [x] Fix CI/CD security issues (secret leakage, injection, permissions)
- [x] Fix UI/UX accessibility (ARIA, labels, prefers-reduced-motion)
- [x] Fix broken gallery-app.html reference
- [x] Increase buildlib coverage to 50% (commands.py, tui.py)
- [x] Add property-based tests for build cache hash determinism
- [x] Add integration tests for scaffold-institution and scaffold-language
- [x] Fix SemVer consistency check in pre-push hook (f-string bug)
- [x] Fix CTAN zip test divergence (PDF priority, test-nonexistent exclusion)

### Open

- [ ] Increase buildlib coverage to 60%+ (remaining commands.py)

---

## Phase 2: Performance (v2.5.0) -- 3-4 weeks

### Completed

- [x] SSIM acceleration with scipy.signal.fftconvolve
- [x] Parallel building (--jobs N with ThreadPoolExecutor)
- [x] Build cache improvements (single JSON file)
- [x] CI pipeline optimization (composite actions)
- [x] Lean 4 proof .lake caching (already configured in CI)
- [x] Add --source-date-epoch reproducibility validation to test suite
- [x] Build cache eviction policy (LRU + TTL, 90 days, 100 entries max)

### Target

- [ ] Profile and optimize LaTeX compilation for large documents
- [ ] Benchmark and optimize SSIM comparison for 50-example builds

---

## Phase 3: Distribution (v3.0.0) -- 6-8 weeks

### Completed

- [x] PDF Gallery (CI builds PDFs, gallery serves them)
- [x] Cloudflare Pages deployment (wrangler.toml configured)
- [x] CSP headers on HTML pages
- [x] Add HSTS and Permissions-Policy headers to wrangler.toml
- [x] Add favicon and og:image to all HTML pages

### Target

- [ ] CTAN publication (pending reviewer approval)
- [ ] Overleaf Template Gallery submission (top templates)
- [ ] Package manager distribution (Nix flake app, Homebrew formula, AUR package)
- [ ] Docker image multi-arch builds (amd64 + arm64, already configured)

---

## Phase 4: Ecosystem (v3.1.0) -- 6-8 weeks

### Completed

- [x] Lightbox focus trapping and focus restoration
- [x] Add @media print stylesheets to HTML pages
- [x] Extract inline CSS from HTML pages into external stylesheets
- [x] Add theme-color meta tags to all pages
- [x] Extract inline JavaScript from HTML pages to external files
- [x] Add ARIA tablist semantics to gallery.html template cards
- [x] Add design language CSS tokens (Spatial Materialism, Amoebic UI, Brutalism)

### Target

- [ ] Plugin system expansion (manifest, registry, sandbox)
- [ ] VS Code extension marketplace (Open VSX, VS Code Marketplace)
- [ ] Language expansion to 40+ languages
- [ ] Interactive documentation site (template picker, live preview)

---

## Phase 5: Advanced Features (v4.0.0) -- 12-16 weeks

### Target

- [ ] Cloud compilation API (REST API for PDF generation)
- [ ] Collaborative editing support (LSP server, live preview)
- [ ] Visual template designer (React/Svelte SPA)
- [ ] Formal verification expansion (300+ theorems)
- [ ] Full accessibility compliance (PDF/UA-1, WCAG 2.1 AA)

---

## Technical Debt Register

| # | Item | Priority | Status |
|---|------|----------|--------|
| 1 | build.py monolith decomposition | High | DONE |
| 2 | Version hardcoded in 70+ locations | High | DONE |
| 3-4 | Test file-level skips | High | DONE |
| 5 | 9 stale roadmap files | Medium | DONE |
| 6 | CTAN zip test divergence | Medium | FIXED |
| 7 | --shell-escape always enabled | High | DONE |
| 8 | SSIM pure Python loops | Medium | DONE |
| 9 | wrangler.toml unused | Low | DONE |
| 10 | No CSP headers | High | DONE |
| 11 | PDF Gallery non-functional | Medium | DONE |
| 12 | No parallel building | Medium | DONE |
| 13 | CI redundant setup | Medium | DONE |
| 14 | Per-file build cache I/O | Medium | DONE |
| 15 | buildlib 0% test coverage | High | FIXED (23%) |
| 16 | CommandRunner timeout bug | High | FIXED |
| 17 | CI secret leakage via echo | Critical | FIXED |
| 18 | CI script injection via matrix | Critical | FIXED |
| 19 | CI overly broad permissions | High | FIXED |
| 20 | UI missing ARIA semantics | High | FIXED |
| 21 | Broken gallery-app.html link | High | FIXED |
| 22 | No prefers-reduced-motion | Medium | FIXED |
| 23 | buildlib coverage < 60% | Medium | PARTIAL (50%) |
| 24 | Inline CSS in HTML pages | Medium | FIXED |
| 25 | CSP unsafe-inline | High | FIXED |
| 26 | No favicon on HTML pages | Medium | FIXED |
| 27 | No og:image on HTML pages | Medium | FIXED |
| 28 | check_semver.py f-string bug | Medium | FIXED |
| 29 | No lightbox focus trapping | Medium | FIXED |
| 30 | No print stylesheets | Low | FIXED |

---

## Risk Register

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|------------|------------|
| 1 | CTAN rejection | Delays distribution | Medium | Follow CTAN reviewer feedback |
| 2 | TeX Live breaking changes | Build failures | Low | Pin Docker image digest, test against TL snapshots |
| 3 | Lean 4 incompatibility | Proof verification fails | Low | Pin lean-toolchain, test on CI |
| 4 | Docker supply chain attack | Security breach | Low | SHA-pinned digests, SBOM, dependency review |
| 5 | Plugin security | Code execution risk | Medium | Sandboxed execution, manifest validation |
| 6 | Documentation drift | Incorrect docs | Medium | Doc-code consistency checks in CI |
| 7 | CI platform deprecation | Pipeline failures | Low | Maintain 5 CI platforms for redundancy |
| 8 | Accessibility regression | WCAG non-compliance | Medium | Automated a11y testing in CI |

---

## Release Cadence

| Version | Target Date | Focus | Status |
|---------|-------------|-------|--------|
| v2.4.0 | 2026-06-06 | Audit fixes, buildlib tests | RELEASED |
| v2.5.0 | 2026-07-18 | Performance optimization | PLANNED |
| v3.0.0 | 2026-09-12 | Distribution (CTAN live) | PLANNED |
| v3.1.0 | 2026-11-07 | Ecosystem expansion | PLANNED |
| v4.0.0 | 2027-Q1 | Advanced features | PLANNED |

---

## Quality Gate Criteria

### Pre-Commit

- black formatting: PASS
- isort import ordering: PASS
- flake8 linting: PASS
- markdownlint: PASS
- YAML validation: PASS
- Fast pytest suite (878 tests): PASS
- Lean 4 proofs (198 theorems): PASS
- LaTeX TODO check: PASS

### Pre-Push

- Fast pytest suite (no compilation): PASS
- Lint checks: PASS
- Docker digest consistency: PASS
- Semantic versioning consistency: PASS

### CI Pipeline (GitHub Actions)

- Lint (black, isort, flake8): PASS
- Dependency review: PASS
- Build LaTeX document: PASS
- Build all examples (50 parallel): PASS
- Language integration matrix (11 languages): PASS
- Lean 4 proof verification: PASS
- Visual regression (SSIM): PASS
- Performance regression (< 250% threshold): PASS
- Docker image build and push: PASS
- Documentation deployment: PASS
