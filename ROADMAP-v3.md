# OmniLaTeX Roadmap (v3 Archive)

> **This file is archived.** The active roadmap is [`ROADMAP.md`](ROADMAP.md).

This document contains the detailed v3 planning breakdown that has been consolidated into the active roadmap..0

**Date:** 2026-05-26 | **Current:** v2.2.0 | **Target:** v4.0.0 | **License:** Apache 2.0

---

## Current Status (v2.2.0)

| Metric | Value |
|--------|-------|
| Version | v2.2.0 (2026-05-26) |
| Document types | 27 (55+ aliases), 3 KOMA-Script base classes + Beamer |
| `.sty` modules | 31 across 9 subdirectories (`lib/`) |
| Examples | 48 templates (all compile on TeX Live 2025+) |
| Institutions | 21 configs (aalto, cambridge, cmu, columbia, epfl, eth, harvard, imperial, kit, mit, ntnu, oxford, princeton, stanford, tudelft, tuhh, tum, uoft, yale + generic) |
| Languages | 25+ via polyglossia (CJK, RTL, Cyrillic, Thai, Bengali) |
| Tests (fast) | 771 passing, 52 skipped |
| Lean 4 proofs | 198 theorems, 0 sorry, 16 proof modules |
| CI/CD | 15 GitHub Actions workflows (incl. Cloudflare Pages) + GitLab/Gitea/Forgejo/Woodpecker |
| Docker | Multi-arch (amd64/arm64), digest-synced, GHCR-hosted |
| Documentation | MkDocs Material (19 pages) |
| Determinism | Byte-for-byte reproducible PDFs via SOURCE_DATE_EPOCH |
| Distribution | CTAN submission pending review |
| VS Code extension | Build-on-save, 27 doctype snippets, log diagnostics |
| Export formats | HTML (LaTeXML), EPUB, DOCX (pandoc) via `build.py export` |
| Citation styles | 15 pre-configured |
| Security | Conditional shell-escape, CSP headers, PDF Gallery pipeline |
| Build system | `buildlib/` package (9 modules, mixin composition), 14-line `build.py` wrapper |

---

## Phase 1: Stabilization (v2.2.0)

**Timeline:** 3-4 weeks | **Priority:** Critical | **Branch:** `release/v2.2`

### 1.1 Decompose build.py Monolith

**STATUS: DONE** (`f47e98b`) — Decomposed into `buildlib/` package with 9 modules using mixin composition.

The 2915-line `build.py` was decomposed into a `buildlib/` package:

| Component | Lines | Module |
|-----------|-------|--------|
| Constants, ProjectConfig, REPO_ROOT | 37 | `buildlib/config.py` |
| TerminalOutput with color support | 45 | `buildlib/ui.py` |
| CommandRunner subprocess wrapper | 68 | `buildlib/runner.py` |
| SSIM visual regression | 53 | `buildlib/diff.py` |
| Build core mixin (compile, cache, build) | 752 | `buildlib/builder.py` |
| Commands mixin (doctor, lint, check, etc.) | 1527 | `buildlib/commands.py` |
| Interactive menu (rich + simple) | ~250 | `buildlib/tui.py` |
| CLI main() with argparse | ~250 | `buildlib/cli.py` |
| Package init (composes BuildTasks) | 21 | `buildlib/__init__.py` |
| Entry point | 14 | `build.py` (thin wrapper) |

**Acceptance Criteria:**

- `build.py` is 14 lines (imports + main)
- Each module is independently importable
- All 771 tests pass without modification
- No new dependencies introduced
- Named `buildlib/` to avoid conflict with gitignored `build/`

**Effort:** 16h

### 1.2 Automate Version String Propagation

**STATUS: DONE** (`a93b270`) — `scripts/sync_versions.py` propagates version from VERSION.md to 35+ files.

Version string `v2.1.0` was hardcoded in 70+ locations. `sync_versions.py` reads `VERSION.md` and patches all `\ProvidesPackage` lines, `build.lua`, CI workflow references, and other files. Pre-commit validates version consistency.

