# OmniLaTeX Detailed Roadmap

**Current version:** v1.25.0 | **Date:** 2026-05-11 | **License:** Apache 2.0

---

## Current State Assessment

### What Works (v1.25.0)

| Area | Status | Details |
|------|--------|---------|
| Core class | Stable | 390-line `omnilatex.cls`, 28 `.sty` modules across 9 subdirectories |
| Document types | Stable | 26 doctypes, 55+ aliases, 3 KOMA-Script base classes (scrartcl/scrbook/scrreprt) |
| Examples | Stable | 46 example templates, all compile on TeX Live 2025+ |
| Languages | Stable | 25 via polyglossia, 18 with full OmniLaTeX translations (47 keys each) |
| Institutions | Stable | 16 pluggable configs (ETH, MIT, Stanford, TUHH, TUM, Cambridge, etc.) |
| Formal verification | Stable | 198 Lean 4 theorems across 16 modules, 0 `sorry`, all compile |
| Test suite | Stable | 442 fast tests (48 skipped, 1 xfailed) |
| CI/CD | Stable | 10 GitHub Actions + GitLab/Gitea/Forgejo/Woodpecker configs, 442 tests (structural, property, integration, institution) |
| Pre-commit hooks | Stable | 25 hooks: trailing whitespace, black, isort, flake8, markdownlint, pytest gate, Lean gate |
| Reproducible builds | Stable | SOURCE_DATE_EPOCH, byte-for-byte deterministic PDFs |
| Docker | Stable | Multi-arch (amd64+arm64) Docker image with auto digest sync |
| CTAN | Ready | Auto-upload script with 5-phase validation |
| VS Code extension | Enhanced | Build-on-save, 26 doctype snippets, log diagnostics |
| Reference manual | Stable | 238 pages, 59 chapters, 12.4k lines |
| Beamer support | New | omnilatex-beamer.sty with OmniLaTeX colors/fonts for presentations |
| Code coverage CI | New | pytest-cov in CI with 60% threshold enforcement |

### Known Issues (Post-Audit)

| ID | Severity | Description | Effort |
|----|----------|-------------|--------|
| KI-001 | Medium | `DocumentSettings.lean` proof model does not match actual `DOCTYPE_TO_CLASS` mapping in `constants.py` (thesis/dictionary mapped to `report` in proof but `scrbook` in code) | RESOLVED in v1.18.0 |
| KI-002 | Medium | `I18nCompleteness.lean` only covers 18 primary languages; secondary languages with polyglossia registration but no translations are unverified | RESOLVED in v1.18.0 |
| KI-003 | Low | `visual_regression.py` SSIM script never runs in CI; `tests/references/` is empty | RESOLVED in v1.25.0 -- 46 reference PDFs generated, visual regression CI active |
| KI-004 | Low | `hypothesis` not declared in `tests/pyproject.toml` dependencies; property tests silently skip without it | RESOLVED in v1.18.0 |
| KI-005 | Low | Stale Docker digests in Forgejo/Woodpecker/GitLab/Gitea CI configs not auto-synced | AUDITED in v1.21.0 -- all consistent, sync automation recommended |
| KI-006 | Low | No `pytest-cov` or coverage measurement; branch coverage unknown | RESOLVED in v1.19.0 |
| KI-007 | Low | CHANGELOG v1.15.0 and v1.16.0 contain near-duplicate content; v1.12.0/v1.13.0 share duplicate entries | RESOLVED in v1.18.0 |
| KI-008 | Low | `pre-commit-latex-hooks` and `language-formatters-pre-commit-hooks` have Python version compatibility issues in some environments | RESOLVED in v1.21.0 |
| KI-009 | Info | `pretty-format-yaml` hook fails on Python 3.14 (missing `pkg_resources`) | RESOLVED in v1.21.0 |
| KI-010 | Info | No root-level `Makefile`; only `tests/Makefile` and `tests/module_tests/Makefile` | RESOLVED in v1.18.0 |

