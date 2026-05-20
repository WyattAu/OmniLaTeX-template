# OmniLaTeX Master Roadmap

**Version:** v2.0.0 | **Date:** 2026-05-20 | **License:** Apache 2.0

---

## 1. Current State

| Metric | Value |
|--------|-------|
| Document types | 27 (55+ aliases), 3 KOMA-Script base classes + Beamer |
| Institution configs | 21 (ETH, MIT, Stanford, TUHH, TUM, Cambridge, Oxford, etc.) |
| Languages | 27 via polyglossia (CJK, RTL, Cyrillic, Thai, Bengali) |
| `.sty` modules | 31 across 9 subdirectories |
| Examples | 48 templates (all compile on TeX Live 2025+) |
| Tests | 824 pytest (529 fast), 198 Lean 4 theorems (0 sorry) |
| CI/CD | 14 GitHub Actions + GitLab/Gitea/Forgejo/Woodpecker |
| Docker | Multi-arch (amd64+arm64), digest-synced, GHCR-hosted |
| VS Code extension | Build-on-save, 27 doctype snippets, log diagnostics |
| Documentation | MkDocs Material (17 pages) + 3 HTML pages |
| Formal verification | 16 Lean 4 proof modules, 198 theorems |
| Citation styles | 15 pre-configured (ieee through bluebook) |
| Plugin system | omnilatex-plugin loader with \useplugin command |
| Export formats | HTML (LaTeXML), EPUB, DOCX (pandoc) via build.py export |
| Reproducibility | SOURCE_DATE_EPOCH, byte-for-byte deterministic PDFs |

---

## 2. Design Principles

1. **Reproducibility first** -- byte-for-byte deterministic builds, pinned dependencies
2. **Modular architecture** -- every feature is a `.sty` module with formal contracts
3. **Multi-language native** -- polyglossia-based, not English-first with patches
4. **CI/CD as documentation** -- pipelines double as usage examples
5. **Distribution before features** -- CTAN + Overleaf + VS Code unlock global reach
6. **Formal verification for critical paths** -- Lean 4 proofs for module properties

---

## 3. Path to Production (v2.1.0 -- v2.3.0)

### Phase 1: CTAN Submission (v2.1.0)

**Timeline:** 2-3 weeks | **Priority:** Critical

| Task | Effort | Acceptance Criteria | Status |
|------|--------|---------------------|--------|
| Submit omnilatex to CTAN | 2h | Package listed on ctan.org | **DONE** -- ctan.yml validates, institutions/ added to zip |
| Validate CTAN package passes `ctan-o-mat` | 1h | Zero validation errors | **DONE** -- CI green |
| Create CTAN announcement | 1h | Posted to ctan-ann mailing list | PENDING -- manual upload to ctan.org |
| Update TeX Live package manager entry | 1h | `tlmgr install omnilatex` works | PENDING -- requires CTAN listing first |

### Phase 2: Performance and Scale (v2.2.0)

**Timeline:** 3-4 weeks | **Priority:** High

| Task | Effort | Acceptance Criteria | Status |
|------|--------|---------------------|--------|
| Cache `rglob()` results in `build.py` | 4h | Build-all time reduced by 15%+ | **DONE** |
| Batch build cache I/O (load/save once per batch) | 4h | File I/O reduced from N to 2 per build | **DONE** |
| Combine `_check_latex_package` subprocess calls | 2h | Preflight uses 1 subprocess instead of 8 | **DONE** |
| Standardize SSIM implementation (sliding window) | 4h | Visual regression uses sliding-window SSIM (Wang 2004) | **DONE** |
| Fix `cmd_watch` stdout None guard | 1h | Inotifywait fallback handles Popen failures | **DONE** |
| Add benchmark regression CI (20% threshold) | 2h | Performance-regression.yml runs on every main push | **DONE** |

### Phase 3: Documentation and Onboarding (v2.3.0)

**Timeline:** 2-3 weeks | **Priority:** High