**Deliverables:**

- Single source of truth: `VERSION.md`
- `scripts/sync_versions.py` patches all locations
- Pre-push hook validates version consistency via `check-semver`
- Idempotent: running twice produces no diff

**Acceptance Criteria:**

- `grep -rn` for old version after sync returns zero results (excluding CHANGELOG, ROADMAP)
- `make check-semver` passes
- Running `sync_version.py` twice is idempotent (no diff on second run)

**Effort:** 6h

### 1.3 Fix Test Skip Behavior

**STATUS: DONE** (`a074d5a`) — Module-level skips replaced with per-test `@pytest.mark.skipif`.

`test_properties.py` uses `@pytest.mark.skipif(not HAS_HYPOTHESIS, ...)` on 7 hypothesis-dependent tests only (not the whole file). `test_visual_regression.py` uses the same pattern for 4 pymupdf-dependent tests. All other tests run regardless of optional deps.

**Deliverables:**

- Refactor to per-test `pytest.importorskip()` or `@pytest.mark.skipif` decorators
- CI matrix explicitly installs `hypothesis` and `pymupdf` in relevant jobs
- Document required test dependencies in `tests/README.md`
- `Makefile` test-fast target remains functional without optional deps (graceful skip)

**Acceptance Criteria:**

- `pytest --co` lists all tests even without optional deps installed
- Individual tests skip (not entire files)
- CI installs full test dependency set; zero skips in CI

**Effort:** 4h

### 1.4 Consolidate Stale Roadmap Files

**STATUS: DONE** (`c8ad070`) — 10 stale roadmap files consolidated to 2.

Nine roadmap files exist with overlapping, contradictory, and outdated content:

```
ROADMAP.md                    -- generic, stale
ROADMAP-ARCHIVED-v1.1.md      -- historical
ROADMAP-ARCHIVED-v1.5.md      -- historical
ROADMAP-DETAILED.md           -- outdated metrics
ROADMAP-MASTER.md             -- most current, but v2.0.0 dated
ROADMAP-PATH-FORWARD.md       -- redundant with MASTER
ROADMAP-PRODUCTION-FINAL.md   -- redundant with MASTER
ROADMAP-PRODUCTION.md         -- redundant with MASTER
ROADMAP-v2.md                 -- superseded
```

**Deliverables:**

- Keep `ROADMAP-v3.md` (this file) as the single active roadmap
- Move all others to `docs/archived/roadmaps/` (preserve git history)
- `ROADMAP.md` becomes a one-line redirect: `See ROADMAP-v3.md`
- Update `CONTRIBUTING.md` and `README.md` to reference `ROADMAP-v3.md`

**Acceptance Criteria:**

- Root directory contains exactly one active roadmap file
- All historical content preserved in `docs/archived/roadmaps/`
- No broken internal links after move

**Effort:** 2h

### 1.5 CTAN Shell Script Test Alignment

**STATUS: OPEN** — Python reimplementation and shell script still diverge. `zip` binary availability in CI is a blocker for subprocess-based approach.

**Deliverables:**

- `test_ctan.py` invokes `make-ctan-zip.sh --dry-run` and asserts on its output
- Python reimplementation removed or relegated to a cross-check (warn on divergence)
- CI runs both and asserts equivalence

**Acceptance Criteria:**

- CTAN test uses actual shell script (or subprocess call to it)
- Divergence between script and test triggers CI failure

**Effort:** 3h

### 1.6 Address shell-escape Security Posture

**STATUS: DONE** (`eb9fea4`) — `OMNILATEX_SHELL_ESCAPE` env var controls conditional enable.

Default is enabled (1) for backwards compatibility. Set `OMNILATEX_SHELL_ESCAPE=0` to disable. Only `minted` (Pygments) and `svg` (Inkscape) require shell-escape. `.latexmkrc` reports status on every invocation. Remaining: `--shell-escape=restricted` support, listings fallback, Docker `TEXMF.cnf` restriction.

**Deliverables:**

