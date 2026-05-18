# OmniLaTeX Roadmap v2

**Current version:** v2.0.0 | **Date:** 2026-05-18 | **License:** Apache 2.0

---

## 1. Current State Summary (v2.0.0)

| Dimension | Value |
|-----------|-------|
| Core class | `omnilatex.cls` (390 lines), 28 `.sty` modules, 9 subdirectories |
| Document types | 26 doctypes, 55+ aliases, 3 KOMA-Script base classes |
| Examples | 47 templates (all compile on TeX Live 2025+) |
| Institutions | 21 configs (ETH, MIT, Stanford, TUHH, TUM, Cambridge, etc.) |
| Languages | 18 full OmniLaTeX translations (47 keys each) + 25 via polyglossia |
| Formal verification | 196 Lean 4 theorems, 16 modules, 0 `sorry` |
| Tests | 473 pytest + 47 l3build + Lean 4 proofs |
| CI/CD | 10 GitHub Actions + GitLab/Gitea/Forgejo/Woodpecker |
| Docker | Multi-arch (amd64+arm64), digest-synced across 8 CI configs |
| VS Code extension | Build-on-save, 26 doctype snippets, log diagnostics |
| Manual | 238 pages, 59 chapters, 12.4k lines |
| GitHub Pages | 3 raw HTML pages (index, gallery, verify) -- docs/ NOT served |
| CTAN | Upload script ready, submission pending review |
| Reproducibility | SOURCE_DATE_EPOCH, byte-for-byte deterministic PDFs |

### Known Issues Requiring Action

| ID | Severity | Description | Status |
|----|----------|-------------|--------|
| KI-011 | Medium | `docs/` (16 markdown files) not served on GitHub Pages; only raw HTML pages deployed | OPEN (v3.0) |
| KI-012 | Medium | No formal docs site generator (MkDocs/Docusaurus) | OPEN (v3.0) |
| KI-013 | Low | CSS duplicated across `pages/index.html`, `gallery.html`, `verify.html` | FIXED (v2.1.0) |
| KI-014 | Low | README examples table missing `beamer-defense` entry | FIXED (v2.1.0) |
| KI-015 | Low | Language lists inconsistent between README and USER_GUIDE | FIXED (v2.1.0) |
| KI-016 | Low | No `CODEOWNERS` file | FIXED (v2.1.0) |
| KI-017 | Medium | `visual-regression.yml` regenerate job pushes directly to default branch | FIXED (v2.1.0) |
| KI-018 | Low | flake8 E501 noise in `build.py` (100+ lines exceed 79 chars) | FIXED (v2.1.0) |
| KI-019 | Low | Integration matrix only tests EN/DE/FR/ZH | OPEN (v3.0) |
| KI-020 | Low | CHANGELOG entries v1.18.0 and earlier have stale counts | FIXED (v2.1.0) |
| KI-021 | Low | GitHub Actions `actions/cache` was tag-pinned | FIXED (v2.1.0) |
| KI-022 | Medium | No `actions/dependency-review-action` on PRs | FIXED (v2.1.0) |

---

## 2. v2.1.0 -- Polish and Hardening

**Timeline:** 2-4 weeks | **Priority:** Critical/High

### 2.1 Security and CI Hardening

| Task | Effort | Acceptance | Status |
|------|--------|------------|--------|
| Pin all GitHub Actions to SHA digests | 2h | `rg "uses:" .github/workflows/` shows no tag refs | DONE |
| Add `actions/dependency-review-action` to PR workflow | 1h | PRs blocked on new vulnerable deps | DONE |
| Fix `visual-regression.yml` regenerate pushing to default branch | 1h | Regenerate opens PR instead of direct push | DONE |
| Add SBOM upload to GitHub Security tab | 2h | SBOM artifact visible in Security tab | DEFERRED (low priority) |
| Add timeout-minutes to Forgejo/Woodpecker/GitLab jobs | 30m | No job runs unbounded | DONE |
| Use full action URLs in Gitea workflow | 30m | Gitea CI runs without URL resolution errors | DONE |

### 2.2 Documentation Consistency

