# OmniLaTeX Formal Proof Specifications

## Overview

This directory contains Lean 4 formal verification proof sketches for core invariants of the OmniLaTeX document class system. These proofs formalize properties that are currently tested empirically (via golden tests and constraint checks) into mathematically rigorous assertions.

## Quick Start

```bash
# Build all proofs with Lake
lake build

# Build with Nix (recommended)
nix develop .# --impure --command lake build

# Check individual file
lean specs/proofs/OmniLaTeXProofs/BuildModes.lean
```

## Project Structure

```
specs/proofs/
├── lakefile.toml          # Lake build configuration
├── lean-toolchain         # Pinned Lean version
├── OmniLaTeXProofs.lean   # Root library (imports all modules)
├── OmniLaTeXProofs/       # Lake library sources
│   ├── BuildModes.lean
│   ├── DoctypeResolution.lean
│   ├── FloatInvariant.lean
│   ├── FontHierarchy.lean
│   └── PageGeometry.lean
└── README.md
```

## Proof Status

| File | Property | Theorems | Proven | Sorry |
|------|----------|----------|--------|-------|
| `BuildModes.lean` | Build mode configuration consistency | 5 | 4 | 1 |
| `DoctypeResolution.lean` | Doctype alias resolution is deterministic and total | 4 | 2 | 2 |
| `FontHierarchy.lean` | Font sizes form a strict total order | 4 | 1 | 3 |
| `PageGeometry.lean` | Page geometry satisfies balance equations | 5 | 0 | 5 |
| `FloatInvariant.lean` | Float placement respects section boundaries | 2 | 0 | 2 |
| **Total** | | **20** | **7** | **13** |

## Verified Theorems

### BuildModes.lean
- **`ultra_no_bib`** — Ultra mode never runs bibliography tools
- **`prod_validates`** — Prod mode validates datamodel and runs biber
- **`dev_enough_passes`** — Dev mode has ≥3 passes for reference resolution
- **`all_modes_shell_escape`** — All modes enable shell-escape

### DoctypeResolution.lean
- **`profile_class_consistency`** — Book-class profiles map to `scrbook`
- **`known_alias_count`** — Exactly 46 known aliases defined

### FontHierarchy.lean
- **`font_size_irreflexive`** — No font size is less than itself

## Proof Strategy

### Doctype Resolution
- **Determinism**: Pattern matching ensures each alias maps to exactly one profile. Proof by case analysis on all 46 aliases.
- **Totality**: Each alias in `knownAliases` resolves to `some` profile.

### Page Geometry
- **Balance equations**: KOMA-Script typearea enforces `textwidth + margins = paperwidth`. Requires formalizing Float arithmetic.
- **DIV formula**: `textwidth = paperwidth * (DIV-1)/DIV` is strictly between 0 and `paperwidth`.

### Font Hierarchy
- **Strict total order**: 9 font sizes satisfy irreflexivity, asymmetry, transitivity, and connexity.

### Float Invariant
- **Section boundary**: Floats with `[h]` placement appear on pages whose section ≥ defining section. Proof sketch — full formalization requires modeling LaTeX's float queue.

## Integration

These proofs complement the existing specification infrastructure:

- **Constraint files**: `specs/layout_constraints.toml`, `specs/typography_constraints.toml`
- **State machine**: `specs/document_model_state_machine.md`
- **Module contracts**: `specs/module_contracts/` (21 TOML files)
- **Golden tests**: `tests/golden/`
- **Property tests**: `tests/test_properties.py` (Hypothesis fuzzing)