- Document the security implications in `SECURITY.md` (already partially addressed)
- Add `--shell-escape=restricted` support for engines that support it (LuaLaTeX >= 1.17)
- Add `--no-shell-escape` flag to `build.py` that disables minted and falls back to `listings`
- Default to `--shell-escape` for backward compatibility; warn in `build.py doctor` output
- Restrict `shell_escape_commands` in `TEXMF.cnf` template for Docker image

**Acceptance Criteria:**

- `build.py --no-shell-escape` produces valid PDFs with listings fallback
- `build.py doctor` reports shell-escape status and associated risk
- Docker image restricts allowed shell-escape commands

**Effort:** 6h

---

## Phase 2: Performance (v2.3.0)

**Timeline:** 3-4 weeks | **Priority:** High | **Branch:** `release/v2.3`

### 2.1 SSIM Computation Acceleration

**STATUS: DONE** (`a93b270`) — Vectorized with `scipy.signal.fftconvolve` + numpy fallback.

Pure Python loops replaced with vectorized sliding window (Wang 2004). Falls back to `np.einsum`-based convolution when scipy is unavailable.

**Deliverables:**

- Replace pure Python SSIM with `numpy` vectorized sliding window (Wang 2004)
- Fallback to pure Python only if `numpy` unavailable
- Benchmark: >= 10x speedup on 100-page document comparison
- Integration with `test_visual_regression.py`

**Acceptance Criteria:**

- Visual regression test suite completes in < 30s (currently > 5min for full suite)
- Numerical results identical to current implementation (within float epsilon)
- `numpy` listed as optional dependency only

**Effort:** 4h

### 2.2 Parallel Example Building

**STATUS: ALREADY EXISTS** — `--jobs N` flag with `ThreadPoolExecutor` has been in `build.py` since before this roadmap.

Default is `os.cpu_count()`. Deterministic output with `SOURCE_DATE_EPOCH` propagation. Progress reporting with Rich dashboard or TQDM fallback.

**Deliverables:**

- Add `--jobs N` flag (default: `os.cpu_count()`)
- Use `concurrent.futures.ProcessPoolExecutor` for parallel compilation
- Ensure deterministic output: `SOURCE_DATE_EPOCH` propagation, no write conflicts
- Progress reporting with per-example timing

**Acceptance Criteria:**

- `build.py build-examples --jobs 4` completes in <= 25% of single-threaded time
- Output PDFs are byte-identical regardless of parallelism level
- No file handle exhaustion on large job counts

**Effort:** 8h

### 2.3 Build Cache Improvements

Current cache saves/loads per-file. Batch operations should reduce I/O syscalls.

**Deliverables:**

- Single atomic cache file (JSON or SQLite) instead of per-file `.cache` entries
- Cache key includes: source hash, TeX Live version, omnilatex version, module list
- Cache invalidation on version bump (automatic with Phase 1.2)
- `build.py cache --clear` and `build.py cache --stats` subcommands

**Acceptance Criteria:**

- Build-all I/O operations reduced from N file reads to 1
- Cache hit rate > 90% on incremental builds
- Cache corruption detected and auto-repaired

**Effort:** 6h

### 2.4 CI Pipeline Optimization

14 workflows with redundant setup and no caching between runs.

**Deliverables:**

- Shared `actions/` composite actions for TeX Live install, Python setup
- `actions/cache` for `~/.texlive`, `~/.cache/pip`, `.pytest_cache`
- Merge `build.yml` + `build-examples.yml` (unnecessary split)
- Reduce total CI minutes by >= 30%

**Acceptance Criteria:**

- PR CI feedback in < 10 minutes (currently ~15-20 min)
- No duplicate TeX Live installations across workflow jobs
- Cache hit rate > 80% on repeat runs

**Effort:** 8h

### 2.5 Lean 4 Proof Performance

198 theorems verified in CI. Lake build time should be tracked and optimized.

**Deliverables:**

- Add proof verification timing to CI output
- Set regression threshold (e.g., >= 20% slower triggers investigation)
- Cache `.lake` build artifacts between CI runs