| Task | Effort | Acceptance | Status |
|------|--------|------------|--------|
| Add `beamer-defense` to README examples table | 15m | Table includes all 47 examples | DONE |
| Synchronize language lists across README and USER_GUIDE | 30m | Identical lists in both files | DONE |
| Fix CHANGELOG stale counts for v1.18.0 and earlier | 1h | All version entries reflect actual metrics at time of release | DONE |
| Add `CODEOWNERS` file | 30m | File exists with sensible ownership rules | DONE |
| Fix language count to match actual i18n.sty translations (18, not 20) | 30m | README/USER_GUIDE/CTAN_README consistent | DONE |
| Fix CTAN_README.txt missing languages and ctan-upload.sh stale count | 15m | All 18 languages listed, 21 institutions | DONE |

### 2.3 Code Quality

| Task | Effort | Acceptance | Status |
|------|--------|------------|--------|
| Refactor `build.py` to eliminate E501 violations (use line continuations or extract functions) | 4h | `flake8 build.py` produces zero E501 warnings | DONE |
| Extract shared CSS into `pages/style.css`, link from all 3 HTML pages | 2h | Zero duplicated CSS blocks across HTML files | DONE |

### 2.4 CTAN Submission

| Task | Effort | Acceptance |
|------|--------|------------|
| Final metadata review (CTAN_README.txt, file layout) | 2h | `scripts/ctan-upload.sh --dry-run` passes |
| Submit to CTAN via web form | 1h | Submission confirmed in CTAN queue |
| Address reviewer feedback | Variable | All feedback resolved |
| Verify `tlmgr install omnilatex` on clean TL2025+ | 2h | Install succeeds, examples compile |

### 2.5 Deliverables

- All KI-011 through KI-022 resolved
- CTAN submission accepted
- CI security posture hardened (SHA-pinned actions, dependency review, SBOM)
- Zero flake8 E501 violations in `build.py`
- CSS deduplication complete

---

## 3. v2.2.0 -- Ecosystem Expansion

**Timeline:** 4-8 weeks | **Priority:** High/Medium
**Depends on:** v2.1.0 (CTAN live)

### 3.1 Distribution Channels

| Task | Effort | Acceptance |
|------|--------|------------|
| Submit 10 curated templates to Overleaf gallery | 2h | Submission confirmed |
| Publish VS Code extension to marketplace | 2h | Extension installable from marketplace |
| Update README install section with CTAN path | 1h | CTAN, Overleaf, Nix, Docker, VS Code all documented |
| Verify Nix package: `nix build .#omnilatex` | 2h | Build succeeds, output valid |

### 3.2 Community Contributions

| Task | Effort | Acceptance | Status |
|------|--------|------------|--------|
| Create institution contribution guide (template + checklist) | 4h | `CONTRIBUTING.md` contains institution section | DONE |
| Add 5+ community institutions (Aalto, Chalmers, KIT, NTNU, UofT) | 8h | Each has CI validation (compile, ProvidesPackage, metadata) | DONE (already exist) |
| Institution gallery page in docs | 4h | All 26+ institutions listed with logos/colors | OPEN (v3.0) |

### 3.3 Per-Doctype Citation Defaults

| Task | Effort | Acceptance | Status |
|------|--------|------------|--------|
| IEEE default for article/journal/technical-report | 2h | Document loads IEEE without explicit citation option | DONE (already implemented) |
| APA default for cv/cover-letter/exam/presentation/etc. | 2h | Document loads APA by default | DONE (already implemented) |
| Chicago default for book/dictionary | 1h | Book/dictionary doctypes load Chicago by default | DONE (already implemented) |

### 3.4 Accessibility

| Task | Effort | Acceptance |
|------|--------|------------|
| NVDA screen reader validation for PDF output | 4h | NVDA reads all content without errors |
| PDF/UA-1 compliance verification | 8h | PDF passes automated PDF/UA-1 checks |

### 3.5 Performance Regression CI

| Task | Effort | Acceptance |
|------|--------|------------|
| Benchmark compilation time per example | 4h | Baseline timings recorded |
| CI gate: fail if compile time regresses >10% | 4h | PR blocked on performance regression |

### 3.6 Docker Improvements

