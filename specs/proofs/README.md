# OmniLaTeX Formal Proof Specifications

## Overview

This directory contains Lean 4 formal verification proof sketches for core invariants of the OmniLaTeX document class system. These proofs formalize properties that are currently tested empirically (via golden tests and constraint checks) into mathematically rigorous assertions.

## Proof Files

| File | Property | Theorems | Status |
|------|----------|----------|--------|
| `doctype_resolution.lean` | Doctype alias resolution is deterministic and total | 4 | Pending |
| `page_geometry.lean` | Page geometry satisfies balance equations | 5 | Pending |
| `font_hierarchy.lean` | Font sizes form a strict total order | 4 (+1 corollary) | Partial |
| `float_invariant.lean` | Float placement respects section boundaries | 2 | Pending |
| `build_modes.lean` | Build mode configurations are consistent | 5 | Partial |

## Verification Status

**VERIFICATION PENDING** — These proofs require a Lean 4 toolchain to verify. The proof strategy is:

1. **Stated**: All theorems are formally stated with precise types.
2. **Sketched**: Key proof strategies are noted in comments.
3. **Sorry-marked**: Unproven theorems use `sorry` as placeholders.

Three theorems in `build_modes.lean` and one in `font_hierarchy.lean` have complete proofs (no `sorry`) that should verify once the Lean 4 environment is available:

- `font_size_irreflexive` — proved by case analysis
- `ultra_no_bib` — proved by `simp`
- `prod_validates` — proved by `simp`
- `dev_enough_passes` — proved by `simp` + `decide`
- `all_modes_shell_escape` — proved by case analysis + `simp`

## Proof Strategy

### Doctype Resolution (T01)
- **Determinism**: Pattern matching on the resolution function ensures each input string maps to exactly one `DocProfile` constructor. Proof by case analysis on all 46 aliases.
- **Totality**: Enumerate all elements of `knownAliases` and show each resolves to a non-none value.
- **Profile consistency**: Verify the `profileToClass` mapping partitions profiles into the three base classes correctly.

### Page Geometry (T02)
- **Balance equations**: KOMA-Script's typearea system enforces `textwidth + margins = paperwidth`. Proofs require formalizing Float arithmetic with positivity constraints on margins.
- **DIV formula**: The `textwidth = paperwidth * (DIV-1)/DIV` formula produces a value strictly between 0 and `paperwidth` when `DIV > 0`.

### Font Hierarchy (T03)
- **Strict total order**: The 9 LaTeX font sizes (`\scriptsize` through `\Huge`) are shown to satisfy irreflexivity, asymmetry, transitivity, and connexity — the four properties of a strict total order.

### Float Invariant (T04)
- **Section boundary**: Floats placed with `[h]` (here) appear on pages whose section number is at least the section where the float was defined. This is a proof sketch; full formalization requires modeling LaTeX's float queue algorithm.

### Build Modes (T05)
- **Configuration consistency**: The three build modes (`dev`, `prod`, `ultra`) produce well-typed `BuildConfig` values with predictable properties (e.g., ultra mode skips bibliography tools).

## Running the Proofs

```bash
# Install Lean 4 and Lake
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# Verify a single file (requires Lake project setup)
lean specs/proofs/doctype_resolution.lean

# Verify all proofs
lake env lean specs/proofs/*.lean
```

## Integration

These proofs complement the existing specification infrastructure:

- **Constraint files**: `specs/layout_constraints.toml`, `specs/typography_constraints.toml`
- **State machine**: `specs/document_model_state_machine.md`
- **Golden tests**: `tests/golden/`
- **Type check**: `tests/typecheck/`