**Acceptance Criteria:**

- Lean 4 CI step completes in < 5 minutes
- Timing regressions are caught automatically

**Effort:** 3h

---

## Phase 3: Distribution (v3.0.0)

**Timeline:** 6-8 weeks | **Priority:** High | **Branch:** `release/v3.0`

### 3.1 CTAN Publication

CTAN submission is pending. Publication unlocks TeX Live and MiKTeX distribution.

**Deliverables:**

- Confirm CTAN review feedback and address any required changes
- Verify `tlmgr install omnilatex` works after CTAN listing
- Set up automated CTAN upload via `ctan-upload.sh` on tagged releases
- Add CTAN badge to `README.md`
- Monitor TeX Live inclusion for next yearly freeze

**Acceptance Criteria:**

- Package listed at `https://ctan.org/pkg/omnilatex`
- `tlmgr install omnilatex` succeeds on TeX Live 2025/2026
- Automated upload on `v*` tag push

**Effort:** 8h (including review iteration)

### 3.2 Overleaf Template Gallery

**Deliverables:**

- Submit 3-5 top templates to Overleaf gallery (thesis, article, beamer, CV, report)
- Automated Overleaf zip generation validated by `make-overleaf-zip.sh`
- Add "Open in Overleaf" badge/buttons to documentation

**Acceptance Criteria:**

- Templates searchable on overleaf.com/templates
- One-click "Open in Overleaf" works from docs site

**Effort:** 4h

### 3.3 Package Manager Distribution

**Deliverables:**

- Nix flake: `nix run github:WyattAu/OmniLaTeX` produces a compiled example
- Homebrew tap: `brew install omnilatex` installs class files + build tool
- AUR package: `yay -S omnilatex` for Arch Linux users
- Each package auto-updates on release via CI

**Acceptance Criteria:**

- Each package manager install tested in CI (Docker-based)
- Installation completes in < 2 minutes on clean system
- Installed files match CTAN TDS structure

**Effort:** 16h

### 3.4 PDF Gallery Functional Deployment

**STATUS: DONE** (`22e98b7`) — PDF download pipeline deployed.

CI downloads PDFs from build-examples workflow artifacts and includes them in the docs site deployment. Gallery page serves PDFs with `Content-Disposition: inline` headers. Remaining: thumbnail generation, size optimization.

**Deliverables:**

- CI job builds all 48 examples and uploads PDFs to GitHub Pages artifact
- Gallery page renders thumbnails with download links
- PDFs served with `Content-Disposition: inline` headers
- Total gallery size < 200MB (optimize with `gs -dPDFSETTINGS=/ebook`)

**Acceptance Criteria:**

- Every example in the gallery has a downloadable, viewable PDF
- Gallery page loads in < 3 seconds
- Mobile-responsive layout

**Effort:** 8h

### 3.5 Cloudflare Pages Activation or Removal

**STATUS: DONE** (`d12bcf7`) — Cloudflare Pages workflow added for Forgejo repos.

`wrangler.toml` updated for Pages compatibility. `.github/workflows/cloudflare-pages.yml` deploys to Cloudflare Pages on push to main. GitHub Pages remains primary for GitHub-hosted repos. Forgejo repos use Cloudflare Pages via this workflow.

### 3.6 CSP Headers on Web Assets

**STATUS: DONE** (`22e98b7`) — CSP headers deployed via GitHub Pages `_headers` file and `wrangler.toml`.

**Deliverables:**

- Define CSP policy appropriate for MkDocs Material site
- Add headers via chosen deployment mechanism (Cloudflare Pages `_headers`, or GitHub Pages meta tags)
- CSP report-only mode initially; enforce after 2-week observation period
- Document policy in `SECURITY.md`

**Acceptance Criteria:**

- `curl -I <docs-url>` returns `Content-Security-Policy` header
- No CSP violations on any documentation page
- Report URI endpoint configured for violation monitoring

**Effort:** 4h

---

## Phase 4: Ecosystem (v3.1.0)

**Timeline:** 6-8 weeks | **Priority:** Medium | **Branch:** `release/v3.1`