| Task | Effort | Acceptance | Status |
|------|--------|------------|--------|
| Bundle Monaspace Neon and Atkinson Hyperlegible Next fonts | 4h | Fonts available in Docker container | OPEN |
| Add `.env.docker` validation to all workflows | 1h | Workflows fail fast on invalid digest | DONE (already implemented) |

### 3.7 Deliverables

- Overleaf gallery submission confirmed
- VS Code extension live in marketplace
- 21 institution configs (all present, CI-validated)
- Per-doctype citation defaults functional (all 26 doctypes)
- Institution contribution guide in CONTRIBUTING.md
- Performance regression gate active in CI

---

## 4. v3.0.0 -- Scale and Performance

**Timeline:** 2-4 months | **Priority:** Strategic
**Depends on:** v2.2.0

### 4.1 Full Beamer Document Class

| Task | Effort | Acceptance |
|------|--------|------------|
| Design standalone `omnilatex-beamer` class API | 4h | API doc published |
| Implement class wrapping KOMA-Script beamer patterns | 8h | `\documentclass[doctype=beamer-academic]{omnilatex}` compiles |
| Add Beamer options (aspect ratio, navigation, overlays) | 4h | All options documented and tested |
| Create thesis-defense and poster-talk Beamer examples | 4h | Examples compile, visual regression passes |
| Extend Lean 4 proofs for Beamer class properties | 4h | 50+ Beamer theorems |
| Update BREAKING_CHANGES.md | 2h | All breaking changes documented |

### 4.2 Manual Completion

| Task | Effort | Acceptance |
|------|--------|------------|
| Expand 12 thin chapters to >150 lines each | 16h | All 59+ chapters meet minimum |
| Add index, list of examples, list of listings | 4h | Back matter complete |
| TikZ architecture diagrams | 4h | Module dependency diagram in manual |
| Cross-reference validation between all chapters | 2h | Zero unresolved references |

### 4.3 Documentation Site

| Task | Effort | Acceptance |
|------|--------|------------|
| Adopt MkDocs or Docusaurus for docs/ | 8h | `mkdocs serve` renders all 16+ markdown files |
| Configure GitHub Pages deployment from docs site | 2h | `docs.omnilatex.dev` serves generated site |
| Redirect old raw HTML pages to new docs site | 1h | No broken links |

### 4.4 Web Preview (LaTeX via WASM)

| Task | Effort | Acceptance |
|------|--------|------------|
| Integrate texlive.js for in-browser compilation | 40h | Simple documents compile in browser |
| Deploy preview at omnilatex.dev | 8h | Live site accessible |
| Limit scope to simple doctypes (article, letter, memo) | -- | MVP only; complex doctypes remain local |

### 4.5 Build Tool Modernization

| Task | Effort | Acceptance |
|------|--------|------------|
| Profile first-run compilation time (baseline: ~42s) | 4h | Baseline recorded |
| Optimize font loading (pre-cache OTF indices) | 8h | First-run < 25s |
| Reduce latexmk passes for simple documents | 4h | Simple docs compile in 1-2 passes |
| Incremental build support (only rebuild changed examples) | 8h | `build.py --changed` builds only modified examples |

### 4.6 Test Suite Expansion

| Task | Effort | Acceptance |
|------|--------|------------|
| Expand integration matrix to JA/KO/RU/AR/HE | 4h | 9+ languages tested |
| Increase visual regression to 20+ examples | 4h | Coverage includes all major doctypes |
| Expand property-based tests to 40+ | 8h | Hypothesis coverage broader |
| Target 700+ fast tests | Ongoing | `pytest tests/ -m "not slow"` reports 700+ |

### 4.7 Deliverables

- Standalone Beamer document class shipped
- Manual at 300+ pages, all chapters substantive
- Docs site live on GitHub Pages
- Web preview MVP deployed
- Build time reduced by >40%
- 700+ fast tests, 300+ Lean theorems

---

## 5. Production Readiness Checklist

