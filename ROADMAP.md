# OmniLaTeX Roadmap

**Current version:** v2.5.0
**License:** Apache 2.0

---

## Current State Assessment

### Metrics (v2.5.0)

| Metric | Value | Delta from v2.4.1 |
|--------|-------|--------------------|
| Document types | 27 | -- |
| .sty modules | 31 | -- |
| Examples | 50 | -- |
| Institutions | 21 | -- |
| Languages | 25+ | -- |
| Python tests (fast) | 1711 | +346 |
| l3build test files | 94 | -- |
| Lean 4 proof modules | 29 | -- |
| buildlib coverage | 78% | +6% |
| CI platforms | 5 | -- |
| Documentation pages | 25+ | -- |
| Class options | 15 | +3 (enablelayout, enablebibliography, enablehyperref) |
| Web vitest tests | 14 | -- |

### Audit Results Summary (v2.5.0 Post-Audit)

| Area | Status | Key Findings |
|------|--------|--------------|
| Testing | PASS | 1431 fast tests passing, 107 skipped (numpy-dependent). 0 failures. |
| Web Testing | PASS | 14 vitest tests passing. ESLint clean (0 errors, 0 warnings). |
| Code Quality | PASS | black/isort/flake8 clean. Dead code removed, duplicated functions consolidated. |
| CI/CD Security | FIXED | All actions pinned to commit SHAs. bc float comparison fixed. Dead reusable workflows removed. |
| Dependabot | FIXED | npm directory corrected to /web. pip directory corrected to /tests. |
| Accessibility | IMPROVED | Focus trapping, Escape-to-close, aria-hidden on mobile nav, aria-current on active links. |
| SEO | IMPROVED | data-astro-prefetch on nav links. Active page indicator. |
| Code Deduplication | FIXED | slugToTitle and getBaseURL extracted to shared utils. SSIM formula deduplicated. |
| Dead Code | REMOVED | Unused @tanstack/solid-virtual. Unused CSS tokens. Unused CSS_COLORS dict. Dead CI workflows. |
| Documentation Accuracy | FIXED | CTAN_README version updated. SECURITY.md version added. Stats corrected across 5 files. |
| Test Isolation | FIXED | builder.REPO_ROOT monkeypatch bug causing real filesystem side effects. |
| Exception Safety | FIXED | Narrowed except Exception to specific types in _compile_example_worker. |
| Thread Safety | FIXED | Replaced timeout_flag mutable with threading.Event. |
| Cache Atomicity | FIXED | Atomic writes (temp+rename) prevent corruption on crash. |
| TOCTOU Race | FIXED | PDF size captured once, not re-stat'd in finally block. |
| Path Correctness | FIXED | Cleanup uses absolute paths from REPO_ROOT. |
| Formal Verification | PASS | 29 Lean4 modules. |
| Lazy Module Loading | ADDED | enablelayout, enablebibliography, enablehyperref options + minimal mode. |
| Design Tokens | FIXED | Web uses Spatial Materialism + Amoebic UI tokens. prefers-reduced-motion added. |

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

### Completed (v2.4.1)

- [x] Increase buildlib coverage to 65% (89 new tests for commands.py)
- [x] Add accessibility checker module (WCAG 2.1 AA automated tests)
- [x] Fix heading hierarchy in HTML pages (div to h1)
- [x] Add header/footer semantic elements to verify.html

### Completed (v2.5.0)

- [x] Fix test isolation bug (builder.REPO_ROOT monkeypatch)
- [x] Narrow exception handlers to specific types
- [x] Fix TOCTOU race on PDF stat in finally block
- [x] Replace timeout_flag with threading.Event
- [x] Atomic cache writes (temp file + os.replace)
- [x] Fix cleanup to use absolute paths from REPO_ROOT
- [x] Remove 3 unused imports across buildlib

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

### Completed (v2.4.1)

