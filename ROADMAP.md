# OmniLaTeX Roadmap

Current version: **v1.8.0**

## Design Principles

1. **Reproducibility first** — byte-for-byte deterministic builds, pinned dependencies
2. **Modular architecture** — every feature is a `.sty` module with formal contracts
3. **Multi-language native** — polyglossia-based, not English-first with patches
4. **CI/CD as documentation** — pipelines that double as usage examples

## Project Snapshot

| Metric | Value |
|--------|-------|
| Releases | 11 (v1.0.0–v1.8.0) |
| `.sty` modules | 27 |
| Document types | 19 (thesis, dissertation, article, journal, inlinepaper, book, manual, technicalreport, standard, patent, cv, cover-letter, poster, presentation, letter, dictionary, homework, exam, research-proposal) |
| Examples | 35 (35/35 compile on Docker TL2026) |
| Institution configs | 15 |
| Languages | 14 (EN + 13 via polyglossia) |
| CI workflows | 6 (all green) |
| Lean 4 proof modules | 11 |
| Core code | ~14,000 lines |
| License | Apache 2.0 |

---

## Completed Versions

| Version | Date | Summary |
|---------|------|---------|
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

## v1.9.0 — Growth (target: 2–4 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P9.1 CTAN submission** | High | Planned |
| **P9.2 Overleaf gallery submission** | Medium | Planned |
| **P9.3 Performance optimization** | Medium | Planned |
| **P9.4 Module-level integration tests** | Medium | Planned |
| **P9.5 VS Code extension MVP** | Low | Planned |
| **P9.6 Lean 4 proof completion** | Low | Planned |

### P9.1 CTAN Submission
- Validate `scripts/make-ctan-zip.sh` output
- Submit to CTAN
- Maintain CTAN metadata (version bumps, announcements)

### P9.2 Overleaf Gallery Submission
- Create Overleaf-specific zip (no `build.py`, no Nix)
- Test font fallback chains on Overleaf's TeX Live 2024
- Submit to Overleaf template gallery

### P9.3 Performance Optimization
- Profile first-pass compilation (currently 30–131s per example)
- Evaluate fmtutil cache warming
- Explore font subsetting for faster builds

### P9.4 Module-Level Integration Tests
- Test module contracts (e.g., KOMA shim applies colors to blocks)
- Test font fallback chains (CJK, Arabic, Hebrew with missing fonts)
- Test theme switching doesn't leak state between themes

### P9.5 VS Code Extension MVP
- Package existing skeleton in `extensions/vscode-omnilatex/`
- Basic functionality: doctype picker, institution switcher
- Submit to VS Code Marketplace

### P9.6 Lean 4 Proof Completion
- 13 of 20 theorems currently use `sorry`
- Complete remaining proofs for mathematical rigor
- Zero user impact; differentiator for academic credibility

**Completion criteria:** At least one distribution channel live (CTAN or Overleaf), first-pass compile < 30s for standard examples.

---

## v2.0.0 — Ecosystem (target: 4–8 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P10.1 Rust TUI build tool** | Low | Exploratory |
| **P10.2 Additional document types** | Medium | Planned |
| **P10.3 Additional language collections** | Low | Planned |
| **P10.4 Additional institution configs** | Low | Planned |

### P10.2 Additional Document Types
- `lecture-notes` — professor note templates with theorem/proof blocks
- `syllabus` — course info, objectives, grading policies, schedule
- `handout` — compact sidebar layouts for teaching
- `memo` — TO/FROM/SUBJECT/DATE header format

### P10.3 Additional Language Collections
- Enable more language collections in Docker image (French, Spanish, etc.)
- Add corresponding institution configs

---

## Priority Matrix

| Priority | Items |
|----------|-------|
| **Critical path** | P9.1 (CTAN) → P9.2 (Overleaf) |
| **High impact** | P9.1, P9.2, P9.4 |
| **Medium** | P9.3, P10.2 |
| **Long-term** | P9.5, P9.6, P10.1, P10.3, P10.4 |

---

## Technical Debt

| Item | Severity | Notes |
|------|----------|-------|
| Docker image ~6 min rebuild on cache miss | Low | BuildKit cache helps; full rebuild rare |
| 13/20 Lean theorems use `sorry` | Low | No user impact; academic credibility |
| Rust TUI build tool exploratory discussion | Low | No action needed unless user drives it |