| Criterion | Status | Gate |
|-----------|--------|------|
| All pytest tests pass (0 failures, 0 xfailed) | PASS | CI green |
| All Lean 4 proofs compile (0 `sorry`) | PASS | `lake build` |
| All 47 l3build tests pass | PASS | `l3build run` |
| Visual regression gate active | PASS | SSIM > 0.99 |
| Code coverage >= 80% (Python) | PASS | pytest-cov CI |
| CTAN submission accepted | PENDING | v2.1.0 |
| All GitHub Actions pinned to SHA | DONE | v2.1.0 |
| Dependency review on PRs | DONE | v2.1.0 |
| SBOM uploaded | DEFERRED | v2.2.0 |
| No critical/high known issues open | DONE | v2.1.0 |
| CHANGELOG accurate (no stale counts) | DONE | v2.1.0 |
| README and docs consistent | DONE | v2.1.0 |
| Docker multi-arch build passes | PASS | CI green |
| Reproducible builds verified | PASS | SOURCE_DATE_EPOCH |
| Overleaf gallery submitted | PENDING | v2.2.0 |
| VS Code extension in marketplace | PENDING | v2.2.0 |
| Manual compiles without warnings | PASS | `latexmk` clean |
| Pre-commit hooks pass on clean repo | PASS | `pre-commit run --all` |
| Institution contribution guide | DONE | v2.1.0 |
| Per-doctype citation defaults | DONE | Already implemented |
| `.env.docker` validation | DONE | Already implemented |
| CSS deduplication (style.css) | DONE | v2.1.0 |
| CODEOWNERS file | DONE | v2.1.0 |
| Language list accuracy (18 full translations) | DONE | v2.1.0 |
| build.py E501 violations eliminated | DONE | v2.1.0 |

---

## 6. Future Considerations (v4.0+)

| Item | Description | Feasibility | Dependency |
|------|-------------|-------------|------------|
| Rust TUI build tool | Replace `build.py` (2094 lines) with native binary; `clap` CLI, `rayon` parallelism | High | None |
| Template marketplace | GitHub Pages + Jekyll; user submissions via PR workflow | High | Docs site (v3.0) |
| Multi-language docs | Translate USER_GUIDE to ZH, DE, FR | Medium | Native speakers for QA |
| Overleaf premium listing | Enhanced templates with Overleaf-specific features | Medium | Overleaf gallery (v2.2) |
| Full manual (945 pages) | Comprehensive reference covering every module, option, and edge case | High | v3.0 manual foundation |
| LaTeX WASM full compilation | All 26 doctypes compilable in-browser | Low | WASM MVP (v3.0) |
| Emacs/Vim/Neovim plugins | LSP integration, snippet expansion, build commands | Medium | API stability |
| Community translation portal | Crowdin or Weblate for i18n contributions | Medium | v3.0+ stability |
| TeX Live 2026+ pre-release testing | CI against TL pre-release to catch breakage early | High | TL pre-release access |

---

## 7. Risk Register

| ID | Risk | Probability | Impact | Mitigation | Owner |
|----|------|-------------|--------|------------|-------|
| R-01 | CTAN rejection or major revision request | Low | High | Pre-run validation script; strict CTAN guideline adherence | v2.1.0 |
| R-02 | TeX Live 2026 breaks font paths or package APIs | Medium | High | Pin minimum TL version; test on TL pre-release; Docker pin | v3.0.0 |
| R-03 | Lean 4 breaking change (toolchain v5.0+) | Low | Medium | Pin `lean-toolchain`; `lake-manifest.json` in VCS | Ongoing |
| R-04 | Community contribution quality degradation | Medium | Low | CI validation per contribution; review checklist; CODEOWNERS | v2.2.0 |
| R-05 | Single maintainer burnout | Medium | High | Institution contribution guide; CI automation; clear scope boundaries | Ongoing |
| R-06 | WASM compilation performance inadequate | High | Medium | Scope MVP to simple doctypes; incremental complexity | v3.0.0 |
| R-07 | Docker Hub rate limiting affects CI | Low | Low | GHCR primary registry; Docker Hub fallback only | v2.1.0 |
| R-08 | Python 3.14 deprecations break tooling | Low | Low | Pin hook runtimes to `python3`; test on 3.10-3.14 | v2.1.0 |
| R-09 | Visual regression false positives slow development | Medium | Medium | SSIM threshold tuning; per-doctype thresholds; manual override | v2.2.0 |
| R-10 | Docs site migration breaks existing links | Medium | Low | Redirect map; link checker in CI; phased rollout | v3.0.0 |

