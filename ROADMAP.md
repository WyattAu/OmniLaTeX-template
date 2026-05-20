# OmniLaTeX Roadmap

Current version: **v2.0.0**

## Design Principles

1. **Reproducibility first** -- byte-for-byte deterministic builds, pinned dependencies
2. **Modular architecture** -- every feature is a `.sty` module with formal contracts
3. **Multi-language native** -- polyglossia-based, not English-first with patches
4. **CI/CD as documentation** -- pipelines that double as usage examples
5. **Distribution before features** -- CTAN + Overleaf + VS Code unlock global reach

## Project Snapshot

| Metric | Value |
|--------|-------|
| Releases | 28 (v1.0.0--v2.0.0) |
| `.sty` modules | 28 |
| Document types | 26 (55+ aliases) across 3 KOMA-Script base classes |
| Examples | 46 |
| Institution configs | 21 |
| Languages | 18 with full OmniLaTeX translations + 25 via polyglossia |
| Translation keys | 846 total (47 keys x 18 languages) |
| CI workflows | 12 GitHub Actions + 4 other platforms |
| Tests | 442 fast tests + 16 institution tests + slow tests |
| Lean 4 proofs | 198 theorems, 16 modules, 0 sorry |
| Color themes | 6 presets + dark/light toggle |
| Citation styles | 9 (IEEE, ACM, APA, Chicago, Nature, Science, Harvard, Vancouver, MLA) |
| CJK support | Chinese (SC+TC), Japanese, Korean |
| RTL support | Arabic, Hebrew, Persian |
| Manual | 238 pages, 59 chapters, 12.4k lines |
| Core code | ~16,500 lines |
| License | Apache 2.0 |

---

## Completed Versions

| Version | Date | Summary |
|---------|------|---------|
| v2.0.0 | 2026-05-11 | Beamer support, pytest-cov CI, VS Code build-on-save |
| v1.24.0 | 2026-05-11 | 154 Lean theorems, deprecation mechanism, institution docs, semver/digest checks |
| v1.23.0 | 2026-05-11 | 128 Lean theorems, 47 l3build tests, institution tests, full doc audit |
| v1.22.0 | 2026-05-11 | Docker digest sync, CHANGELOG split, README dedup, visual regression CI, doctype tests |
| v1.21.0 | 2026-05-11 | ModuleIntegrity proofs, pre-commit Python 3.14 compat, audits |
| v1.20.0 | 2026-05-11 | BuildModeStrictness proofs (20 theorems), build.py type hints |
| v1.19.0 | 2026-05-10 | build.py tests, API stability doc, Nix flake, accessibility cleanup |
| v1.18.0 | 2026-05-11 | Lean proof-code consistency, CI hardening, quality sweep |
| v1.17.0 | 2026-05-10 | 238-page manual (60 chapters), documentitemspacing fix, audit sweep |
| v1.16.0 | 2026-05-06 | 53 Lean theorems (10 modules), 508 tests, TikZ figures, audit fixes |
| v1.15.0 | 2026-05-05 | Visual regression, digest consistency, 10 Lean proof modules |
| v1.14.0 | 2026-05-04 | Columbia/Harvard institutions, invoice/recipe doctypes, 5 TikZ figures |
| v1.13.0 | 2026-05-03 | Module version bump, Persian RTL, 5 new translations |
| v1.12.0 | 2026-05-03 | Polish -- Persian RTL, NL/PL/CS/EL/TR translations, flake.nix |
| v1.11.0 | 2026-05-02 | 18 secondary languages, FR/ES/RU/IT/PT translations |
| v1.10.0 | 2026-05-02 | 4 new doctypes (lecture-notes, syllabus, handout, memo) |
| v1.9.0 | 2026-05-02 | CTAN CI, Overleaf zip, 282 integration tests |
| v1.8.0 | 2026-05-02 | 3 new doctypes (exam, homework, research-proposal) |
| v1.7.1 | 2026-04-30 | .sty/.cls audit, KOMA TL2025 compat, font consolidation |
| v1.7.0 | 2026-04-29 | CI/CD hardening, Docker multi-arch, Nix packages |
| v1.6.0 | 2026-04-26 | TL2025 migration, CI/CD hardening, supply chain pinning |
| v1.5.0 | 2026-04-24 | 14 institutions, color theme system |
| v1.4.0 | 2026-04-24 | Documentation reconciliation, Lean 4 CI |
| v1.3.1 | 2026-04-24 | Docker monorepo merge, cross-platform CI fix |
| v1.3.0 | 2026-04-23 | poster/presentation/letter, scaffold-language |
| v1.2.0 | 2026-04-23 | TUM/ETH institutions, cross-platform CI, Lean 4 |
| v1.1.0 | 2026-04-22 | README v2, CONTRIBUTING, CTAN/Overleaf packaging |
| v1.0.0 | 2026-04-03 | Foundation -- Nix, 20 examples, build.py, CI/CD |

---

## v2.0.0 -- Ecosystem (target: Month 2)

| Project | Priority | Status |
|---------|----------|--------|
| **P20.1 Full Beamer class** | High | Partial -- `omnilatex-beamer.sty` shipped in v2.0.0; standalone Beamer document class planned |
| **P20.2 Community institution configs** | High | Planned |
| **P20.3 Per-doctype citation defaults** | Medium | Planned |
| **P20.4 Accessibility testing** | Medium | Planned |
| **P20.5 Additional Docker fonts** | Medium | Planned |
| **P20.6 Performance regression CI** | Medium | Planned |

### P20.1 Full Beamer Class

- Standalone `omnilatex-beamer` document class (current `.sty` is a module)
- Compatible with existing institution configs
- Example slides matching all 6 colour themes
- 25 formal proofs already verified (BeamerProperties.lean)

### P20.2 Community Institutions

- Aalto, Chalmers, KIT, NTNU, University of Toronto, etc.
- Contribution guide for new institutions
- CI validation for each config

### P20.3 Citation Defaults

- IEEE default for article/journal/inlinepaper
- APA default for thesis/dissertation
- Vancouver default for medical/standard

### P20.4 Accessibility Testing

- NVDA screen reader validation
- PDF/UA-1 compliance verification
- EN 301 549 documentation

**Completion criteria:** Full Beamer class published, 5+ new institutions, accessibility validated.

---

## v3.0.0 -- Scale (target: Month 6)

| Project | Priority | Status |
|---------|----------|--------|
| **P30.1 Complete manual to 945 pages** | High | Planned |
| **P30.2 Overleaf premium template** | High | Planned |
| **P30.3 Web preview (LaTeX via WASM)** | High | Planned |
| **P30.4 Rust TUI build tool** | Medium | Exploratory |
| **P30.5 Template marketplace** | Medium | Planned |

**Completion criteria:** Published book-quality manual, Overleaf premium listing, web preview.

---

## Priority Matrix

| Priority | Items |
|----------|-------|
| **Critical** | CTAN submission (script ready, pending review) |
| **High** | Overleaf submission, VS Code extension, manual expansion, full Beamer class |
| **Medium** | Community institutions, accessibility (NVDA/PDF-UA), Docker fonts, perf regression CI |
| **Long-term** | WASM preview, Rust TUI, template marketplace |

---

## Technical Debt

| Item | Severity | Notes |
|------|----------|-------|
| 12 thin manual chapters (<100 lines) | Medium | Expand to >150 lines each |
| Test constants duplicated across constants.py and test_properties.py | Low | Deduplicate DOCTYPE_ALIASES |
| 1 HACK in omnilatex-math.sty:230 | Low | Proper vertical spacing |