### 4.1 Plugin System Expansion

`omnilatex-plugin.sty` exists with `\useplugin` command. Expand into a discoverable ecosystem.

**Deliverables:**

- Plugin manifest schema (`omnilatex-plugin.json`): name, version, author, compatibility range
- Plugin registry (initially a JSON file in the repo, later a separate service)
- `build.py plugin install <name>`: downloads `.sty` to local project
- `build.py plugin list`: lists available plugins
- Sandbox: third-party plugins loaded in restricted mode, cannot override core modules
- Plugin template generator: `build.py scaffold-plugin <name>`

**Acceptance Criteria:**

- Third-party `.sty` files load via `\useplugin` without modifying core
- Plugin version conflicts detected and reported
- Plugin API stability guaranteed within minor version

**Effort:** 24h

### 4.2 Institution Contribution Pipeline

21 institutions exist. Reduce friction for community contributions.

**Deliverables:**

- `build.py scaffold-institution` creates complete config directory from template
- Interactive wizard: university name, colors, logo upload, degree types
- Automated validation: compiles test document, passes `check-semver`
- Preview deployment: CI builds a sample PDF for each new institution PR
- Contributing guide: `docs/INSTITUTION_CONTRIBUTING.md` (exists, enhance with examples)

**Acceptance Criteria:**

- New institution PR requires only 3 files: `config.yaml`, `logo.pdf`, `translations.json`
- CI validates and previews every institution PR automatically
- Merge checklist documented and enforced via PR template

**Effort:** 12h

### 4.3 VS Code Extension Marketplace

Extension is packaged but not published to the Open VSX Registry or VS Code Marketplace.

**Deliverables:**

- Publish to VS Code Marketplace (`ext install omnilatex`)
- Publish to Open VSX Registry (VSCodium, Gitpod, etc.)
- Automated publishing on release via GitHub Actions
- Extension README with screenshots and GIF demo

**Acceptance Criteria:**

- `code --install-extension omnilatex` succeeds
- Extension featured in "LaTeX" category search results
- Automated CI publishes on `v*` tag

**Effort:** 6h

### 4.4 Language Expansion to 40+

25+ languages currently supported. Target 40+ for comprehensive coverage.

**Deliverables:**

- Add 15 new language translation files (priority: Vietnamese, Indonesian, Tamil, Telugu, Urdu, Kazakh, Ukrainian, Romanian, Czech, Hungarian, Finnish, Greek, Turkish, Catalan, Basque)
- Each language requires: 47 translation keys, 1 test fixture, 1 example document
- polyglossia compatibility matrix documented per language
- RTL testing for Urdu, Arabic, Hebrew, Persian, Kurdish

**Acceptance Criteria:**

- All 40+ languages compile in at least 3 doctypes
- Translation coverage > 95% for every language
- `build.py doctor` reports language support matrix

**Effort:** 24h

### 4.5 Interactive Documentation Site

Enhance MkDocs site with interactive features.

**Deliverables:**

- Template picker: select doctype + language + institution, download zip
- Live LaTeX preview (client-side, via WebAssembly LaTeX or pre-rendered PDFs)
- Search across all documentation, examples, and API reference
- Contributing section with "good first issue" integration
- Analytics: page views, search queries, download counts

**Acceptance Criteria:**

- Template picker generates valid, compilable zip for any combination
- Search returns relevant results within 200ms
- Site passes accessibility audit (WCAG 2.1 AA)

**Effort:** 20h

---

## Phase 5: Advanced Features (v4.0.0)

**Timeline:** 12-16 weeks | **Priority:** Low (long-term) | **Branch:** `main`

### 5.1 Cloud Compilation API

REST API for PDF generation without local TeX installation.

**Deliverables:**

- API specification (OpenAPI 3.1): `POST /compile` accepts `.tex` + options, returns PDF
- Reference implementation: Docker-based, using existing `build.py` infrastructure
- Rate limiting, input sanitization, sandboxed compilation
- WebSocket support for live compilation logs
- Free tier: 100 compilations/month, paid tier via API key

