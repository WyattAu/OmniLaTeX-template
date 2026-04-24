# OmniLaTeX Roadmap

Current version: **v1.3.1** (2026-04-24)

## Design Principles

1. **Reproducibility first** — byte-for-byte deterministic builds, pinned dependencies
2. **Modular architecture** — every feature is a `.sty` module with formal contracts
3. **Multi-language native** — polyglossia-based, not English-first with patches
4. **CI/CD as documentation** — pipelines that double as usage examples

## v1.4 — Accuracy & Automation (target: 1–2 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P4.1 Documentation accuracy** | High | Pending |
| **P4.2 Lean 4 CI integration** | High | Pending |
| **P4.3 Docker digest automation** | Medium | Pending |
| **P4.4 TeX Live 2025 readiness** | Medium | Pending |

### P4.1 Documentation Accuracy
- Reconcile README counts (55 aliases, 24 examples, 16 profiles)
- Update Docker section for monorepo structure
- Fix stale line counts in project structure
- Update institution listing (TUHH, TUM, ETH Zürich, generic)

### P4.2 Lean 4 CI Integration
- Add CI job running `lake build` + `lake check`
- Gate on proof compilation success
- Update `flake.nix` checks

### P4.3 Docker Digest Automation
- Post-push workflow: after docker-ci.yml builds new image, auto-update digest in `build.yml` and `.env.docker`
- Prevent stale digest references

### P4.4 TeX Live 2025 Readiness
- Test Nix flake with TL2025 when released
- Rebuild Docker image with TL2025
- Full example test suite pass

**Completion criteria:** README fully accurate, Lean 4 in CI, Docker digests auto-pinned.

## v1.5 — Institutions & Themes (target: 3–4 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P5.1 New institution configs** | High | Pending |
| **P5.2 Beamer theme overhaul** | High | Pending |
| **P5.3 Color theme system** | Medium | Pending |

### P5.1 New Institution Configs
- MIT (brand colors, logo placeholder)
- Stanford (brand colors, logo placeholder)
- Cambridge (brand colors, logo placeholder)
- TU Delft (brand colors, logo placeholder)
- University template generator: `build.py scaffold-institution <name>`

### P5.2 Beamer Theme Overhaul
- Branded footers with institution logo + short title
- Progress bar / frame counter
- Custom block environments (theorem, example, alert)
- Color theme integration with institution configs
- Navigation symbols toggle

### P5.3 Color Theme System
- Formal color theme API (`\usetheme{omnilatex}` for Beamer)
- Institution-aware color switching
- Dark mode support (experimental)

**Completion criteria:** 8+ institutions, polished Beamer theme, color theme API.

## v1.6 — Language & Accessibility (target: 3–4 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P6.1 CJK full support** | High | Pending |
| **P6.2 Accessibility hardening** | Medium | Pending |
| **P6.3 RTL language support** | Medium | Pending |

### P6.1 CJK Full Support
- CJK font integration (Noto Sans CJK, Source Han)
- Vertical text mode
- Proper line breaking for CJK
- Ruby annotation support (furigana, pinyin)
- Japanese (JP), Korean (KO), Chinese (ZH) examples

### P6.2 Accessibility Hardening
- Screen reader testing with NVDA/JAWS
- Alt text for all TikZ diagrams
- Tagged PDF as default option
- WCAG 2.1 AA compliance documentation

### P6.3 RTL Language Support
- Arabic (AR), Hebrew (HE) bidi support
- Proper paragraph direction
- RTL-aware page layout

**Completion criteria:** CJK examples compile and look correct, accessibility module tested with screen readers.

## v1.7 — Ecosystem (target: 4–6 weeks)

| Project | Priority | Status |
|---------|----------|--------|
| **P7.1 Citation style library** | High | Pending |
| **P7.2 Overleaf gallery template** | Medium | Pending |
| **P7.3 VS Code extension** | Low | Pending |
| **P7.4 Template marketplace** | Low | Pending |

### P7.1 Citation Style Library
- Pre-configured biblatex styles: IEEE, ACM, Nature, Science, APA, Chicago
- `\usepackage[style=ieee]{omnilatex-citations}` convenience wrapper
- Journal-aware bibliography formatting

### P7.2 Overleaf Gallery Submission
- Overleaf-compatible zip (already have `scripts/make-overleaf-zip.sh`)
- Submit to Overleaf template gallery
- Documentation for Overleaf users

### P7.3 VS Code Extension
- OmniLaTeX command palette (doctype picker, institution switcher)
- Project initialization wizard
- Build status integration

### P7.4 Template Marketplace
- Web page: pick doctype + institution + language → download zip
- GitHub Pages hosted
- API for programmatic access

**Completion criteria:** 6+ citation styles, Overleaf submission, VS Code extension MVP.

## Priority Matrix

| Priority | Items |
|----------|-------|
| **Critical path** | P4.1 → P4.2 → P5.1 → P5.2 |
| **High impact** | P5.1, P5.2, P6.1, P7.1 |
| **Medium** | P4.3, P4.4, P5.3, P6.2, P6.3, P7.2 |
| **Long-term** | P7.3, P7.4 |

## Completed Versions

| Version | Date | Summary |
|---------|------|---------|
| v1.0.0 | 2026-04-03 | Foundation — Nix, 20 examples, build.py, CI/CD |
| v1.1.0 | 2026-04-22 | Distribution — README v2, CONTRIBUTING, CTAN/Overleaf packaging |
| v1.2.0 | 2026-04-23 | Ecosystem — TUM/ETH institutions, cross-platform CI, Lean 4, CWL |
| v1.3.0 | 2026-04-23 | Features — poster/presentation/letter, scaffold-language, perf baselines, PDF/UA-1 |
| v1.3.1 | 2026-04-24 | Housekeeping — Docker monorepo merge, cross-platform CI fix, Docker CI/CD |
