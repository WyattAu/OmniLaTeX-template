---
title: BREAKING CHANGES
---
# Breaking Changes Checklist

This checklist must be completed for any change that modifies the public API surface.

## What Constitutes a Breaking Change

- Removing or renaming a class option (e.g., `doctype` values)
- Removing or renaming a user command (anything not prefixed with `\omnilatex@` or `\@`)
- Changing the signature of a public command (required vs optional arguments)
- Removing a public environment
- Changing default values that affect document output
- Removing a module or moving functionality between modules

## Pre-Release Checklist

- [ ] All removed/renamed commands use `\omnilatexdeprecate` for at least one minor release
- [ ] CHANGELOG/vX.Y.Z.md documents the breaking change
- [ ] docs/API_STABILITY.md is updated (stability levels changed)
- [ ] All examples compile without errors
- [ ] `tests/test_properties.py` passes (doctype mapping, i18n, module integrity)
- [ ] Lean 4 proofs updated if doctype/class mapping changed
- [ ] Migration guide included in CHANGELOG entry

## Deprecation Timeline

1. **Release N**: Issue deprecation warning via `\omnilatexdeprecate`, old command still works
2. **Release N+1**: Deprecation warning continues, migration documented
3. **Release N+2**: Command may be removed at major version boundary

## Version Strategy

- Major version (X.0.0): Breaking changes allowed
- Minor version (X.Y.0): No breaking changes, deprecation warnings only
- Patch version (X.Y.Z): Bug fixes only, no API changes