---

## Phase 1: Short-Term (v1.18.0) -- Quality Hardening [COMPLETED]

**Target:** 2-3 weeks | **Priority:** High | **Completed:** 2026-05-10

### 1.1 Fix Lean Proof-Code Consistency (KI-001) -- DONE

The `DocumentSettings.lean` module proves properties about a doctype-to-class mapping that diverges from the actual `DOCTYPE_TO_CLASS` dictionary in `tests/constants.py` and `omnilatex.cls`.

**Tasks:**

1. Extract canonical doctype-to-class mapping from `omnilatex.cls` (the single source of truth)
2. Generate `constants.py` DOCTYPE_TO_CLASS from the same source (or vice versa)
3. Update `DocumentSettings.lean` to match the canonical mapping exactly
4. Add a CI check that verifies Lean proof constants match Python test constants
5. Re-verify all 53 theorems still hold with corrected mapping

**Deliverables:**

- Single source of truth for doctype-class mapping
- Updated Lean proofs
- New consistency test in `test_properties.py`

### 1.2 Complete i18n Verification (KI-002) -- DONE

**Tasks:**

1. Enumerate all languages in `\setotherlanguages` in `omnilatex-i18n.sty`
2. For each language with `DeclareTranslation` entries, verify key count matches 47
3. For languages with polyglossia but no translations, document this as intentional
4. Update `I18nCompleteness.lean` to cover the full language set
5. Add test verifying no language has partial translation coverage (either 0 or 47 keys)

**Deliverables:**

- Complete language coverage matrix
- Updated Lean proof
- New parity test

### 1.3 CI Pipeline Hardening -- DONE

**Tasks:**

1. Add `test_properties.py` (structural + property) to `build.yml` CI pipeline (currently only `test_modules.py` and `test_ctan.py` run)
2. Add `test_visual_regression.py` to CI
3. Declare `hypothesis` in `tests/pyproject.toml` so property tests run in CI (KI-004)
4. Add `pytest-timeout` to `tests/pyproject.toml` dependencies (KI-004)
5. Pin `pre-commit` hook Python versions to `python3` instead of `python3.10`/`python3.14`

**Deliverables:**

- All non-Docker test files run in CI
- Property tests no longer silently skip
- Pre-commit hooks work across Python versions

### 1.4 Pre-commit Hook Reliability (KI-008, KI-009) -- DONE

**Tasks:**

1. Update `pre-commit-latex-hooks` to latest version (check for Python 3.13+ compat)
2. Replace `language-formatters-pre-commit-hooks` YAML formatter with a local `prettier` or `yq`-based hook
3. Test all hooks on Python 3.10, 3.12, 3.13, and 3.14
4. Document pre-commit hook requirements in CONTRIBUTING.md

### 1.5 CHANGELOG Cleanup (KI-007) -- DONE

**Tasks:**

1. Deduplicate v1.12.0/v1.13.0 shared entries (Persian RTL, Performance docs, Patent example)
2. Investigate and resolve v1.15.0/v1.16.0 near-duplicate content
3. Add proper version separation with clear feature ownership per version

---

## Phase 2: Medium-Term (v1.19.0) -- Testing Depth [COMPLETED]

**Target:** 3-4 weeks | **Priority:** Medium | **Completed:** 2026-05-11

### 2.1 Visual Regression Infrastructure (KI-003) -- DONE

**Tasks:**

1. Generate reference PDFs for all 46 examples (one-time, in Docker for determinism)
2. Store reference PDFs in `tests/references/` (add to git, ~50MB)
3. Integrate `visual_regression.py` SSIM script into CI (threshold: 0.99)
4. Add `--regenerate-references` flag for intentional visual changes
5. Add GitHub Action that runs visual regression on PRs with PDF changes

**Deliverables:**

- 46 reference PDFs
- CI visual regression gate
- SSIM baseline report