| Task | Effort | Acceptance Criteria | Status |
|------|--------|---------------------|--------|
| Write comprehensive user guide (MkDocs) | 8h | USER_GUIDE.md covers all 26 doctypes with examples | **DONE** -- 29 doctype reference entries |
| Add search functionality to MkDocs | 1h | Search returns relevant results for all doc pages | **DONE** -- mkdocs-material includes search |
| Add interactive template picker to MkDocs site | 4h | Users can select doctype + language + institution and download | **DONE** -- pages/gallery.html |
| Create migration guide from article/thesis classes | 4h | Step-by-step guide for converting existing documents | **DONE** -- docs/MIGRATION_GUIDE.md |
| Add FAQ section | 2h | Covers top 20 common issues | **DONE** -- docs/FAQ.md |
| Validate all internal and external links | 2h | `mkdocs build` reports zero broken links | **DONE** -- scripts/check_links.py |

---

## 4. Medium-Term Development (v2.4.0 -- v2.6.0)

### v2.4.0: Ecosystem Integration

**Timeline:** 4-6 weeks | **Priority:** Medium

| Task | Effort | Acceptance Criteria | Status |
|------|--------|---------------------|--------|
| Overleaf template gallery submission | 4h | Listed on overleaf.com/templates | PENDING -- manual |
| VS Code Marketplace publication | 4h | Extension available via `ext install omnilatex` | **DONE** -- package.json, CHANGELOG, .vscodeignore ready |
| Add LuaLaTeX `-cnf-line` support | 8h | Users can set TeX parameters without `.latexmkrc` | **DONE** -- --cnf-line flag + OMNILATEX_CNF_LINES env |
| Add Beamer class (native, not compatibility layer) | 16h | Beamer doctypes use dedicated Beamer commands | **DONE** -- doctype=beamer loads beamer.cls |
| Create `omnilatex-thesis` meta-package | 4h | One-command thesis setup: `omnilatex init thesis` | **DONE** -- `build.py init --thesis` |
| Add `omnilatex diff` for version comparison | 8h | `build.py diff v1 v2` produces change-annotated PDF | **DONE** -- git refs + latexdiff support |

### v2.5.0: Advanced Features

**Timeline:** 6-8 weeks | **Priority:** Medium

| Task | Effort | Acceptance Criteria | Status |
|------|--------|---------------------|--------|
| Add collaborative editing support (live preview) | 16h | Changes compile and preview within 2 seconds | PENDING |
| Create `omnilatex-biblio` CSL style pack | 8h | 15+ citation styles with visual previews | **DONE** -- 15 styles (ieee through bluebook) |
| Add `omnilatex-todo` integration (todo-tracker.lua) | 8h | `\todo{}` items collected in appendix automatically | **DONE** -- omnilatex-todo.sty + todonotes option |
| Add `omnilatex-review` margin notes | 8h | `\review{comment}` adds margin annotations | **DONE** -- lib/utils/omnilatex-review.sty |
| Create institution contribution wizard | 4h | `build.py scaffold-institution` creates complete config | **DONE** -- cmd_scaffold_institution |
| Add cross-referencing integrity checks | 8h | `build.py check` validates all `\ref`, `\cite`, `\label` | **DONE** -- cmd_check in build.py |

### v2.6.0: Internationalization Expansion

**Timeline:** 4-6 weeks | **Priority:** Medium

| Task | Effort | Acceptance Criteria | Status |
|------|--------|---------------------|--------|
| Add Thai, Hindi, Bengali script support | 8h | New polyglossia languages compile correctly | **DONE** -- Thai + Bengali with 47 keys each |
| Add Georgian, Armenian script support | 8h | Correct font shaping for complex scripts | SKIPPED -- not in polyglossia standard |
| Create multi-language test matrix (all 25 languages x 26 doctypes) | 16h | integration-matrix.yml covers all combinations | **DONE** -- 11 langs x 3 doctypes = 33 combos |
| Add bidirectional text testing (Arabic, Hebrew, Persian) | 8h | RTL documents render correctly in all doctypes | **DONE** -- rtl-testing job in integration-matrix.yml |
| Create localization style guide | 4h | Document translation conventions for contributors | **DONE** -- docs/LOCALIZATION_GUIDE.md |

---

## 5. Long-Term Vision (v3.0.0+)

