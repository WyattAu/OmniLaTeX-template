# OmniLaTeX Production Roadmap

**Current version:** v2.0.0 | **Date:** 2026-05-17 | **License:** Apache 2.0

---

## Executive Summary

OmniLaTeX is a modular LaTeX template system with 28 `.sty` modules, 26 doctypes, 21 institution configs, 25 language support, 180 Lean 4 formal theorems, and 442 fast tests. This document charts the path from current state to production release (CTAN), ecosystem expansion, and long-term sustainability.

---

## Current State (v2.0.0)

### Maturity Assessment

| Area | Maturity | Evidence |
|------|----------|----------|
| Core template | Production-ready | 390-line `omnilatex.cls`, 28 modules, 55+ aliases |
| Formal verification | Industry-leading | 180 Lean 4 theorems (0 `sorry`), state machine proofs |
| Test coverage | High | 442 fast + 52 institution + slow tests, hypothesis property testing |
| CI/CD | Comprehensive | 10 GitHub Actions + 4 other platforms, digest-synced Docker |
| Reproducibility | Deterministic | SOURCE_DATE_EPOCH, byte-for-byte PDF, pinned Nix flake |
| Documentation | Thorough | 238-page manual, API reference, user guide, 13 doc files |
| Distribution | CTAN-ready | Auto-upload script, Overleaf zip, VS Code extension |

### Quantitative Metrics

| Metric | Value | Trend |
|--------|-------|-------|
| `.sty` modules | 28 | +1 (beamer, v2.0.0) |
| Document types | 26 (55+ aliases) | Stable |
| Example templates | 46 | +3 (beamer, v2.0.0) |
| Institution configs | 21 | Stable |
| Languages (full translations) | 18 | Stable |
| Languages (polyglossia) | 25 | Stable |
| Lean 4 theorems | 180 | +25 (beamer, v2.0.0) |
| Fast test count | 442 | +53 (institutions, v1.23.0) |
| CI workflows | 14 | Stable |
| Manual pages | 238 (12.4k lines) | Stable |

### Critical Path Items

1. CTAN submission -- script ready, pending human review
2. Overleaf gallery submission -- manual web form, async review
3. VS Code marketplace publish -- extension v1.0.0 ready
4. Manual completion -- 12 thin chapters need expansion
5. Full Beamer document class -- `.sty` module shipped, standalone class planned

---

## Phase 1: CTAN Submission (v1.26.0)

**Target:** 1 week | **Priority:** Critical | **Risk:** Low

### Tasks

| ID | Task | Effort | Dependency |
|----|------|--------|------------|
| 1.1 | Final CTAN metadata review (README, CTAN_README.txt) | 2h | None |
| 1.2 | Verify all 46 examples compile clean on TeX Live 2025+ | 4h | Docker |
| 1.3 | Run `scripts/ctan-upload.sh` dry-run validation | 1h | 1.1, 1.2 |
| 1.4 | Submit to CTAN via web form or `ctan-upload` script | 1h | 1.3 |
| 1.5 | Monitor CTAN review queue (typically 1-2 weeks) | Ongoing | 1.4 |
| 1.6 | Address CTAN reviewer feedback | Variable | 1.5 |
| 1.7 | Post-submission: verify `tlmgr install omnilatex` works | 2h | 1.6 |

### Acceptance Criteria

- Package passes CTAN automated checks
- All files conform to CTAN naming conventions
- `tlmgr install omnilatex` succeeds on clean TeX Live 2025+
- CTAN README accurate and complete

### Risk Mitigation

- CTAN may request changes to file layout or documentation
- Mitigation: pre-run CTAN validation script locally

---

## Phase 2: Ecosystem Distribution (v1.27.0)

**Target:** 2-3 weeks | **Priority:** High | **Risk:** Medium

### Tasks

| ID | Task | Effort | Dependency |
|----|------|--------|------------|
| 2.1 | Overleaf gallery submission (manual web form) | 2h | None |
| 2.2 | Overleaf gallery review cycle | 1-2 weeks | 2.1 |
| 2.3 | VS Code marketplace publish (`vsce publish`) | 2h | None |
| 2.4 | VS Code extension analytics monitoring | Ongoing | 2.3 |
| 2.5 | Nix package update (ensure `nix build .#omnilatex` works) | 2h | None |
| 2.6 | Documentation: update install instructions for CTAN path | 3h | Phase 1 |

### Acceptance Criteria

