# OmniLaTeX Roadmap

Current version: **v1.7.1**

## Design Principles

1. **Reproducibility first** — byte-for-byte deterministic builds, pinned dependencies
2. **Modular architecture** — every feature is a `.sty` module with formal contracts
3. **Multi-language native** — polyglossia-based, not English-first with patches
4. **CI/CD as documentation** — pipelines that double as usage examples

## Project Snapshot

| Metric | Value |
|--------|-------|
| Releases | 10 (v1.0.0–v1.7.1) |
| `.sty` modules | 27 |
| Examples | 31 (31/31 compile on Nix TL2025, 31/31 on Docker TL2026) |
| Institution configs | 15 |
| Languages | 14 (EN + 13 via polyglossia) |
| CI workflows | 6 (all green) |
| Lean 4 proof modules | 8 (13/20 theorems use `sorry`) |
| Core code | ~9,350 lines |

---

## Completed Versions

| Version | Date | Summary |
|---------|------|---------|
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

## v1.8.0 — Polish & Distribution (target: 1–2 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P8.1 CTAN submission** | High | Planned |
| **P8.2 Overleaf gallery submission** | High | Planned |
| **P8.3 Performance optimization** | Medium | Planned |
| **P8.4 Module-level integration tests** | Medium | Planned |
| **P8.5 New document types** | Medium | Planned |

### P8.1 CTAN Submission
- Run `scripts/make-ctan-zip.sh` and validate output
- Ensure all documentation is CTAN-compliant
- Submit and maintain

### P8.2 Overleaf Gallery Submission
- Run `scripts/make-overleaf-zip.sh` and validate output
- Add Overleaf-specific documentation (no `build.py`, no Nix)
- Submit to Overleaf template gallery

### P8.3 Performance Optimization
- Profile first-pass compilation (currently 30–131s per example)
- Evaluate precompilation (fmtutil cache warming)
- Explore font subsetting for faster builds

### P8.4 Module-Level Integration Tests
- Test module contracts (e.g., KOMA shim applies colors to TOC)
- Test font fallback chains (CJK, Arabic, Hebrew with missing fonts)
- Test theme switching doesn't leak state between themes

### P8.5 New Document Types
- `report` — lab report template (abstract, sections, appendices, code listings)
- `exam` — exam paper template (questions, marks, answer space)
- `flyer` — event flyer template (single-page, visual)

**Completion criteria:** At least one distribution channel live (CTAN or Overleaf), first-pass compile < 30s for standard examples.

---

## v1.9.0 — Growth (target: 2–4 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P9.1 VS Code extension MVP** | Medium | Planned |
| **P9.2 Lean 4 proof completion** | Low | Planned |
| **P9.3 Additional language collections** | Low | Planned |

### P9.1 VS Code Extension MVP
- Package existing skeleton in `extensions/vscode-omnilatex/`
- Basic functionality: doctype picker, institution switcher
- Submit to VS Code Marketplace

### P9.2 Lean 4 Proof Completion
- 13 of 20 theorems currently use `sorry`
- Complete remaining proofs for mathematical rigor
- Zero user impact; differentiator for academic credibility

### P9.3 Additional Language Collections
- Enable more language collections in Docker image (French, Spanish, etc.)
- Add corresponding institution configs

**Completion criteria:** VS Code extension published, Lean proofs complete.

---

## Priority Matrix

| Priority | Items |
|----------|-------|
| **Critical path** | P8.1 (CTAN) / P8.2 (Overleaf) → P8.5 (new types) |
| **High impact** | P8.1, P8.2, P8.4 |
| **Medium** | P8.3, P8.5, P9.1 |
| **Long-term** | P9.2, P9.3 |

---

## Technical Debt

| Item | Severity | Notes |
|------|----------|-------|
| `build.py` `CommandRunner.run()` only catches `FileNotFoundError` | Low | Should also catch `PermissionError`, `OSError` |
| Docker image ~6 min rebuild on cache miss | Low | BuildKit cache helps; full rebuild rare |
| 13/20 Lean theorems use `sorry` | Low | No user impact; academic credibility |
