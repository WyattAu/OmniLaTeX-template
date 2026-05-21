# OmniLaTeX: Path to Production and Beyond

**Version:** v2.0.0
**Date:** 2026-05-21
**Status:** Active Development

---

## Current State Summary

OmniLaTeX v2.0.0 is a mature, engineering-grade LaTeX document class with:

- 27 document type profiles (55+ aliases) across 3 KOMA-Script base classes + Beamer
- 31 modular .sty packages across 9 subdirectories
- 48 ready-to-use example templates
- 21 institution configurations
- 18 fully translated languages + 25 via polyglossia
- 198 Lean 4 formally verified theorems across 16 proof modules
- 12 GitHub Actions workflows + 4 alternative CI platforms
- 760+ passing tests (fast suite), full pre-commit gate
- Multi-architecture Docker image (amd64/arm64)
- MkDocs documentation site deployed to GitHub Pages
- Cloudflare Pages configuration for Forgejo-hosted mirrors

---

## Phase 1: Stabilization (v2.1.0) -- Target: 2 Weeks

### Goal

Eliminate all known defects, close technical debt, and achieve zero-warning CI.

### Tasks

| ID | Task | Priority | Est. |
|----|------|----------|------|
| S-01 | Fix OmniPrimaryColor/OmniAccentColor undefined in Beamer mode | Critical | 2h |
| S-02 | Fix math notation commands depending on optional glossaries package | Critical | 3h |
| S-03 | Fix Arabic-Indic numeral reversal in omnilatex-rtl.sty | Critical | 2h |
| S-04 | Fix todo-tracker.lua global counter logic bug | High | 1h |
| S-05 | Add pcall to word-count.lua for luatexbase loading | High | 1h |
| S-06 | Fix "examiner" -> "examiner" typo across codebase | High | 2h |
| S-07 | Deduplicate test constants (single source in constants.py) | High | 4h |
| S-08 | Fix visual regression cache key to include Docker digest | Medium | 1h |
| S-09 | Move inline Python in performance-regression.yml to scripts/ | Medium | 2h |
| S-10 | Add timeout-minutes to all Gitea/Forgejo workflow jobs | Medium | 1h |
| S-11 | Fix lean4-ci.yml hardcoded module list (use filesystem) | Medium | 1h |
| S-12 | Fix performance-regression.yml metrics count bug | Medium | 1h |
| S-13 | Add beamer-native to constants.py DOCTYPE_ALIASES | Medium | 0.5h |
| S-14 | Remove dead "pages" config from visual_regression.py | Low | 0.5h |
| S-15 | Add fetch-depth: 1 to Forgejo/Gitea lint/test jobs | Low | 0.5h |

### Acceptance Criteria

- All CI workflows pass with zero warnings
- All 760+ tests pass
- Lean 4 proofs compile with zero errors
- No TODO/FIXME markers in production .sty/.cls files
- Pre-commit hook enforces test gate

---

## Phase 2: Test Coverage Expansion (v2.2.0) -- Target: 3 Weeks

### Goal

Achieve comprehensive test coverage across all modules, CLI commands, and edge cases.

### Tasks

| ID | Task | Priority | Est. |
|----|------|----------|------|
| T-01 | Add module compilation tests for lib/layout, lib/typography, lib/references, lib/language, lib/tables, lib/utils | High | 6h |
| T-02 | Add CLI tests for build, build-root, clean, lint, watch, doctor commands | High | 4h |
| T-03 | Expand negative tests (circular refs, corrupt bib, invalid languages, conflicting options) | High | 3h |
| T-04 | Add Unicode edge cases (Thai, Georgian, ZWJ sequences, bidirectional text) | Medium | 3h |
| T-05 | Add concurrent build tests (parallel compilation safety) | Medium | 2h |
| T-06 | Add error recovery tests (LaTeX error handling beyond crash) | Medium | 2h |
| T-07 | Parametrize Overleaf zip tests across multiple examples | Medium | 2h |
| T-08 | Add thesis-tuhh and beamer-native to visual regression EXAMPLES | Medium | 1h |
| T-09 | Add property-based tests for remaining doctypes (beamer, invoice) | Medium | 2h |
| T-10 | Verify PDF content (not just existence) for Unicode tests | Low | 3h |

### Acceptance Criteria

- 900+ tests passing
- All 9 lib subdirectories have module compilation tests
- All CLI commands have at least basic invocation tests
- Negative tests catch actual error conditions (not tautological)

---

## Phase 3: Distribution (v2.3.0) -- Target: 4 Weeks

### Goal

Publish OmniLaTeX to CTAN, Overleaf Gallery, and VS Code Marketplace.

### Tasks

| ID | Task | Priority | Est. |
|----|------|----------|------|
| D-01 | Complete CTAN submission review process | Critical | 4h |
| D-02 | Submit to Overleaf template gallery | Critical | 3h |
| D-03 | Publish VS Code extension to marketplace | High | 4h |
| D-04 | Create dedicated landing page (proper intro + docs link + gallery) | High | 6h |
| D-05 | Build and host example PDFs for the gallery | High | 4h |
| D-06 | Add interactive template picker to landing page | Medium | 4h |
| D-07 | Set up Cloudflare Pages deployment for Forgejo mirror | Medium | 2h |
| D-08 | Create demo video/GIF for README | Medium | 2h |

### Acceptance Criteria

- CTAN package published and installable via `tlmgr install omnilatex`
- Overleaf template searchable and usable
- VS Code extension installable from marketplace
- Landing page live at custom domain or GitHub Pages
- Example PDFs viewable in browser

---

## Phase 4: Community (v2.4.0) -- Target: 6 Weeks

