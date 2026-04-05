# OmniLaTeX Roadmap — v1.1 through v1.4

> **Goal:** Turn excellent engineering into widespread adoption through
> distribution, discoverability, and ecosystem expansion.

**Base version:** v1.0.0 (2026-04-03)
**Last updated:** 2026-04-05

---

## Design Principles

1. **Distribution before features** — CTAN submission is the single
   highest-leverage action. Once on CTAN, OmniLaTeX ships with TeX Live
   and is installable via `tlmgr`.
2. **Show, don't tell** — PDF gallery, not README prose. Users choose
   templates based on what they see, not what they read.
3. **Lower the contribution bar** — clear guides, issue templates,
   `good-first-issue` labels, and scaffolding commands.
4. **Each version ships** — no version should be "infrastructure only."
   Every release must contain something a user can see or use.

---

## Table of Contents

1. [v1.1 — Distribution & Onboarding](#v11--distribution--onboarding)
2. [v1.2 — Ecosystem & Localization](#v12--ecosystem--localization)
3. [v1.3 — Cross-Platform & Quality](#v13--cross-platform--quality)
4. [v1.4 — Features & Polish](#v14--features--polish)
5. [v1.5+ — Future Horizons](#v15--future-horizons)
6. [Priority Matrix](#priority-matrix)
7. [Execution Summary](#execution-summary)

---

## v1.1 — Distribution & Onboarding

**Timeline:** 4–6 weeks
**Goal:** Make OmniLaTeX installable, discoverable, and approachable.

### P1.1 — CTAN Submission

**Why first:** CTAN is the TeX ecosystem's package manager. Once accepted,
OmniLaTeX is automatically included in TeX Live and MiKTeX. Users run
`tlmgr install omnilatex` and it just works.

**Action:**
- [ ] Create CTAN-ready package structure:
  ```
  omnilatex/
  ├── README.md            # CTAN README (different from GitHub README)
  ├── LICENSE              # Apache-2.0
  ├── omnilatex.cls        # Document class
  ├── lib/                 # All 21 modules
  ├── config/              # Default configs (settings, doctypes)
  ├── lua/                 # Lua scripts (git-metadata.lua)
  └── doc/
      ├── omnilatex.pdf    # User manual (required by CTAN)
      └── omnilatex.tex    # Manual source
  ```
- [ ] Write `doc/omnilatex.tex` — user manual covering all options,
      doctypes, modules, configuration, and migration from TUHH template
- [ ] Build documentation PDF
- [ ] Test `.tds.zip` installation in clean TeX Live environment
- [ ] Submit to CTAN via upload form

**CTAN Requirements Checklist:**
- [ ] README in plain text (no Markdown, no HTML)
- [ ] LICENSE file present
- [ ] Documentation PDF (`doc/omnilatex.pdf`)
- [ ] No external dependencies at install time (fonts are optional runtime deps)
- [ ] Clean `.tds.zip` respecting TDS directory structure

### P1.2 — Overleaf-Compatible Template

**Why:** Overleaf is the #1 platform for LaTeX collaboration. A one-click
template exposes OmniLaTeX to millions of users.

**Action:**
- [ ] Create `overleaf/` directory with minimal self-contained project:
  ```
  overleaf/
  ├── main.tex              # \documentclass{omnilatex}
  ├── omnilatex.cls         # Copy of root class
  ├── lib/                  # Copy of all modules
  ├── config/               # Default configs only
  ├── lua/                  # Lua scripts
  ├── bib/                  # Sample bibliography
  ├── assets/               # Sample images
  └── .latexmkrc            # Simplified for Overleaf
  ```
- [ ] Overleaf uses `latexmk -lualatex` — verify no custom flags needed
- [ ] Test on Overleaf (free tier, TeX Live 2024)
- [ ] Submit to Overleaf Gallery
- [ ] Add "Open in Overleaf" badge to README

### P1.3 — README Overhaul

**Why:** The README is the project's front door. Current issues:
- Opens with "fork from TUHH" — undersells the project
- Lists 3 of 20 examples
- References non-existent `cv-bw` (should be `cv-twopage`)
- No visual showcase
- Engineering quality (tests, proofs, 5 CI platforms) not surfaced

**Action:**
- [ ] Rewrite opening paragraph — lead with value proposition
- [ ] Add screenshot or PDF gallery (5–6 document types)
- [ ] List all 20 examples with one-line descriptions
- [ ] Fix stale reference: `cv-bw` → `cv-twopage`
- [ ] Add badges: CI status, CTAN version (after P1.1), license
- [ ] Surface unique engineering:
      - 21 modules with formal interface contracts
      - 239 test cases, 5 CI platforms
      - Byte-for-byte reproducible builds
      - Lean 4 mathematical proofs
- [ ] Improve quickstart: working 5-minute path to first PDF
- [ ] Add "Why OmniLaTeX?" section comparing to alternatives

### P1.4 — Contributing Guide

**Why:** The extensibility model (institutions, languages, doctypes) is
powerful but undocumented for contributors. A clear guide lowers the bar
for community contributions.

**Action:**
- [ ] Create `CONTRIBUTING.md` with:
  - [ ] Architecture overview (module system, option resolution, build pipeline)
  - [ ] "Adding a new institution in 30 minutes" tutorial
  - [ ] "Adding a new language in 30 minutes" tutorial
  - [ ] "Adding a new doctype" tutorial
  - [ ] Development setup (Docker / Nix / local TeX Live)
  - [ ] PR checklist (tests pass, CHANGELOG updated, no new warnings)
  - [ ] Code style conventions (LaTeX3/expl3 naming, comments)
- [ ] Ensure issue templates exist (Bug, Feature, Institution Request)
- [ ] Label strategy: `good-first-issue`, `help wanted`, `documentation`

### P1.5 — CHANGELOG CI Check

**Why:** Enforce changelog discipline so every release has a complete record.

**Action:**
- [ ] Add CI job: if PR modifies `.sty` or `.cls` files, CHANGELOG.md
      must also be modified
- [ ] Document Keep-a-Changelog format in CONTRIBUTING.md
- [ ] Add unreleased section template to CHANGELOG.md

### v1.1 Completion Criteria

- [ ] CTAN package submitted and accepted (or submission ready with all artifacts)
- [ ] Overleaf template tested and gallery submission ready
- [ ] README v2 committed with all fixes
- [ ] CONTRIBUTING.md committed with all tutorials
- [ ] CHANGELOG CI check active

---

## v1.2 — Ecosystem & Localization

**Timeline:** 6–8 weeks
**Goal:** Expand the user base through languages, institutions, and visibility.

### P2.1 — Institution Config Framework

**Why:** Only TUHH exists today. Most users need their own institution's
branding. Making this easy is the path to adoption at universities.

**Action:**
- [ ] Document `config/institutions/NAME/NAME.sty` convention in CONTRIBUTING.md
- [ ] Add `build.py scaffold-institution NAME` command:
      creates `config/institutions/NAME/` with template `.sty`,
      logo placeholder, color definitions
- [ ] Create example institution configs:
  - [ ] `generic` — minimal branding (university name, logo placeholder, colors)
  - [ ] `tum` — TU Munich (large German university)
  - [ ] `eth` — ETH Zürich (international demand)
- [ ] Add institution to integration matrix CI

### P2.2 — Language Expansion

**Why:** OmniLaTeX supports 2 languages. The polyglossia infrastructure
supports 80+. Adding 4 common languages dramatically expands the addressable
user base.

**Action:**
- [ ] Add language configs for:
  - [ ] French (`french`)
  - [ ] Spanish (`spanish`)
  - [ ] Chinese Simplified (`simplified-chinese`)
  - [ ] Japanese (`japanese`)
- [ ] For each: verify polyglossia support, add OmniLaTeX-specific strings
      (captions, TOC headings, etc.)
- [ ] Update `omnilatex-i18n.sty` with new `\setotherlanguages` entries
- [ ] Add language tests to CI matrix
- [ ] Document "Adding a new language" in CONTRIBUTING.md

### P2.3 — Template Gallery

**Why:** Users pick templates based on visual output, not feature lists.

**Action:**
- [ ] Build all 20 examples → collect PDFs
- [ ] Create `docs/gallery.md` with thumbnails or links
- [ ] Optionally deploy to GitHub Pages
- [ ] Add gallery link to README

### P2.4 — Docker Image In-Repo

**Why:** The Docker image is currently external. Having the Dockerfile in
the repo means the build environment is fully reproducible and auditable.

**Action:**
- [ ] Create `Dockerfile` in repo root:
      base `texlive/texlive:TL2024-historic` + required packages + fonts
- [ ] Pin base image by digest
- [ ] Update `.env.docker` to reference local build
- [ ] Add `docker build` step to CI for image verification
- [ ] Document in README

### v1.2 Completion Criteria

- [ ] 3+ institution configs with scaffolding command
- [ ] 6+ languages supported and tested
- [ ] Template gallery published
- [ ] Docker image buildable from repo

---

## v1.3 — Cross-Platform & Quality

**Timeline:** 4–6 weeks
**Goal:** Robust on every platform, every TeX Live version.

### P3.1 — Cross-Platform CI

**Why:** TeX Live runs on Windows and macOS. Users on those platforms need
confidence that OmniLaTeX works.

**Action:**
- [ ] Add `windows-latest` CI job:
      install TeX Live via Chocolatey, `tlmgr install` required packages
- [ ] Add `macos-latest` CI job:
      install MacTeX, `tlmgr install` required packages
- [ ] Fix `.latexmkrc` path separator:
      replace hardcoded `:` with `$Config{'path_sep'}` or `;` on Windows
- [ ] Integration matrix includes Windows + macOS for smoke tests

### P3.2 — TeX Live 2025 Compatibility

**Why:** TeX Live releases annually. Forward compatibility must be verified.

**Action:**
- [ ] Once TL 2025 is released, test in Docker (`texlive/texlive:TL2025`)
- [ ] Update Nix flake to nixpkgs with TL 2025
- [ ] Document any breaking changes
- [ ] Update minimum version in README and CTAN metadata
- [ ] Run full test suite on TL 2025

### P3.3 — Lean 4 Proof Verification

**Why:** 5 proof files exist but are tagged "VERIFICATION PENDING."
Verifying them closes the loop on the mathematical proof infrastructure.

**Action:**
- [ ] Set up Lake project configuration
- [ ] Verify all 5 proofs compile with Lean 4
- [ ] Add `checks.lean4` to `flake.nix`
- [ ] Add Lean 4 verification step to CI (Nix provides the toolchain)

### P3.4 — Editor Integration Guide

**Why:** Most users edit LaTeX in an IDE. First-class editor support
reduces friction.

**Action:**
- [ ] Create `docs/editor-integration.md` with configs for:
  - [ ] VS Code: LaTeX Workshop + build task + PDF preview
  - [ ] Vim/Neovim: VimTeX config snippet
  - [ ] Emacs: AUCTeX config snippet
- [ ] Add OmniLaTeX-specific completions for texlab (LSP)

### v1.3 Completion Criteria

- [ ] CI green on Linux, Windows, macOS
- [ ] TeX Live 2024 + 2025 compatibility documented
- [ ] All Lean 4 proofs verified in CI
- [ ] Editor integration docs for 3 editors

---

## v1.4 — Features & Polish

**Timeline:** 6–8 weeks
**Goal:** New capabilities and user experience refinements.

### P4.1 — New Doctypes

**Why:** Cover more document categories to reduce the need for alternative
templates.

**Action:**
- [ ] `poster` — conference poster (a4paper landscape, large fonts, TikZ grid)
- [ ] `presentation` — beamer-based slides (new base class `beamer`)
- [ ] `letter` — formal letter (DIN 676 / ISO standard)
- [ ] Add examples for each new doctype
- [ ] Update doctype alias table in `omnilatex.cls` and `specs/option_schema.toml`

### P4.2 — `build.py init` Command

**Why:** Starting a new document from scratch should be one command.

**Action:**
- [ ] `build.py init NAME --doctype=thesis --institution=tuhh --language=english`
- [ ] Copies minimal-starter as template, renames, fills in metadata
- [ ] `build.py scaffold-institution NAME` — creates institution config skeleton
- [ ] `build.py scaffold-language LANG` — creates language addition guide
- [ ] Interactive prompts with sensible defaults

### P4.3 — Performance Baseline

**Why:** Establish quantitative targets for build speed.

**Action:**
- [ ] Benchmark all 20 examples (cold build, incremental build)
- [ ] Establish baseline metrics in `specs/performance_baselines.toml`
- [ ] Target: cold build < 15s for simple documents (article, CV)
- [ ] Investigate Lua module caching via `luaotfload`
- [ ] Performance regression detection in CI

### P4.4 — PDF Accessibility

**Why:** Accessibility is increasingly required by institutions and law
(PDF/UA, EN 301 549).

**Action:**
- [ ] Add tagged PDF support via `tagpdf` package
- [ ] PDF/UA compliance option: `\documentclass[accessible]{omnilatex}`
- [ ] Test with screen readers (NVDA, VoiceOver)
- [ ] Document accessibility features

### v1.4 Completion Criteria

- [ ] 3 new doctypes with examples
- [ ] `build.py init` creates working project
- [ ] Performance baselines established for all examples
- [ ] Tagged PDF option available

---

## v1.5+ — Future Horizons

| Idea | Feasibility | Impact | Notes |
|------|------------|--------|-------|
| Overleaf premium template | High | High | Direct monetization, wide reach |
| Template marketplace | High | High | Community institutions, network effects |
| Beamer theme (`omnilatex-beamer`) | High | Medium | Natural extension of doctype system |
| VS Code extension | Medium | Medium | OmniLaTeX command completions |
| Web-based preview (LaTeX via WASM) | Medium | High | Overleaf competitor, significant effort |
| Memoir class support | Low | Low | KOMA-Script is sufficient |
| Citation style library | Medium | Medium | Pre-configured biblatex styles per doctype |

---

## Priority Matrix

```
Impact
  ▲
  │  P1.1 CTAN         P2.1 Institutions  P3.1 Cross-Platform  P4.1 New Doctypes
  │  P1.2 Overleaf     P2.2 Languages     P3.2 TL2025          P4.2 build.py init
  │  P1.3 README       P2.3 Gallery       P3.3 Lean4           P4.3 Performance
  │  P1.4 Contrib      P2.4 Dockerfile    P3.4 Editors         P4.4 Accessibility
  │
  └─────────────────────────────────────────────────────────────────────────────► Effort
     Low                                                            High
```

**Critical path:** v1.1 → v1.2 → v1.3 → v1.4 (sequential)
**Within v1.1:** P1.1 (CTAN) unblocks P1.2 (Overleaf); P1.3 and P1.4 are independent

---

## Execution Summary

```
v1.1 Distribution & Onboarding
  ├─ P1.1 CTAN Submission          ← highest leverage single action
  ├─ P1.2 Overleaf Template        ← millions of potential users
  ├─ P1.3 README Overhaul          ← project's front door
  ├─ P1.4 Contributing Guide       ← community growth enabler
  └─ P1.5 CHANGELOG CI Check       ← release hygiene

v1.2 Ecosystem & Localization
  ├─ P2.1 Institution Framework    ← adoption at universities
  ├─ P2.2 Language Expansion       ← international reach
  ├─ P2.3 Template Gallery         ← visual discovery
  └─ P2.4 Docker Image In-Repo     ← reproducible builds

v1.3 Cross-Platform & Quality
  ├─ P3.1 Cross-Platform CI        ← platform confidence
  ├─ P3.2 TeX Live 2025            ← forward compatibility
  ├─ P3.3 Lean 4 Verification      ← proof infrastructure closure
  └─ P3.4 Editor Integration       ← reduced friction

v1.4 Features & Polish
  ├─ P4.1 New Doctypes             ← broader document coverage
  ├─ P4.2 build.py init            ← project scaffolding
  ├─ P4.3 Performance Baseline     ← quantitative targets
  └─ P4.4 PDF Accessibility        ← institutional compliance
```