---

## 8. Dependency Graph

```
v2.0.0 (current)
  |
  +---> v2.1.0 (Polish/Hardening)
  |       |
  |       +--[KI-021,KI-022] Pin Actions to SHA + dependency review
  |       +--[KI-017] Fix visual-regression direct push
  |       +--[KI-013] CSS deduplication
  |       +--[KI-014,KI-015,KI-016,KI-020] Doc consistency fixes
  |       +--[KI-018] build.py E501 cleanup
  |       +---> CTAN submission (async, 1-2 week review)
  |               |
  |               +---> CTAN accepted
  |
  +---> v2.2.0 (Ecosystem) [depends: CTAN live from v2.1.0]
          |
          +---> Overleaf submission (async review)
          +---> VS Code marketplace publish
          +---> Community institutions (5+ new)
          +---> Per-doctype citation defaults
          +---> Accessibility (NVDA + PDF/UA-1)
          +---> Performance regression CI
          |
          +---> v3.0.0 (Scale) [depends: v2.2.0]
                  |
                  +---> Full Beamer document class
                  +---> Manual expansion (300+ pages)
                  +---> Docs site (MkDocs/Docusaurus) [parallel]
                  +---> WASM preview MVP [parallel, independent]
                  +---> Build performance optimization [parallel]
                  +---> Test suite expansion (700+ tests)
                  |
                  +---> v4.0+ (Future)
                          +---> Rust TUI build tool
                          +---> Template marketplace
                          +---> Multi-language docs
                          +---> Full manual (945 pages)
```

### Critical Path

```
CTAN submission (v2.1.0) --> CTAN accepted --> Overleaf (v2.2.0) --> v3.0.0
                                                              \
                                                               --> WASM MVP (parallel)
                                                               --> Docs site (parallel)
```

---

## 9. Metrics and Success Criteria

### Per-Phase Targets

| Metric | v2.0.0 | v2.1.0 | v2.2.0 | v3.0.0 | v4.0+ |
|--------|--------|--------|--------|--------|-------|
| CTAN status | Pending | Accepted | Live | Live | Live |
| Overleaf gallery | No | No | Submitted | Live | Premium |
| VS Code installs | 0 | 0 | 100+ | 1000+ | 5000+ |
| pytest tests | 473 | 500+ | 550+ | 700+ | 1000+ |
| l3build tests | 47 | 47 | 50+ | 60+ | 70+ |
| Lean 4 theorems | 196 | 200+ | 220+ | 300+ | 400+ |
| Examples | 47 | 47 | 52+ | 60+ | 70+ |
| Institutions | 21 | 21 | 26+ | 35+ | 50+ |
| Languages (full) | 18 | 18 | 20+ | 22+ | 25+ |
| Integration matrix langs | 4 | 4 | 6+ | 9+ | 12+ |
| Manual pages | 238 | 238 | 250+ | 300+ | 945+ |
| Docs site | No | No | No | MkDocs | Multi-lang |
| Web preview | No | No | No | MVP | Full |
| Build time (simple doc) | ~42s | ~42s | ~35s | ~25s | ~15s |
| Code coverage (Python) | 60% | 70% | 75% | 85% | 90% |
| Known critical/high issues | 2 | 0 | 0 | 0 | 0 |
| Actions SHA-pinned | No | Yes | Yes | Yes | Yes |
| CODEOWNERS | No | Yes | Yes | Yes | Yes |
| Language list verified (18) | No | Yes | Yes | Yes | Yes |

### Production Gate

All of the following must be TRUE before declaring production-ready:

1. CTAN package accepted and installable via `tlmgr`
2. Zero critical/high known issues (KI-*) open
3. All GitHub Actions pinned to SHA digests
4. Dependency review active on all PRs
5. Code coverage >= 80%
6. All 473+ tests pass with zero failures
7. All 196+ Lean 4 theorems compile with zero `sorry`
8. Visual regression gate active and stable
9. Docker multi-arch builds pass
10. Reproducible builds verified (SOURCE_DATE_EPOCH)
