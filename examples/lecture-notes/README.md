# Lecture Notes

Graph theory lecture notes with formal definitions, theorems, proofs, and worked examples.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example lecture-notes

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | lecture-notes | Lecture notes doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `definition` environment
- `theorem` environment with optional labels
- `lemma` and `corollary` environments
- `proof` environment with proof sketches
- `example` environment for worked problems
- `remark` environment for supplementary commentary
- Display mathematics (summations, set notation)

## Notes

The lecture-notes doctype provides theorem-like environments. This example covers introductory graph theory including the Handshaking Lemma, tree properties, and Euler's formula.