- [x] Profile and optimize LaTeX compilation for large documents (buildlib/profiler.py)
- [x] Benchmark and optimize SSIM comparison for 50-example builds (buildlib/ssim_benchmark.py)

### Completed (v2.5.0)

- [x] CI/CD security hardening (command injection, secret handling, path filters)
- [x] WCAG accessibility fixes (aria-live, touch targets, semantic roles)
- [x] 3 new Lean4 proof modules for hardened properties
- [x] Pre-push hook hardened (lint failures now block push)

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
- [x] Package manager distribution (Nix flake app, Homebrew formula, AUR package)
- [x] Docker image multi-arch builds (amd64 + arm64, already configured)

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
- [x] Plugin system specification and sandbox (manifest.toml, registry)
- [x] VS Code extension marketplace preparation guide
- [x] Language expansion scaffolding (40+ languages target)

### Completed (v2.4.1)

- [x] Plugin system expansion (plugin_manager.py, registry, sandbox, validation)
- [x] Plugin examples (markdown-table, watermark)
- [x] Interactive documentation site (template picker, live preview)
- [x] Full accessibility compliance (WCAG 2.1 AA automated tests, 126 tests)

---

## Phase 5: Advanced Features (v4.0.0) -- 12-16 weeks

### Completed (v2.4.1)

- [x] Formal verification expansion (301 theorems, up from 223)
- [x] 4 new proof modules (TypographicConstraints, OutputFormats, LaTeXPackageDependencies, DocumentClassHierarchy)
- [x] 7 existing proof modules extended with additional theorems

### In Progress (v2.5.0)

- [x] WASM feasibility report (specs/wasm_feasibility.md)
- [x] WASM editor prototype (wasm/editor/index.html)
- [x] WebSocket compilation server (wasm/server/main.py)
- [ ] Pure WASM LuaTeX compilation (6-12 months, requires dedicated effort)
- [ ] Tauri desktop app (deferred to after WASM)

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
| 15 | buildlib 0% test coverage | High | FIXED (73%) |
| 16 | CommandRunner timeout bug | High | FIXED |
| 17 | CI secret leakage via echo | Critical | FIXED |
| 18 | CI script injection via matrix | Critical | FIXED |
| 19 | CI overly broad permissions | High | FIXED |
| 20 | UI missing ARIA semantics | High | FIXED |
| 21 | Broken gallery-app.html link | High | FIXED |
| 22 | No prefers-reduced-motion | Medium | FIXED |
| 23 | buildlib coverage < 60% | Medium | FIXED (73%) |
| 24 | Inline CSS in HTML pages | Medium | FIXED |
| 25 | CSP unsafe-inline | High | FIXED |
| 26 | No favicon on HTML pages | Medium | FIXED |
| 27 | No og:image on HTML pages | Medium | FIXED |
| 28 | check_semver.py f-string bug | Medium | FIXED |
| 29 | No lightbox focus trapping | Medium | FIXED |
| 30 | No print stylesheets | Low | FIXED |
| 31 | Missing CSS style tags in HTML pages | High | FIXED |
| 32 | Dead code after \endinput in 4 modules | High | FIXED |
| 33 | Hard assert in git-metadata.lua | Medium | FIXED |
| 34 | Redundant luatexbase fetch in conditional-include | Low | FIXED |
| 35 | Duplicate RequirePackage{silence} | Low | FIXED |
| 36 | Missing .dockerignore | Medium | FIXED |
| 37 | CI test suite inconsistency (Forgejo/Gitea) | Medium | FIXED |
| 38 | Performance regression threshold too generous | Medium | FIXED |
| 39 | buildlib commands.py low coverage | High | FIXED (80%) |
| 40 | No plugin manager/validation | Medium | FIXED |
| 41 | Lean 4 proofs below 300 | Medium | FIXED (301) |
| 42 | No automated accessibility testing | Medium | FIXED |
| 43 | No LaTeX compilation profiler | Low | FIXED |
| 44 | No SSIM benchmark suite | Low | FIXED |
| 45 | builder.py discover_examples relative path bug | High | FIXED |
| 46 | test_ssim_benchmark.py missing numpy import in try block | Medium | FIXED |
| 47 | dependabot/fetch-metadata unpinned action | Moderate | FIXED |
| 48 | performance-regression.yml 90m timeout | Medium | FIXED (45m) |
| 49 | docker-ci.yml 180m timeout | Low | FIXED (120m) |
| 50 | setup-texlive hardcoded year 2026 | Medium | FIXED |
| 51 | GitLab templates hardcoded /assign @alex | Low | FIXED |
| 52 | Gallery select focus outline:none a11y violation | High | FIXED |
| 53 | Card elements missing accessible names | High | FIXED |
| 54 | verify.js &mdash; HTML entity in textContent | Medium | FIXED |
| 55 | Duplicate inline CSS in 3 HTML pages (~500 lines) | Medium | FIXED |
| 56 | builder.REPO_ROOT test isolation bug | High | FIXED |
| 57 | except Exception too broad in _compile_example_worker | High | FIXED |
| 58 | TOCTOU race on PDF stat in finally block | High | FIXED |
| 59 | timeout_flag mutable (unsafe under free-threaded Python) | Medium | FIXED |
| 60 | Non-atomic cache writes (corruption on crash) | High | FIXED |
| 61 | cleanup.py uses relative paths (CWD-dependent) | High | FIXED |
| 62 | CI command injection via matrix interpolation | Critical | FIXED |
| 63 | CI secret logging via echo-pipe docker login | Critical | FIXED |
| 64 | CI missing path filters (wasteful doc-only builds) | Medium | FIXED |
| 65 | Gallery role=tablist on non-tab grid | High | FIXED |
| 66 | Verify status not in aria-live region | High | FIXED |
| 67 | Lightbox close button below WCAG touch target | Medium | FIXED |