- OmniLaTeX appears in Overleaf template gallery
- VS Code extension installable from marketplace
- `nix build .#omnilatex` produces valid package
- README install section covers CTAN, Overleaf, Nix, Docker, VS Code

---

## Phase 3: Beamer Full Class (v2.0.0)

**Target:** 3-4 weeks | **Priority:** High | **Risk:** Medium

This is a breaking change release (major version bump) due to potential API surface expansion.

### Tasks

| ID | Task | Effort | Dependency |
|----|------|--------|------------|
| 3.1 | Design standalone `omnilatex-beamer` document class | 4h | None |
| 3.2 | Implement Beamer class wrapping KOMA-Script beamer patterns | 8h | 3.1 |
| 3.3 | Add Beamer-specific options (aspect ratio, navigation, etc.) | 4h | 3.2 |
| 3.4 | Create 3 Beamer example templates (academic, corporate, minimal) | 4h | 3.2 |
| 3.5 | Extend Lean 4 proofs for Beamer class properties | 4h | 3.2 |
| 3.6 | Add Beamer doctype aliases to `omnilatex.cls` | 2h | 3.2 |
| 3.7 | Update all documentation for Beamer support | 4h | 3.4 |
| 3.8 | Visual regression tests for Beamer PDFs | 4h | 3.4 |
| 3.9 | BREAKING_CHANGES.md update for v2.0.0 | 2h | 3.6 |

### Acceptance Criteria

- `\documentclass[doctype=beamer-academic]{omnilatex}` compiles
- 25+ Lean theorems for Beamer properties (already have 25 from v2.0.0)
- All 3 Beamer examples compile clean
- API stability doc updated with Beamer surface
- No regressions in existing 43 non-Beamer examples

---

## Phase 4: Community and Accessibility (v2.1.0)

**Target:** 3-4 weeks | **Priority:** Medium | **Risk:** Low

### Tasks

| ID | Task | Effort | Dependency |
|----|------|--------|------------|
| 4.1 | Community institution configs (Aalto, Chalmers, KIT, NTNU, UofT) | 8h | None |
| 4.2 | Institution contribution CI validation | 4h | 4.1 |
| 4.3 | NVDA screen reader validation for PDF output | 4h | None |
| 4.4 | PDF/UA-1 compliance verification | 8h | 4.3 |
| 4.5 | Per-doctype citation defaults (IEEE for articles, APA for thesis) | 4h | None |
| 4.6 | Docker font bundling (Monaspace Neon, Atkinson Hyperlegible) | 4h | None |
| 4.7 | Performance regression CI (benchmark gating) | 8h | None |

### Acceptance Criteria

- 5+ new institution configs with CI validation
- NVDA can read PDF content without errors
- PDF passes PDF/UA-1 automated checks
- Default citation style varies by doctype
- Docker image includes all referenced fonts
- CI fails if compile time regresses >10%

---

## Phase 5: Manual Completion (v2.2.0)

**Target:** 4-6 weeks | **Priority:** Medium | **Risk:** Low

### Tasks

| ID | Task | Effort | Dependency |
|----|------|--------|------------|
| 5.1 | Expand 12 thin chapters to >150 lines each | 16h | None |
| 5.2 | Add index, list of examples, list of listings | 4h | 5.1 |
| 5.3 | Screenshots of VS Code extension workflow | 2h | Phase 2 |
| 5.4 | PDF screenshots of key doctypes | 4h | None |
| 5.5 | TikZ architecture diagrams | 4h | None |
| 5.6 | Cross-reference validation between chapters | 2h | 5.1 |
| 5.7 | Publish manual PDF | 2h | 5.6 |

### Acceptance Criteria

- All 59 chapters >150 lines
- Manual compiles without warnings
- All cross-references resolve
- Visual assets (screenshots, diagrams) included

---

## Phase 6: Scale and Platform (v3.0.0)

**Target:** 3-6 months | **Priority:** Long-term | **Risk:** High

### Tasks

| ID | Task | Effort | Dependency |
|----|------|--------|------------|
| 6.1 | Complete manual to 945 pages | 40h | Phase 5 |
| 6.2 | Overleaf premium template listing | 4h | Phase 2 |
| 6.3 | Web preview via LaTeX WASM (texlive.js) | 80h | None |
| 6.4 | Rust TUI build tool (replaces build.py) | 120h | None |
| 6.5 | Template marketplace / gallery website | 80h | None |
| 6.6 | Multi-language documentation (ZH, DE, FR) | 40h | Phase 5 |

### Acceptance Criteria