### Goal

Build contributor base, add community-requested institutions, and establish feedback loops.

### Tasks

| ID | Task | Priority | Est. |
|----|------|----------|------|
| C-01 | Streamline institution contribution workflow (scaffold-institution improvements) | High | 4h |
| C-02 | Add 10+ community institution configs | High | 8h |
| C-03 | Set up GitHub Discussions for Q&A | Medium | 1h |
| C-04 | Create CONTRIBUTING.md video tutorial / detailed guide | Medium | 4h |
| C-05 | Implement per-doctype citation defaults (IEEE/APA/Vancouver) | Medium | 4h |
| C-06 | Add accessibility testing (NVDA, PDF/UA-1) | Medium | 6h |
| C-07 | Expand Lean 4 proofs to 220+ theorems | Medium | 8h |
| C-08 | Add remaining CJK example (Traditional Chinese) | Low | 2h |

### Acceptance Criteria

- 30+ institution configurations
- Contribution guide with step-by-step examples
- GitHub Discussions active with triage process
- PDF/UA-1 compliance report

---

## Phase 5: Scale (v3.0.0) -- Target: 3 Months

### Goal

Transform from template to platform: web preview, comprehensive manual, advanced features.

### Tasks

| ID | Task | Priority | Est. |
|----|------|----------|------|
| V3-01 | Web preview: LaTeX compilation via WASM (LaTeX.js or similar) | High | 40h |
| V3-02 | Complete manual to 500+ pages (currently 238) | High | 30h |
| V3-03 | Full standalone Beamer document class | High | 20h |
| V3-04 | Rust TUI build tool (replace build.py) | Medium | 40h |
| V3-05 | Template marketplace / sharing platform | Medium | 60h |
| V3-06 | Additional Docker fonts (full CJK, academic symbols) | Medium | 8h |
| V3-07 | Performance regression CI with historical tracking | Medium | 8h |
| V3-08 | Formal verification coverage: all safety-critical algorithms | Low | 20h |

### Acceptance Criteria

- Web preview working in browser for at least 10 doctypes
- Manual published as physical-quality PDF
- Beamer class published independently on CTAN
- 1000+ tests passing with 95%+ branch coverage on critical paths

---

## Technical Debt Register

| Item | Severity | Phase | Notes |
|------|----------|-------|-------|
| 12 thin manual chapters (<100 lines) | Medium | v3.0 | Expand to >150 lines each |
| Test constants duplicated across 4 files | High | v2.1 | Deduplicate to constants.py only |
| 1 HACK in omnilatex-math.sty:230 | Low | v2.1 | Proper vertical spacing solution |
| CSS duplication across pages/*.html | Low | v2.3 | Extract shared styles |
| .hypothesis/ and build artifacts in repo root | Low | v2.1 | Clean and gitignore |
| tests/pyproject.toml author is stale | Low | v2.1 | Update to WyattAu |
| tests/config.yml appears unused | Low | v2.2 | Remove or integrate |
| Module test coverage only 44% (4/9 subdirs) | High | v2.2 | Add remaining 5 modules |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| CTAN review rejects package | Medium | High | Pre-validate with `ctan_validate` tool; follow CTAN guidelines |
| LaTeX 2026 breaks compatibility | Low | High | Pin TeX Live version in Docker; CI tests against TL2025 and TL2026 |
| Lean 4 breaking changes | Medium | Medium | Pin Lean 4 version in lakefile; test with latest stable |
| Community contributions are low quality | Medium | Medium | Automated CI validation; template-based contribution workflow |
| WASM preview performance | High | Medium | Fallback to server-side compilation; progressive enhancement |

---

## Metrics and Success Criteria

| Metric | Current | v2.1 Target | v2.3 Target | v3.0 Target |
|--------|---------|-------------|-------------|-------------|
| Passing tests | 760 | 800 | 900 | 1000 |
| Branch coverage (critical) | ~85% | 90% | 93% | 95% |
| Lean 4 theorems | 198 | 198 | 210 | 230 |
| Document types | 27 | 27 | 27 | 30+ |
| Institutions | 21 | 21 | 30+ | 40+ |
| CI pass rate | ~80% | 95% | 99% | 99.5% |
| Documentation accuracy | Partial | Verified | Verified | Verified |
| Distribution channels | Docker/CI only | +CTAN | +Overleaf+VS Code | +Web preview |
| Contributors | 1 | 1-3 | 5-10 | 10-20 |

---

## Architecture Principles for Future Development

1. **Reproducibility first**: Every build must be byte-for-byte deterministic with `SOURCE_DATE_EPOCH`
2. **Modular architecture**: Each feature is an independently loadable .sty module with formal interface contracts
3. **Multi-language native**: Polyglossia-based from the start, not English-first with patches
4. **CI/CD as documentation**: Pipeline configurations serve as usage examples
5. **Distribution before features**: CTAN + Overleaf + VS Code unlock global reach before adding more features
6. **Formal verification where it matters**: Lean 4 proofs for complex algorithms, property-based testing for everything else
7. **No stubs in production**: Every command, environment, and option must be fully implemented
8. **Test gate enforcement**: Pre-commit hook prevents any push that fails tests

---

## Timeline Summary

```
Week 1-2:  Phase 1 (Stabilization) -- v2.1.0
Week 3-5:  Phase 2 (Test Coverage) -- v2.2.0
Week 6-9:  Phase 3 (Distribution)  -- v2.3.0
Week 10-15: Phase 4 (Community)    -- v2.4.0
Week 16-28: Phase 5 (Scale)        -- v3.0.0
```

---

*This roadmap is a living document. Update after each phase completion.*