**Acceptance Criteria:**

- API compiles all 48 examples correctly
- Request-to-PDF latency < 30s for 50-page documents
- No shell-injection vectors (sandboxed LuaLaTeX, no shell-escape)

**Effort:** 40h

### 5.2 Collaborative Editing Support

Live preview and multi-user editing integration.

**Deliverables:**

- LSP server for OmniLaTeX (diagnostics, completion, formatting)
- Integration with existing VS Code extension
- Live preview: recompile on save with incremental build cache
- Optional: CRDT-based collaborative editing protocol

**Acceptance Criteria:**

- LSP server starts in < 2s, provides completions within 100ms
- Live preview updates within 2s of save
- VS Code extension communicates with LSP server

**Effort:** 60h

### 5.3 Visual Template Designer

Browser-based GUI for creating institution and doctype configurations.

**Deliverables:**

- Single-page app (React or Svelte)
- Visual page layout editor: margins, fonts, colors, headers/footers
- Export to `config.yaml` + `.sty` files
- Import existing institution configs for editing
- Preview renders via Cloud Compilation API

**Acceptance Criteria:**

- Designer produces valid configs that compile without modification
- Round-trip: import -> edit -> export produces equivalent output
- Usable without LaTeX knowledge

**Effort:** 80h

### 5.4 Formal Verification Expansion

198 Lean 4 theorems verified. Target 400+ with coverage of more critical paths.

**Deliverables:**

- Proof coverage for all module load-order dependencies
- Proof coverage for page geometry calculation correctness
- Proof coverage for language fallback chains
- Proof coverage for institution config validation rules
- Continuous proof verification blocks merge on failure (already implemented)

**Acceptance Criteria:**

- >= 400 theorems, 0 sorry
- All critical module interaction properties proven
- Proof verification < 10 minutes in CI

**Effort:** 40h

### 5.5 Accessibility Compliance

PDF/UA-1 support exists (`omnilatex-accessibility.sty`). Expand to full compliance.

**Deliverables:**

- All 48 examples pass PDF/UA-1 validation (veraPDF)
- Tagged PDF output with correct reading order
- Alt-text required for all images (build warning if missing)
- MathML fallback for mathematical content
- WCAG 2.1 AA compliance for documentation site

**Acceptance Criteria:**

- veraPDF reports zero violations on all example PDFs
- Screen reader testing passes on 3 representative doctypes
- Accessibility audit documented

**Effort:** 24h

---

## Technical Debt Register

| # | Item | Priority | Effort | Phase | Status |
|---|------|----------|--------|-------|--------|
| 1 | `build.py` 2915-line monolith | P0 | 16h | 1.1 | **DONE** (f47e98b) |
| 2 | Version string hardcoded in 70+ locations | P0 | 6h | 1.2 | **DONE** (a93b270) |
| 3 | `test_properties.py` skips entire file | P1 | 4h | 1.3 | **DONE** (a074d5a) |
| 4 | `test_visual_regression.py` skips entire file | P1 | (included in 1.3) | 1.3 | **DONE** (a074d5a) |
| 5 | 9 stale roadmap files | P1 | 2h | 1.4 | **DONE** (c8ad070) |
| 6 | CTAN zip test uses Python reimplementation | P1 | 3h | 1.5 | Open |
| 7 | `--shell-escape` always enabled | P1 | 6h | 1.6 | **DONE** (eb9fea4) |
| 8 | SSIM pure Python loops (slow) | P2 | 4h | 2.1 | **DONE** (a93b270) |
| 9 | `wrangler.toml` unused (dead config) | P2 | 4h | 3.5 | **DONE** (d12bcf7) |
| 10 | No CSP headers on web assets | P2 | 4h | 3.6 | **DONE** (22e98b7) |
| 11 | PDF Gallery non-functional (no PDFs uploaded) | P1 | 8h | 3.4 | **DONE** (22e98b7) |
| 12 | No parallel example building | P2 | 8h | 2.2 | **ALREADY EXISTS** |
| 13 | CI workflows have redundant setup | P2 | 8h | 2.4 | **DONE** (composite actions: setup-python, setup-texlive, read-docker-digest) |
| 14 | Build cache is per-file I/O | P3 | 6h | 2.3 | **DONE** — `_shared_build_cache` dict loaded/saved once per batch; single JSON file |

