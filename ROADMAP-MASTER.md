# OmniLaTeX Master Roadmap

**Version:** v2.0.0 | **Date:** 2026-05-20 | **License:** Apache 2.0

---

## 1. Current State (Post-Audit v2.0.0)

| Metric | Value |
|--------|-------|
| Document types | 26 (55+ aliases), 3 KOMA-Script base classes |
| Institution configs | 21 (ETH, MIT, Stanford, TUHH, TUM, Cambridge, Oxford, etc.) |
| Languages | 25 via polyglossia (CJK, RTL, Cyrillic) |
| `.sty` modules | 28 across 9 subdirectories |
| Examples | 47 templates (all compile on TeX Live 2025+) |
| Tests | 815 pytest (750 fast), 47 l3build, 198 Lean 4 theorems (0 sorry) |
| CI/CD | 12 GitHub Actions + GitLab/Gitea/Forgejo/Woodpecker |
| Docker | Multi-arch (amd64+arm64), digest-synced, GHCR-hosted |
| VS Code extension | Build-on-save, 26 doctype snippets, log diagnostics |
| Documentation | MkDocs Material (14 pages) + 3 HTML pages (gallery, picker, verify) |
| GitHub Pages | MkDocs docs + PDF gallery + template picker + verify tool |
| Formal verification | 16 Lean 4 proof modules, 198 theorems |
| Manual | 238 pages, 59 chapters |
| Reproducibility | SOURCE_DATE_EPOCH, byte-for-byte deterministic PDFs |

### Audit Findings Resolved (2026-05-20)

| Category | Resolved | Remaining |
|----------|----------|-----------|
| Code quality (HIGH) | 4/4 | 11 MEDIUM (performance), 34 LOW (style) |
| CI/CD (CRITICAL) | 3/3 | 9 HIGH (monitoring), 17 MEDIUM |
| Documentation | Stale metrics, xelatex error, invalid doctypes, MkDocs nav | Backward version refs in archived roadmaps |
| Security | VS Code extension exec() injection | 0 critical |
| Pre-commit | Already correct (750 tests + Lean proofs) | -- |

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
| Submit omnilatex to CTAN | 2h | Package listed on ctan.org | PENDING |
| Validate CTAN package passes `ctan-o-mat` | 1h | Zero validation errors | PENDING |
| Create CTAN announcement | 1h | Posted to ctan-ann mailing list | PENDING |
| Update TeX Live package manager entry | 1h | `tlmgr install omnilatex` works | PENDING |

### Phase 2: Performance and Scale (v2.2.0)

**Timeline:** 3-4 weeks | **Priority:** High

| Task | Effort | Acceptance Criteria | Status |
|------|--------|---------------------|--------|
| Cache `rglob()` results in `build.py` | 4h | Build-all time reduced by 15%+ | PENDING |
| Batch build cache I/O (load/save once per batch) | 4h | File I/O reduced from N to 2 per build | PENDING |
| Combine `_check_latex_package` subprocess calls | 2h | Preflight uses 1 subprocess instead of 8 | PENDING |
| Standardize SSIM implementation (sliding window) | 4h | Visual regression uses skimage.metrics.structural_similarity | PENDING |
| Fix `cmd_watch` stdout None guard | 1h | Inotifywait fallback handles Popen failures | PENDING |
| Add benchmark regression CI (20% threshold) | 2h | Performance-regression.yml runs on every main push | PENDING |

### Phase 3: Documentation and Onboarding (v2.3.0)

**Timeline:** 2-3 weeks | **Priority:** High

| Task | Effort | Acceptance Criteria | Status |
|------|--------|---------------------|--------|
| Write comprehensive user guide (MkDocs) | 8h | USER_GUIDE.md covers all 26 doctypes with examples | PENDING |
| Add search functionality to MkDocs | 1h | Search returns relevant results for all doc pages | PENDING |
| Add interactive template picker to MkDocs site | 4h | Users can select doctype + language + institution and download | PENDING |
| Create migration guide from article/thesis classes | 4h | Step-by-step guide for converting existing documents | PENDING |
| Add FAQ section | 2h | Covers top 20 common issues | PENDING |
| Validate all internal and external links | 2h | `mkdocs build` reports zero broken links | PENDING |

---

## 4. Medium-Term Development (v2.4.0 -- v2.6.0)

### v2.4.0: Ecosystem Integration

**Timeline:** 4-6 weeks | **Priority:** Medium

