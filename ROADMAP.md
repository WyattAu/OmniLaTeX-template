# OmniLaTeX Roadmap

Current version: **v1.5.0** (2026-04-24)

## Design Principles

1. **Reproducibility first** — byte-for-byte deterministic builds, pinned dependencies
2. **Modular architecture** — every feature is a `.sty` module with formal contracts
3. **Multi-language native** — polyglossia-based, not English-first with patches
4. **CI/CD as documentation** — pipelines that double as usage examples

## Project Snapshot

| Metric | Value |
|--------|-------|
| Releases | 7 (v1.0.0–v1.5.0) |
| `.sty` modules | 27 |
| Examples | 31 (30 compile on TL2025) |
| Institution configs | 14 |
| Languages | 14 (EN + 13 via polyglossia) |
| CI workflows | 6 |
| Lean 4 proof modules | 8 (13/20 theorems proven) |
| Core code | ~9,350 lines |
| Docker | Multi-arch, BuildKit |

---

## v1.6.0 — Hardening (target: now)

> 6 commits since v1.5.0. Ready to tag.

| Project | Priority | Status |
|---------|----------|--------|
| **P6.1 TL2025 migration** | Critical | In Progress |
| **P6.2 Fix broken examples** | Critical | In Progress |
| **P6.3 CI/CD hardening** | High | In Progress |
| **P6.4 Code quality fixes** | Medium | In Progress |
| **P6.5 Supply chain hardening** | High | In Progress |
| **P6.6 Lean 4 stable toolchain** | Medium | In Progress |

### P6.1 TL2025 Migration
- Nix flake updated to TeX Live 2025
- Docker image rebuilt for TL2025

### P6.2 Fix Broken Examples
- 11 examples fixed to compile on TL2025

### P6.3 CI/CD Hardening
- Workflow timeouts added
- Docker digest pinning
- BuildKit version pinned

### P6.4 Code Quality Fixes
- Version bump across modules
- Deduplication pass
- Dead code cleanup

### P6.5 Supply Chain Hardening
- Font URLs pinned to specific versions
- Lean toolchain pinned
- All mutable refs replaced with immutable digests

### P6.6 Lean 4 Stable Toolchain
- Upgraded from RC to stable v4.29.0

**Completion criteria:** All examples compile on TL2025, CI passes, no mutable refs.

---

## v1.7.0 — Infrastructure & Distribution (target: 1–3 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P7.1 CI green on GitHub Actions** | Critical | Pending |
| **P7.2 Docker TL2025 image push** | High | Pending |
| **P7.3 Nix user-facing build** | Medium | Pending |
| **P7.4 CTAN submission** | Medium | Pending |
| **P7.5 Overleaf gallery submission** | Medium | Pending |
| **P7.6 VS Code extension MVP** | Low | Pending |

### P7.1 CI Green on GitHub Actions
- Validate all 6 workflows pass on GitHub Actions
- Workflows exist but have never been tested on the platform (repo was pushed directly)
- Fix any platform-specific issues (permissions, runner quirks, action versions)

### P7.2 Docker TL2025 Image Push
- Rebuild and push Docker image with TL2025 to GHCR
- Verify multi-arch manifests (linux/amd64, linux/arm64)
- Update README with new image tag

### P7.3 Nix User-Facing Build
- Add `packages.default` to `flake.nix` producing a standalone PDF
- `nix develop` already works; this adds `nix build`
- Allow users to build any example via `nix build .#example-article`

### P7.4 CTAN Submission
- Run `scripts/make-ctan-zip.sh` and validate output
- Submit to CTAN
- Ongoing maintenance for future releases

### P7.5 Overleaf Gallery Submission
- Run `scripts/make-overleaf-zip.sh` and validate output
- Submit to Overleaf template gallery
- Add Overleaf-specific documentation

### P7.6 VS Code Extension MVP
- Package existing skeleton in `extensions/vscode-omnilatex/`
- Basic functionality: doctype picker, institution switcher
- Submit to VS Code Marketplace

**Completion criteria:** All CI green, Docker image on GHCR, at least one distribution channel live (CTAN or Overleaf).

---

## v1.8.0 — Growth (target: 2–4 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P8.1 New document types** | High | Planned |
| **P8.2 Performance optimization** | Medium | Planned |
| **P8.3 Lean 4 proof completion** | Low | Planned |

### P8.1 New Document Types
- `report` — lab report template (abstract, sections, appendices, code listings)
- `exam` — exam paper template (questions, marks, answer space)
- `flyer` — event flyer template (single-page, visual)

### P8.2 Performance Optimization
- Profile first-pass compilation (currently 30–131s per example)
- Evaluate precompilation (fmtutil cache warming)
- Explore font subsetting for faster builds

### P8.3 Lean 4 Proof Completion
- 13 of 20 theorems currently use `sorry`
- Complete remaining proofs for mathematical rigor
- Zero user impact; differentiator for academic credibility

**Completion criteria:** 3 new document types, first-pass compile < 30s for standard examples.

---

## Priority Matrix

| Priority | Items |
|----------|-------|
| **Critical path** | P7.1 (CI green) → P7.2 (Docker push) → P7.4/P7.5 (distribution) |
| **High impact** | P7.1, P7.2, P8.1 |
| **Medium** | P6.3–P6.5, P7.3–P7.5, P8.2 |
| **Long-term** | P7.6, P8.3 |

## Completed Versions

| Version | Date | Summary |
|---------|------|---------|
| v1.0.0 | 2026-04-03 | Foundation — Nix, 20 examples, build.py, CI/CD |
| v1.1.0 | 2026-04-22 | Distribution — README v2, CONTRIBUTING, CTAN/Overleaf packaging |
| v1.2.0 | 2026-04-23 | Ecosystem — TUM/ETH institutions, cross-platform CI, Lean 4, CWL |
| v1.3.0 | 2026-04-23 | Features — poster/presentation/letter, scaffold-language, perf baselines, PDF/UA-1 |
| v1.3.1 | 2026-04-24 | Housekeeping — Docker monorepo merge, cross-platform CI fix, Docker CI/CD |
| v1.4.0 | 2026-04-24 | Accuracy — documentation reconciliation, Lean 4 CI, Docker digests |
| v1.5.0 | 2026-04-24 | Institutions — 14 configs, Beamer overhaul, color theme system |