### New (v2.5.0 Post-Audit)

| # | Item | Priority | Status |
|---|------|----------|--------|
| 68 | Duplicate slugToTitle in 2 docs files | Low | FIXED (extracted to lib/utils.ts) |
| 69 | Duplicate base URL calc in 7 files | Low | FIXED (extracted to lib/utils.ts) |
| 70 | Unused @tanstack/solid-virtual dep | Low | FIXED (removed) |
| 71 | Unused CSS tokens (--bg-surface, --depth-3, --radius-lg) | Low | FIXED (removed) |
| 72 | Dead .category-tabs [role=tablist] CSS rule | Low | FIXED (removed) |
| 73 | Unused CSS_COLORS dict in accessibility_checker.py | Low | FIXED (removed) |
| 74 | Redundant `import time as _time` in 2 files | Low | FIXED |
| 75 | Duplicated SSIM formula in ssim_benchmark.py | Low | FIXED |
| 76 | Emoji in commands.py output | Low | FIXED (PASS/FAIL text) |
| 77 | ESLint missing TypeScript parser | High | FIXED |
| 78 | Hamburger menu no keyboard trap/Escape | High | FIXED |
| 79 | No active page indicator in nav | Medium | FIXED |
| 80 | No aria-hidden on hamburger SVG | Low | FIXED |
| 81 | No data-astro-prefetch on nav links | Low | FIXED |
| 82 | CTAN_README.txt stale version (v2.4.0) | High | FIXED (v2.5.0) |
| 83 | SECURITY.md missing v2.5.x row | High | FIXED |
| 84 | docs/index.md stale stats | High | FIXED |
| 85 | FAQ.md wrong Monaspace Neon URL | Medium | FIXED |
| 86 | Dependabot npm dir watches / instead of /web | Medium | FIXED |
| 87 | Dependabot pip dir watches / instead of /tests | Medium | FIXED |
| 88 | lean4-ci.yml bc float comparison silently fails | Critical | FIXED |
| 89 | Dead _docker-setup.yml reusable workflow | Low | FIXED (removed) |
| 90 | Dead setup-texlive composite action | Low | FIXED (removed) |
| 91 | actions/checkout@v6 tag (28 occurrences) | High | FIXED (SHA-pinned) |
| 92 | actions/setup-node@v4 tag | Medium | FIXED (SHA-pinned) |
| 93 | actions/github-script@v9 tag | Medium | FIXED (SHA-pinned) |
| 94 | buildlib watch.py/ssim_benchmark.py redundant import time | Low | FIXED |
| 95 | Validator.tsx unused copied state | Low | FIXED |
| 96 | Validator.tsx map instead of For in lists | Low | FIXED |
| 97 | Validator.tsx options not reactive | Low | FIXED |
| 98 | ROADMAP-v3.md in root (should be archived) | Low | FIXED (moved to docs/archived/) |
| 99 | Test count inconsistency across 7+ files | High | FIXED (updated to 1711) |