| Task | Effort | Acceptance Criteria |
|------|--------|---------------------|
| Overleaf template gallery submission | 4h | Listed on overleaf.com/templates |
| VS Code Marketplace publication | 4h | Extension available via `ext install omnilatex` |
| Add LuaLaTeX `-cnf-line` support | 8h | Users can set TeX parameters without `.latexmkrc` |
| Add Beamer class (native, not compatibility layer) | 16h | Beamer doctypes use dedicated Beamer commands |
| Create `omnilatex-thesis` meta-package | 4h | One-command thesis setup: `omnilatex init thesis` |
| Add `omnilatex diff` for version comparison | 8h | `build.py diff v1 v2` produces change-annotated PDF |

### v2.5.0: Advanced Features

**Timeline:** 6-8 weeks | **Priority:** Medium

| Task | Effort | Acceptance Criteria |
|------|--------|---------------------|
| Add collaborative editing support (live preview) | 16h | Changes compile and preview within 2 seconds |
| Create `omnilatex-biblio` CSL style pack | 8h | 15+ citation styles with visual previews |
| Add `omnilatex-todo` integration (todo-tracker.lua) | 8h | `\todo{}` items collected in appendix automatically |
| Add `omnilatex-review` margin notes | 8h | `\review{comment}` adds margin annotations |
| Create institution contribution wizard | 4h | `build.py scaffold-institution` creates complete config |
| Add cross-referencing integrity checks | 8h | `build.py check` validates all `\ref`, `\cite`, `\label` |

### v2.6.0: Internationalization Expansion

**Timeline:** 4-6 weeks | **Priority:** Medium

| Task | Effort | Acceptance Criteria |
|------|--------|---------------------|
| Add Thai, Hindi, Bengali script support | 8h | New polyglossia languages compile correctly |
| Add Georgian, Armenian script support | 8h | Correct font shaping for complex scripts |
| Create multi-language test matrix (all 25 languages x 26 doctypes) | 16h | integration-matrix.yml covers all combinations |
| Add bidirectional text testing (Arabic, Hebrew, Persian) | 8h | RTL documents render correctly in all doctypes |
| Create localization style guide | 4h | Document translation conventions for contributors |

---

## 5. Long-Term Vision (v3.0.0+)

### v3.0.0: Next Generation

| Task | Description |
|------|-------------|
| Template DSL | Declarative template definition language for custom doctypes |
| Visual template designer | Browser-based GUI for creating institution configs |
| Plugin system | Third-party `.sty` packages via `omnilatex-plugin` namespace |
| Cloud compilation API | REST API for PDF generation without local TeX installation |
| Continuous proof verification | Lean 4 proofs run on every PR, blocking merge on failure |
| Multi-output formats | HTML (via LaTeXML), EPUB, DOCX export from same source |
| AI-assisted writing | Optional LSP integration for LaTeX writing assistance |

### Infrastructure

| Task | Description |
|------|-------------|
| Dedicated documentation site | Move from GitHub Pages to custom domain with Cloudflare CDN |
| Forgejo/Cloudflare Pages mirror | Automatic deployment from Forgejo via Cloudflare Pages |
| Performance monitoring dashboard | Track build times, test durations, and resource usage trends |
| Automated dependency updates | Dependabot + Renovate for all ecosystems (TeX, Python, npm, Lean) |
| SBOM compliance tracking | Continuous SPDX generation and vulnerability monitoring |

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

| Item | Effort | Priority | Target |
|------|--------|----------|--------|
| Consolidate 7 roadmap files into 2 | 4h | Medium | v2.1.0 |
| Fix stale metrics in archived roadmaps | 2h | Low | v2.1.0 |
| Standardize SSIM implementation | 4h | Medium | v2.2.0 |
| Cache `rglob()` in build.py | 4h | High | v2.2.0 |
| Batch build cache I/O | 4h | High | v2.2.0 |
| Remove dead code in build.py | 2h | Low | v2.2.0 |
| Add type hints to all public APIs | 8h | Low | v2.3.0 |
| Generate API docs from module contracts | 8h | Medium | v2.3.0 |
| Consolidate CTAN workflows (3 -> 1) | 4h | Medium | v2.2.0 |

---

## 8. Success Metrics

| Metric | v2.0.0 (Current) | v2.3.0 Target | v3.0.0 Target |
|--------|-------------------|---------------|---------------|
| Tests | 815 | 1000+ | 1500+ |
| Test coverage (critical paths) | >95% | >97% | >99% |
| Lean 4 theorems | 198 | 250+ | 400+ |
| Build time (all examples) | ~8 min | <6 min | <4 min |
| CI/CD success rate | ~90% | >98% | >99.5% |
| Documentation pages | 14 | 30+ | 60+ |
| CTAN package installs | N/A | Track via CTAN stats | Top 100 LaTeX packages |
| GitHub stars | Track | 100+ | 500+ |
| Contributors | Track | 5+ | 20+ |
| Supported languages | 25 | 30+ | 40+ |
| Institution configs | 21 | 30+ | 50+ |
