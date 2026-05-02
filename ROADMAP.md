# OmniLaTeX Roadmap

Current version: **v1.11.0**

## Design Principles

1. **Reproducibility first** — byte-for-byte deterministic builds, pinned dependencies
2. **Modular architecture** — every feature is a `.sty` module with formal contracts
3. **Multi-language native** — polyglossia-based, not English-first with patches
4. **CI/CD as documentation** — pipelines that double as usage examples

## Project Snapshot

| Metric | Value |
|--------|-------|
| Releases | 14 (v1.0.0–v1.11.0) |
| `.sty` modules | 27 |
| Document types | 23 (thesis, dissertation, article, journal, inlinepaper, book, manual, technicalreport, standard, patent, cv, cover-letter, poster, presentation, letter, dictionary, homework, exam, research-proposal, lecture-notes, syllabus, handout, memo) |
| Examples | 39 (39/39 compile on Docker TL2026) |
| Institution configs | 15 |
| Languages | 14 primary + 18 secondary via polyglossia (EN, DE, FR, ES, ZH, JA, KO, AR, HE, RU, IT, PT, NL, PL, CS, EL, TR) |
| Translation keys | 55+ across 7 languages (EN, DE, FR, ES, RU, IT, PT) |
| CI workflows | 7 (all green) |
| Integration tests | 318 (across 6 categories) |
| Lean 4 proofs | 13 proven, 7 retained (false as stated, need hypotheses) |
| Core code | ~15,000 lines |
| License | Apache 2.0 |

---

## Completed Versions

| Version | Date | Summary |
|---------|------|---------|
| v1.11.0 | 2026-05-02 | Languages — 18 secondary languages, 55+ translations (FR/ES/RU/IT/PT), TC Chinese auto-detect, 7 Lean proofs, CTAN guide |
| v1.10.0 | 2026-05-02 | Distribution — 4 new document types (lecture-notes, syllabus, handout, memo), 39 examples, CTAN CI updated |
| v1.9.0 | 2026-05-02 | Growth — CTAN CI, Overleaf zip, 282 integration tests, 8 missing configs fixed, Pages gallery update |
| v1.8.0 | 2026-05-02 | Distribution — 3 new document types (exam, homework, research-proposal), CTAN packaging, Pages gallery, font setters, 6 bug fixes, template enrichment |
| v1.7.1 | 2026-04-30 | Quality — .sty/.cls audit (6 fixes), KOMA TL2025 compat, font consolidation, CI hardening |
| v1.7.0 | 2026-04-29 | Infrastructure — CI/CD hardening, Docker multi-arch, Nix packages, digest sync |
| v1.6.0 | 2026-04-26 | Hardening — TL2025 migration, CI/CD hardening, supply chain pinning |
| v1.5.0 | 2026-04-24 | Institutions — 14 configs, Beamer overhaul, color theme system |
| v1.4.0 | 2026-04-24 | Accuracy — documentation reconciliation, Lean 4 CI, Docker digests |
| v1.3.1 | 2026-04-24 | Housekeeping — Docker monorepo merge, cross-platform CI fix |
| v1.3.0 | 2026-04-23 | Features — poster/presentation/letter, scaffold-language, perf baselines |
| v1.2.0 | 2026-04-23 | Ecosystem — TUM/ETH institutions, cross-platform CI, Lean 4, CWL |
| v1.1.0 | 2026-04-22 | Distribution — README v2, CONTRIBUTING, CTAN/Overleaf packaging |
| v1.0.0 | 2026-04-03 | Foundation — Nix, 20 examples, build.py, CI/CD |

---

## v1.12.0 — Polish & Distribution (target: 2–4 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P12.1 CTAN submission** | High | Ready (script + guide + CI) |
| **P12.2 Overleaf gallery submission** | Medium | Ready (script + docs) |
| **P12.3 Persian/Farsi RTL support** | Medium | Planned |
| **P12.4 Dutch, Polish, Czech translations** | Low | Planned |
| **P12.5 VS Code extension MVP** | Low | Planned |
| **P12.6 Lean 4: fix false theorems** | Low | Planned |

### P12.1 CTAN Submission
- Submit `omnilatex.zip` to CTAN (script ready, CI validates, guide in docs/CTAN_SUBMISSION.md)
- Maintain CTAN metadata (version bumps, announcements)

### P12.2 Overleaf Gallery Submission
- Test font fallback chains on Overleaf's TeX Live 2024
- Submit to Overleaf template gallery

### P12.3 Persian/Farsi RTL Support
- Add persian as RTL language variant
- Reuse Arabic font setup with persian-specific adjustments

### P12.4 Additional Translations
- Dutch, Polish, Czech translations for common keys
- Greek, Turkish translations for common keys

### P12.5 VS Code Extension MVP
- Package existing skeleton in `extensions/vscode-omnilatex/`
- Basic functionality: doctype picker, institution switcher

### P12.6 Lean 4: Fix False Theorems
- 7 theorems retained with `sorry` are false as stated (missing non-negativity hypotheses)
- Add proper preconditions and complete proofs

**Completion criteria:** CTAN submission live, Overleaf gallery live.

---

## v2.0.0 — Ecosystem (target: 4–8 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P13.1 Rust TUI build tool** | Low | Exploratory |
| **P13.2 Additional language collections** | Low | Planned |
| **P13.3 Additional institution configs** | Low | Planned |

### P13.2 Additional Language Collections
- Enable more language collections in Docker image (French, Spanish, etc.)
- Add corresponding institution configs

---

## Priority Matrix

| Priority | Items |
|----------|-------|
| **Critical path** | P12.1 (CTAN) → P12.2 (Overleaf) |
| **High impact** | P12.1, P12.2, P12.3 |
| **Medium** | P12.4, P12.5 |
| **Long-term** | P12.6, P13.1, P13.2, P13.3 |

---

## Technical Debt

| Item | Severity | Notes |
|------|----------|-------|
| Docker image ~6 min rebuild on cache miss | Low | BuildKit cache helps; full rebuild rare |
| 13/20 Lean theorems use `sorry` | Low | No user impact; academic credibility |
| Rust TUI build tool exploratory discussion | Low | No action needed unless user drives it |