### 2.2 Coverage Measurement (KI-006) -- DONE

**Tasks:**

1. Add `pytest-cov` to test dependencies
2. Run coverage on Python test suite (tests/*.py, build.py, scripts/*.py)
3. Target: >80% line coverage for Python code, >95% for critical paths
4. Add coverage badge to README
5. Add coverage threshold enforcement in CI

### 2.3 Root Makefile (KI-010) -- DONE

Create a root-level `Makefile` with standardized targets:

```makefile
.PHONY: test test-fast test-slow test-lean lint format clean build build-all

test:          ## Run fast tests (structural + property + CTAN)
test-fast:     ## Alias for test
test-slow:     ## Run all tests including LaTeX compilation
test-lean:     ## Verify Lean 4 proofs
lint:          ## Run black, isort, flake8, markdownlint
format:        ## Auto-format code (black + isort)
clean:         ## Remove build artifacts
build:         ## Build root document
build-all:     ## Build all examples
preflight:     ## Run all checks before release
```

### 2.4 Docker Digest Sync (KI-005) -- DONE

**Tasks:**

1. Extend `docker-digest-sync.yml` to also update Forgejo, Woodpecker, GitLab, Gitea configs
2. Read digest from `.env.docker` in all CI configs (not hardcoded)
3. Add validation that all CI configs reference the same digest

---

## Phase 3: Feature Expansion (v2.0.0) -- Breaking Changes

**Target:** 6-8 weeks | **Priority:** Strategic

### 3.1 Beamer/Presentation Overhaul (P20.1 from ROADMAP.md) -- DONE

**Tasks:**

1. Create `omnilatex-beamer.sty` using OmniLaTeX color/font system
2. Support all 6 color themes + dark/light toggle in presentations
3. Compatible with existing institution configs
4. Add 3 Beamer examples (minimal, academic, corporate)
5. Lean 4 proofs for Beamer-specific properties (slide count invariants, theme consistency)

### 3.2 Community Institutions (P20.2 from ROADMAP.md)

**Tasks:**

1. Create institution contribution guide (template + checklist)
2. Add 5+ community-contributed institutions
3. Institution validation test suite (compile check, ProvidesPackage check, metadata check)
4. Institution gallery page in docs

### 3.3 l3build Test Expansion -- DONE

47 l3build tests, all 26 doctypes covered.

**Tasks:**

1. Expand `.lvt` test coverage from 22 to 40+ modules (add doctype-specific tests)
2. Add regression tests for all 26 doctypes
3. Add cross-module interaction tests (e.g., math + code listings + floats)
4. Integrate l3build into CI pipeline

### 3.4 Additional Lean 4 Proofs -- DONE

198 theorems across 15 modules, exceeded 100 target.

**Tasks:**

1. Prove page geometry invariants for all 26 doctypes (currently only general)
2. Prove translation key completeness for secondary languages
3. Prove build mode strictness properties (dev < prod < ultra)
4. Prove cross-reference consistency (no dangling labels)
5. Target: 100+ theorems

---

## Phase 4: Ecosystem (v2.1.0 - v3.0.0) -- Growth

**Target:** Ongoing | **Priority:** Strategic

### 4.1 CTAN Submission and Maintenance (v2.1.0)

1. Submit to CTAN via automated upload script
2. Monitor CTAN review feedback
3. Maintain CTAN metadata on all future releases
4. Respond to CTAN user issues

### 4.2 Overleaf Template Gallery (v2.1.0)

1. Submit 10 curated templates to Overleaf gallery
2. Add Overleaf-specific documentation
3. Monitor Overleaf compatibility on each release

### 4.3 VS Code Extension Updates (v2.2.0)

1. Publish to VS Code marketplace
2. Add snippet library for all 26 doctypes
3. Add build-on-save integration
4. Add error parsing and diagnostics

### 4.4 Performance Optimization (v2.3.0)

1. Profile first-run compilation time (currently ~42s)
2. Optimize font loading (pre-cache OTF indices)
3. Reduce latexmk passes for simple documents
4. Add incremental build support (only rebuild changed examples)
5. Target: <15s for simple documents, <5min for full build-all

### 4.5 Nix Flake Improvements (v2.3.0)

1. Add `nix build` target for PDF output
2. Add `nix develop` with all tools (lean4, texlive, python)
3. Add `nix flake check` that runs full test suite
4. Multi-arch Nix support (aarch64-linux, x86_64-darwin)

### 4.6 API Stability and SemVer (v3.0.0) -- DONE

1. Define public API surface (class options, commands, environments)
2. Document deprecation policy
3. Add `\omnilatexdeprecate{cmd}{new-cmd}` mechanism
4. Semantic versioning enforcement in CI
5. Breaking change checklist for v3.0.0

---

## Technical Debt Register

| ID | Description | Priority | Version Target |
|----|-------------|----------|----------------|
| TD-001 | `test_properties.py` duplicates `DOCTYPE_ALIASES` from `constants.py` | Low | RESOLVED in v1.18.0 |
| TD-002 | Build artifacts (main.pdf, *.aux,*.log) committed to repo | Low | N/A (not tracked in git) |
| TD-003 | No integration test for `build.py` commands (scaffold, init, list) | Medium | v1.19.0 |
| TD-004 | No type hints in `build.py` (1331 lines) | Medium | RESOLVED in v1.20.0 |
| TD-005 | `docs/accessibility.md` duplicates `CONTRIBUTING.md` PDF accessibility section | Low | v1.19.0 |
| TD-006 | README.md document types table duplicates `docs/USER_GUIDE.md` | Low | AUDITED in v1.21.0 -- overlap documented, refactoring recommended |
| TD-007 | No `.editorconfig` for consistent formatting across editors | Low | RESOLVED in v1.18.0 |
| TD-008 | `CHANGELOG.md` exceeds 500 lines; should be split per-version | Low | v2.0.0 |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| TeX Live 2026 breaks font paths | Medium | High | Pin font versions in Docker; add regression test |
| Lean 4 breaking change (v5.0) | Low | High | Pin lean-toolchain; maintain compatibility layer |
| CTAN review requests changes | Medium | Medium | Pre-flight validation script already covers requirements |
| Docker Hub rate limiting | Low | Low | GHCR already primary; Docker Hub is fallback |
| Python 3.14 deprecates `pkg_resources` | High | Low | Already mitigated by pinning to `python3` in hooks |
| Contributor burnout (single maintainer) | Medium | High | Institution contribution guide; CI automation reduces manual work |

---

## Metrics Dashboard

### Current Metrics (v1.25.0)

| Metric | Value | Target |
|--------|-------|--------|
| Test cases (non-hypothesis) | 442 | >500 |
| Test cases (with hypothesis) | 442 | >600 |
| Lean 4 theorems | 198 | >100 |
| Lean 4 modules | 15 | 15 |
| Document types | 26 | 30+ |
| Examples | 46 | 50+ |
| Institutions | 16 | 25+ |
| Languages (polyglossia) | 25 | 30+ |
| Languages (full translations) | 18 | 25+ |
| CI platforms | 5 | 5 |
| Pre-commit hooks | 25 | 25+ |
| Module TOML contracts | 21 | 27 (all modules) |
| Manual chapters | 59 | 60+ |
| Code coverage (Python) | 60% | >80% |
| l3build tests | 47 | 47 |
| CHANGELOG files | 26 | 26 |
| Beamer examples | 3 | 3 |

### Success Criteria for v2.0.0

- All Lean proofs match actual code behavior
- All non-Docker tests run in CI (< 5 min total)
- Visual regression gate active
- Code coverage > 80%
- 0 open critical/high issues
- CTAN submission accepted
- Beamer support shipped
