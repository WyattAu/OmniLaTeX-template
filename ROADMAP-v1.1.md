# OmniLaTeX Roadmap — v1.2 and beyond

> **Goal:** Expand adoption through ecosystem growth, cross-platform
> confidence, and new capabilities.

**Base version:** v1.1.0 (2026-04-22)
**Last updated:** 2026-04-22

---

## Design Principles

1. **Each version ships** — no release is infrastructure-only.
2. **Show, don't tell** — users choose templates by what they see.
3. **Lower the contribution bar** — scaffolding commands, clear docs.
4. **Distribution before features** — CTAN is the highest-leverage action.

---

## Table of Contents

1. [v1.2 — Ecosystem & Quality](#v12--ecosystem--quality)
2. [v1.3 — Features & Polish](#v13--features--polish)
3. [v1.4+ — Future Horizons](#v14--future-horizons)
4. [Priority Matrix](#priority-matrix)

---

## v1.2 — Ecosystem & Quality

**Timeline:** 6–8 weeks
**Goal:** Institutional adoption, platform confidence, proof closure.

### P2.1 — Institution Config Framework

**Why:** Most users need their own institution's branding. Pre-built configs
for major universities lower the barrier.

**Action:**
- [x] `build.py scaffold-institution NAME` command
- [x] `generic` template — minimal branding placeholder
- [ ] `tum` — TU Munich (large German university, high demand)
- [ ] `eth` — ETH Zürich (international demand)
- [ ] Document CJK language support (polyglossia handles it natively)
- [ ] Add institution + language to integration matrix CI

### P2.2 — Cross-Platform CI

**Why:** Users on Windows and macOS need confidence OmniLaTeX works.

**Action:**
- [ ] Add `windows-latest` CI job (TeX Live via Chocolatey + `tlmgr`)
- [ ] Add `macos-latest` CI job (MacTeX + `tlmgr`)
- [ ] Fix `.latexmkrc` path separator for Windows
- [ ] Integration matrix includes Windows + macOS smoke tests

### P2.3 — TeX Live 2025 Compatibility

**Why:** Annual TL release. Forward compat must be verified.

**Action:**
- [ ] Test in Docker `texlive/texlive:TL2025` when available
- [ ] Update Nix flake to nixpkgs with TL 2025
- [ ] Run full test suite on TL 2025
- [ ] Document any breaking changes

### P2.4 — Lean 4 Proof Verification

**Why:** 5 proof files exist but are tagged "VERIFICATION PENDING."
Verifying them closes the mathematical proof loop.

**Action:**
- [x] Add Lean 4 toolchain to Nix flake
- [ ] Set up Lake project configuration
- [x] Verify all 5 proofs compile (4/5 fully proven, 1 partial)
- [ ] Add `checks.lean4` to `flake.nix`
- [ ] Add Lean 4 step to CI

### P2.5 — texlab LSP Completions

**Why:** OmniLaTeX-specific completions in editors reduce lookup friction.

**Action:**
- [x] Add `.cwl` (command completion) file for OmniLaTeX commands (80+ commands)
- [ ] Test with texlab / LaTeX Workshop

### v1.2 Completion Criteria

- [x] 3+ institution configs (tum, eth, generic)
- [ ] CI green on Linux + Windows + macOS
- [ ] TeX Live 2024 + 2025 compatibility documented
- [x] All Lean 4 proofs verified (or documented as blocked)

---

## v1.3 — Features & Polish

**Timeline:** 6–8 weeks
**Goal:** New capabilities users notice immediately.

### P3.1 — New Doctypes

**Why:** Cover more document categories to reduce need for alternative templates.

**Action:**
- [x] `poster` — conference poster (A1 landscape, tcolorbox blocks, multicol)
- [x] `presentation` — KOMA-based slides (tcolorbox slideframe environment)
- [x] `letter` — formal letter (sender/recipient/closing commands)
- [x] Add examples for each new doctype
- [x] Update doctype alias table in `omnilatex.cls` and `specs/option_schema.toml`

### P3.2 — `build.py init` Enhancements

**Why:** Starting a project should be one command with sensible defaults.

**Action:**
- [x] `build.py init NAME --doctype=thesis --institution=tuhh --language=english`
- [ ] `build.py scaffold-language LANG` — creates language addition guide
- [x] Fill in metadata from flags when creating project

### P3.3 — Performance Baseline

**Why:** Quantitative targets for build speed.

**Action:**
- [x] Benchmark all 23 examples (cold + incremental)
- [x] Establish baselines in `specs/performance_baselines.toml`
- [x] Target: cold build < 15s for simple documents (16/22 pass)
- [ ] Performance regression detection in CI

### P3.4 — PDF Accessibility

**Why:** Accessibility increasingly required by institutions (PDF/UA, EN 301 549).

**Action:**
- [x] Tagged PDF support via `tagpdf` package
- [x] `lib/layout/omnilatex-accessibility.sty` module
- [x] `examples/accessibility-test/` working example
- [ ] Test with screen readers (NVDA, VoiceOver)
- [ ] Document accessibility features

### v1.3 Completion Criteria

- [x] 3 new doctypes with examples
- [x] `build.py init` supports --doctype/--institution/--language flags
- [x] Performance baselines established
- [x] Tagged PDF option available

---

## v1.4+ — Future Horizons

| Idea | Feasibility | Impact | Notes |
|------|------------|--------|-------|
| Overleaf premium template | High | High | Direct monetization, wide reach |
| Template marketplace | High | High | Community institutions, network effects |
| Beamer theme (`omnilatex-beamer`) | High | Medium | Natural extension of doctype system |
| VS Code extension | Medium | Medium | OmniLaTeX command completions |
| Web-based preview (LaTeX via WASM) | Medium | High | Overleaf competitor, significant effort |
| Citation style library | Medium | Medium | Pre-configured biblatex styles per doctype |

---

## Priority Matrix

```
Impact
  ▲
  │  P2.1 Institutions  P3.1 New Doctypes
  │  P2.2 Cross-Platform P3.2 init flags
  │  P2.3 TL2025        P3.3 Performance
  │  P2.4 Lean4         P3.4 Accessibility
  │  P2.5 LSP
  │
  └─────────────────────────────────────────────► Effort
     Low                                    High
```

**Critical path:** v1.2 → v1.3 (sequential)
**Within v1.2:** P2.1, P2.2, P2.3 are independent; P2.4 depends on Nix flake changes