### Remaining Items (v2.5.0 Post-Audit)

| # | Item | Priority | Status |
|---|------|----------|--------|
| 100 | i18n JSON files exist but never imported (dead code) | Medium | OPEN |
| 101 | German translation missing umlauts | Medium | OPEN |
| 102 | lang="en" hardcoded despite i18n infrastructure | Medium | OPEN |
| 103 | Missing og:image/twitter:image for social sharing | Low | OPEN |
| 104 | No JSON-LD structured data | Low | OPEN |
| 105 | Doc sidebar only has back link, no TOC | Low | OPEN |
| 106 | No responsive mobile padding override on doc headers | Low | OPEN |
| 107 | PDF viewer styles defined but no component | Low | OPEN |
| 108 | No typography scale tokens (font sizes hardcoded) | Low | OPEN |
| 109 | px units instead of rem in many layout values | Low | OPEN |
| 110 | FAQ.md claims CTAN not available (may be stale) | Medium | OPEN |
| 111 | build.py builder.py coverage still 60% (rich dependency) | Medium | OPEN |
| 112 | accessibility_checker.py coverage 68% (bs4/numpy gaps) | Medium | OPEN |
| 113 | Duplicate build command construction in builder.py/profiler.py | Low | OPEN |
| 114 | Duplicate log parsing error handler in builder.py/profiler.py | Low | OPEN |
| 115 | Violation.line field in accessibility_checker never populated | Low | OPEN |
| 116 | VS Code extension doctype naming vs web naming inconsistency | Medium | OPEN |
| 117 | VS Code legacy latex.json broken choice syntax | Low | OPEN |
| 118 | VS Code galleryBanner color mismatch with design system | Low | OPEN |
| 119 | VS Code DiagnosticCollection not disposed in deactivate() | Low | OPEN |
| 120 | Docs manual PART_I claims build.py is 2094 lines | Medium | OPEN |

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
| v2.5.0 | 2026-06-07 | Exhaustive audit: test isolation, buildlib hardening, CI/CD security, WCAG | RELEASED |
| v2.4.1 | 2026-06-06 | Audit: tests, CI/CD, UI/UX, design tokens, packages | RELEASED |
| v2.4.0 | 2026-06-05 | Audit fixes, buildlib tests | RELEASED |
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
- Fast pytest suite (1711 tests): PASS
- Lean 4 proofs (29 modules): PASS
- LaTeX TODO check: PASS

### Pre-Push

- Fast pytest suite (no compilation): PASS (blocks on failure)
- Lint checks: PASS (blocks on failure)
- Docker digest consistency: PASS (blocks on failure)
- Semantic versioning consistency: PASS (blocks on failure)

### CI Pipeline (GitHub Actions)

- Lint (black, isort, flake8): PASS
- Dependency review: PASS
- Build LaTeX document: PASS
- Build all examples (50 parallel): PASS
- Language integration matrix (11 languages): PASS
- Lean 4 proof verification: PASS
- Visual regression (SSIM): PASS
- Performance regression (< 100% threshold): PASS
- Docker image build and push: PASS
- Documentation deployment: PASS