- Manual reaches 945+ pages
- Live web preview at omnilatex.dev (or similar)
- Rust build tool replaces Python build.py
- Template gallery accessible via web

### Technical Feasibility Notes

- **LaTeX WASM:** texlive.js exists but full template compilation in-browser requires significant work. Initial MVP: preview simple documents only.
- **Rust TUI:** build.py is 2094 lines. Rust rewrite enables faster builds, better error handling, and cross-platform binary distribution. Use `clap` for CLI, `rayon` for parallel compilation.
- **Marketplace:** Could leverage GitHub Pages + Jekyll for low-cost hosting. User submissions via PR workflow.

---

## Phase 7: Sustainability (Ongoing)

### Continuous Items

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Dependency vulnerability scanning | Weekly | Automated (Dependabot/Renovate) |
| TeX Live compatibility testing | Per TL release | CI |
| Lean 4 proof maintenance | Per new feature | Developer |
| Institution config contributions | Ongoing | Community |
| Documentation updates | Per release | Developer |
| Performance regression monitoring | Per CI run | Automated |

### Lean 4 Proof Expansion

Current: 180 theorems. Target areas for expansion:

| Domain | Current | Target | Priority |
|--------|---------|--------|----------|
| Page geometry invariants | 17 | 30 | High |
| Cross-reference consistency | 26 | 40 | High |
| Module integrity | 26 | 35 | Medium |
| Font hierarchy | 4 | 15 | Medium |
| Build system properties | 14 | 25 | Medium |
| I18n completeness | 9 | 20 | Low |
| Float invariants | 2 | 10 | Low |

### Test Suite Expansion

Current: 442 fast + 52 institution. Target areas:

| Domain | Current | Target | Priority |
|--------|---------|--------|----------|
| Structural tests | 200+ | 250+ | High |
| Property-based tests | 21 | 40 | High |
| Visual regression | 4 | 20 | Medium |
| Integration tests | 47 (l3build) | 60 | Medium |
| Edge case compilation | 6 | 15 | Low |
| Unicode stress tests | 10 | 20 | Low |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CTAN rejection | Low | High | Pre-run validation, follow CTAN guidelines strictly |
| TeX Live breaking changes | Medium | High | Pin minimum TL version, test on TL pre-release |
| Lean 4 toolchain breakage | Low | Medium | Pin lean-toolchain, lake-manifest.json in VCS |
| Community contribution quality | Medium | Low | CI validation, contribution guide, review process |
| WASM performance | High | Medium | Start with simple documents, incremental complexity |
| Maintenance burden | Medium | Medium | Automate dependency updates, limit scope creep |

---

## Version Timeline

```
v2.0.0 (current) -----> v1.26.0 (CTAN) -----> v1.27.0 (Ecosystem)
     |                        1 week               2-3 weeks
     |
     +-----> v2.0.0 (Beamer) -----> v2.1.0 (Community) -----> v2.2.0 (Manual)
                   3-4 weeks               3-4 weeks               4-6 weeks
                   |
                   +-----> v3.0.0 (Scale) -----> v3.1.0 (Sustainability)
                              3-6 months              Ongoing
```

---

## Success Metrics

| Metric | Current (v2.0.0) | v2.0.0 Target | v3.0.0 Target |
|--------|-------------------|---------------|---------------|
| CTAN availability | Pending | Live | Live |
| Overleaf gallery | No | Submitted | Premium |
| VS Code installs | 0 | 100+ | 1000+ |
| Lean 4 theorems | 180 | 200+ | 300+ |
| Fast tests | 442 | 500+ | 700+ |
| Examples | 46 | 50+ | 60+ |
| Institutions | 21 | 25+ | 40+ |
| Manual pages | 238 | 300+ | 945+ |
| Web preview | No | No | Yes (MVP) |
| Docker pulls | Tracking | 500+ | 5000+ |

---

## Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| LuaLaTeX-only engine | Required for fontspec, polyglossia, Lua-based features | v1.0.0 |
| KOMA-Script base classes | Superior typography, multilingual support vs. standard classes | v1.0.0 |
| Lean 4 for verification | Mathematical rigor, no Mathlib dependency, decidable proofs | v1.4.0 |
| Nix flake for reproducibility | Pinned dependencies, cross-platform, hermetic builds | v1.7.0 |
| Apache 2.0 license | Permissive, compatible with TeX Live, community-friendly | v1.0.0 |
| Beamer as module first | Incremental approach: module validates design before full class | v2.0.0 |
| Docker multi-arch | arm64 (Apple Silicon) + amd64 coverage | v1.7.0 |
