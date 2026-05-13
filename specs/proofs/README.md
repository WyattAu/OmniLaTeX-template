# OmniLaTeX Formal Proofs

Lean 4 formal verification of core invariants in the OmniLaTeX document class system.

## Toolchain

```
leanprover/lean4:v4.29.0
```

## Build

```bash
# Via Nix (recommended)
nix develop .# --impure --command lake build

# Direct Lake
lake build

# Check individual file
lean specs/proofs/OmniLaTeXProofs/BuildModes.lean
```

## Proof Status

All 154 theorems are proven. Zero `sorry` declarations remain.

| # | Module | Theorems |
|---|--------|----------|
| 1 | `BuildModes.lean` | 5 |
| 2 | `BuildModeStrictness.lean` | 20 |
| 3 | `BuildSystem.lean` | 9 |
| 4 | `BeamerProperties.lean` | 25 |
| 5 | `CrossReferenceConsistency.lean` | 26 |
| 6 | `DoctypeClassMapping.lean` | 12 |
| 7 | `DoctypePageGeometry.lean` | 12 |
| 8 | `DoctypeResolution.lean` | 4 |
| 9 | `DocumentSettings.lean` | 14 |
| 10 | `FloatInvariant.lean` | 2 |
| 11 | `FontHierarchy.lean` | 4 |
| 12 | `I18nCompleteness.lean` | 3 |
| 13 | `LanguageFallback.lean` | 6 |
| 14 | `ModuleIntegrity.lean` | 26 |
| 15 | `PageGeometry.lean` | 5 |
| 16 | `SecondaryLanguageCompleteness.lean` | 6 |
| | **Total** | **154** |

## Structure

```
specs/proofs/
  lakefile.toml
  lean-toolchain
  OmniLaTeXProofs.lean       # root library, imports all modules
  OmniLaTeXProofs/
    BuildModes.lean
    BuildModeStrictness.lean
    BuildSystem.lean
    BeamerProperties.lean
    CrossReferenceConsistency.lean
    DoctypeClassMapping.lean
    DoctypePageGeometry.lean
    DoctypeResolution.lean
    DocumentSettings.lean
    FloatInvariant.lean
    FontHierarchy.lean
    I18nCompleteness.lean
    LanguageFallback.lean
    ModuleIntegrity.lean
    PageGeometry.lean
    SecondaryLanguageCompleteness.lean
```

## Namespace Note

`BuildModes.lean` wraps all definitions and theorems inside `namespace BuildModes`. Other modules use top-level declarations directly.