---

## Metrics Targets

| Metric | v2.2.0 (Current) | v2.3.0 Target | v3.0.0 Target | v4.0.0 Target |
|--------|-------------------|---------------|---------------|---------------|
| Document types | 27 | 27 | 30+ | 40+ |
| `.sty` modules | 31 | 31 | 35+ | 45+ |
| Examples | 48 | 48 | 60+ | 80+ |
| Institutions | 21 | 25+ | 35+ | 50+ |
| Languages | 25+ | 30+ | 40+ | 50+ |
| Tests (fast) | 771 | 800+ | 1200+ | 2000+ |
| Test coverage (critical paths) | >95% | >97% | >99% | >99.5% |
| Lean 4 theorems | 198 | 250+ | 300+ | 400+ |
| Build time (all examples, 1 thread) | ~8 min | ~6 min | ~5 min | ~4 min |
| Build time (all examples, parallel) | ~2 min | ~2 min | ~1.5 min | ~1 min |
| CI success rate | >97% | >98% | >99% | >99.5% |
| CI PR feedback time | ~15 min | ~10 min | <8 min | <5 min |
| Documentation pages | 19+ | 20+ | 40+ | 60+ |
| `build.py` lines | 14 | 14 | 14 | 14 |
| Version hardcoded locations | 0 | 0 | 0 | 0 |
| PDF Gallery examples with PDFs | 48 | 48 | 48 | 60+ |
| Package manager distributions | 1 (Docker) | 1 | 4+ | 6+ |
| Citation styles | 15 | 15 | 20+ | 25+ |
| CSP enforced | Yes | Yes | Yes | Yes |

---

## Release Cadence

| Version | Target Date | Focus |
|---------|-------------|-------|
| v2.2.0 | 2026-06-20 | Stabilization: build.py decomposition, version automation, test fixes |
| v2.3.0 | 2026-07-18 | Performance: SSIM, parallel builds, CI optimization |
| v3.0.0 | 2026-09-12 | Distribution: CTAN live, package managers, gallery, CSP |
| v3.1.0 | 2026-11-07 | Ecosystem: plugins, institutions, VS Code marketplace, languages |
| v4.0.0 | 2027-Q1 | Advanced: cloud API, LSP, visual designer, formal verification |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| CTAN rejection (formatting, licensing) | Medium | High | Pre-validate with `ctan-o-mat`, follow TDS conventions strictly |
| TeX Live breaking changes | Low | High | Pin to TeX Live 2025, test against pretest channel |
| Lean 4 toolchain incompatibility | Medium | Medium | Pin `lean-toolchain`, update proofs on stable releases |
| `build.py` decomposition regressions | Medium | High | Comprehensive test suite before refactor; feature-freeze during Phase 1 |
| npm/Node.js 20 deprecation in GHA | High | Low | Update to Node.js 24-compatible actions by June 2026 |
| Docker image supply chain attack | Low | Critical | SHA-pin all actions, digest-sync across CI configs, SBOM tracking |
| Cloudflare Pages config drift | Low | Low | Decide and act in Phase 3 (activate or delete) |
| Plugin system security vulnerabilities | Medium | High | Sandbox third-party plugins, restricted mode, no core module overrides |
| Documentation site performance degradation | Low | Medium | Cache headers, lazy-load PDFs, monitor Core Web Vitals |

---

## Contributing

See `CONTRIBUTING.md` for guidelines. Priority areas for external contributions:

1. Institution configs (low barrier, high impact)
2. Language translations (47 keys per language)
3. Example templates
4. Plugin development (after Phase 4.1)

This roadmap supersedes all previous roadmap files. Historical roadmaps are archived in `docs/archived/roadmaps/`.
