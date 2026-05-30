# OmniLaTeX Roadmap

Current version: **v2.2.0**

See [ROADMAP-v3.md](ROADMAP-v3.md) for the comprehensive, phase-by-phase technical roadmap.

## Design Principles

1. **Reproducibility first** -- byte-for-byte deterministic builds, pinned dependencies
2. **Modular architecture** -- every feature is a `.sty` module with formal contracts
3. **Multi-language native** -- polyglossia-based, not English-first with patches
4. **CI/CD as documentation** -- pipelines that double as usage examples
5. **Distribution before features** -- CTAN + Overleaf + VS Code unlock global reach

## Project Snapshot

| Metric | Value |
|--------|-------|
| Releases | 32 (v1.0.0--v2.2.0) |
| `.sty` modules | 31 across 9 subdirectories |
| Document types | 27 (55+ aliases) across 3 KOMA-Script base classes + Beamer |
| Examples | 48 templates (all compile on TeX Live 2025+) |
| Institution configs | 21 pluggable configs |
| Languages | 25+ via polyglossia (CJK, RTL, Cyrillic) |
| Tests (fast) | 775 passing, 52 skipped, 293 deselected |
| Lean 4 proofs | 198 theorems, 16 modules, 0 sorry |
| CI/CD | 15 GitHub Actions + 4 other platforms |
| Docker | Multi-arch (amd64/arm64), digest-synced, GHCR-hosted |
| Documentation | MkDocs Material (19 pages) |
| Manual | 238 pages, 59 chapters |
| Build system | `buildlib/` package (9 modules, mixin composition), 14-line `build.py` wrapper |
| Determinism | Byte-for-byte reproducible PDFs via SOURCE_DATE_EPOCH |
| Export formats | HTML (LaTeXML), EPUB, DOCX (pandoc) via `build.py export` |
| Citation styles | 9 pre-configured (IEEE, ACM, APA, Chicago, Nature, Science, Harvard, Vancouver, MLA) |

---

## Completed Versions

| Version | Date | Summary |
|---------|------|---------|
| v2.2.0 | 2026-05-26 | PDF content validation, glossaries-extra fix, beamer/accessibility ProvidesPackage, test hardening, Lean 4 cache, changelog |
| v2.1.0 | 2026-05-24 | Docker digest sync, CHANGELOG split, ROADMAP v2, Overleaf zip validation |
| v2.0.0 | 2026-05-11 | Beamer support, pytest-cov CI, VS Code build-on-save |
| v1.24.0 | 2026-05-11 | 154 Lean theorems, deprecation mechanism, institution docs, semver/digest checks |
| v1.17.0 | 2026-05-10 | 238-page manual (60 chapters), documentitemspacing fix, audit sweep |

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

## Immediate Priorities

| Priority | Item | Status |
|----------|------|--------|
| Critical | CTAN submission (script ready, pending review) | Open |
| High | Overleaf template submission | Planned |
| High | VS Code extension marketplace listing | Planned |
| High | README/docs accuracy for v2.2.0 features | In progress |

## Technical Debt

| Item | Severity | Notes |
|------|----------|-------|
| ROADMAP.md out of date | Low | This file; ROADMAP-v3.md is canonical |
| 12 thin manual chapters (<100 lines) | Medium | Expand to >150 lines each |
| Test constants duplicated between constants.py and test_properties.py | Low | Deduplicate DOCTYPE_ALIASES |
| 1 HACK in omnilatex-math.sty:230 | Low | Proper vertical spacing |
| visual_regression.py SSIM deduplicated but run_module_tests.py still has some code duplication | Low | Minor |

---

## Near-Term Targets (v2.3.0)

| Project | Priority |
|---------|----------|
| Additional Docker fonts (DejaVu, Fira Code) | Medium |
| Performance regression CI (automated timing baselines) | Medium |
| Accessibility NVDA screen reader validation | Medium |
| Per-doctype citation defaults (IEEE for articles, APA for thesis) | Medium |
| Community institution contribution guide | Medium |

## Long-Term Targets (v3.0.0)

| Project | Priority |
|---------|----------|
| WASM-based LaTeX preview (LaTeX in browser) | High |
| Rust TUI build tool (replace Python build.py core) | Low |
| Template marketplace (curated third-party templates) | Low |
| Expanded manual (book-quality, 500+ pages) | Medium |