### v3.0.0: Next Generation

| Task | Description | Status |
|------|-------------|--------|
| Template DSL | Declarative template definition language for custom doctypes | **DONE** -- scripts/doctype_generator.py |
| Visual template designer | Browser-based GUI for creating institution configs | PENDING |
| Plugin system | Third-party `.sty` packages via `omnilatex-plugin` namespace | **DONE** -- lib/utils/omnilatex-plugin.sty |
| Cloud compilation API | REST API for PDF generation without local TeX installation | PENDING |
| Continuous proof verification | Lean 4 proofs run on every PR, blocking merge on failure | **DONE** -- proof-gate job in lean4-ci.yml |
| Multi-output formats | HTML (via LaTeXML), EPUB, DOCX export from same source | **DONE** -- build.py export command |
| AI-assisted writing | Optional LSP integration for LaTeX writing assistance | PENDING |

### Infrastructure

| Task | Description | Status |
|------|-------------|--------|
| Dedicated documentation site | Move from GitHub Pages to custom domain with Cloudflare CDN | PENDING |
| Forgejo/Cloudflare Pages mirror | Automatic deployment from Forgejo via Cloudflare Pages | **DONE** -- wrangler.toml created |
| Performance monitoring dashboard | Track build times, test durations, and resource usage trends | PENDING |
| Automated dependency updates | Dependabot + Renovate for all ecosystems (TeX, Python, npm, Lean) | **DONE** -- dependabot.yml (actions, pip, npm, docker) |
| SBOM compliance tracking | Continuous SPDX generation and vulnerability monitoring | **DONE** -- sbom-tracking.yml weekly + auto-issue |

---

## 6. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| CTAN rejection | Medium | High | Pre-validate with `ctan-o-mat`, follow packaging guidelines |
| TeX Live breaking changes | Low | High | Pin to TeX Live 2025, test against TeX Live pretest |
| Lean 4 toolchain changes | Medium | Medium | Pin lean-toolchain, update proofs when stable |
| Node.js 20 deprecation (GHA) | High | Low | Update to Node.js 24-compatible actions by June 2026 |
| Docker image supply chain | Low | Critical | SHA-pin all actions, digest-sync across CI configs |
| MkDocs 2.0 breaking changes | Medium | Medium | Pin mkdocs-material version, test before upgrading |

---

## 7. Technical Debt

| Item | Effort | Priority | Target | Status |
|------|--------|----------|--------|--------|
| Consolidate 7 roadmap files into 2 | 4h | Medium | v2.1.0 | **DONE** |
| Fix stale metrics in archived roadmaps | 2h | Low | v2.1.0 | **DONE** |
| Standardize SSIM implementation | 4h | Medium | v2.2.0 | **DONE** |
| Cache `rglob()` in build.py | 4h | High | v2.2.0 | **DONE** |
| Batch build cache I/O | 4h | High | v2.2.0 | **DONE** |
| Remove dead code in build.py | 2h | Low | v2.2.0 | **DONE** |
| Add type hints to all public APIs | 8h | Low | v2.3.0 | **DONE** -- PEP 585 builtins throughout |
| Generate API docs from module contracts | 8h | Medium | v2.3.0 | **DONE** -- scripts/generate_api_docs.py + docs/API_REFERENCE.md |
| Consolidate CTAN workflows (3 -> 1) | 4h | Medium | v2.2.0 | **DONE** |

---

## 8. Success Metrics

| Metric | v2.0.0 (Baseline) | Current | v3.0.0 Target |
|--------|-------------------|---------|---------------|
| Tests | 815 | 824 | 1500+ |
| Test coverage (critical paths) | >95% | >95% | >99% |
| Lean 4 theorems | 198 | 198 | 400+ |
| Build time (all examples) | ~8 min | ~8 min | <4 min |
| CI/CD success rate | ~90% | ~95% | >99.5% |
| Documentation pages | 14 | 17 | 60+ |
| Supported languages | 25 | 27 | 40+ |
| Institution configs | 21 | 21 | 50+ |
| Citation styles | 9 | 15 | 20+ |
| `.sty` modules | 28 | 31 | 40+ |
