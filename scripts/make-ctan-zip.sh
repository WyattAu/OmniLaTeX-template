#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

PKG_NAME="omnilatex"
CTAN_DIR="$TMPDIR/ctan"

mkdir -p "$CTAN_DIR"

# ── Build CTAN package zip (flat tree, per CTAN guidance) ─────────────────────
# CTAN reviewer requirements:
#   1. No omnilatex.tds.zip — package is complicated enough without it
#   2. omnilatex.pdf INSIDE omnilatex/doc/
#   3. PDF source (.tex) included in omnilatex/doc/  (open source requirement)
#   4. README.md at omnilatex/README.md (top level of omnilatex directory)
#   5. Exclude test fixtures (test-univ, generic) from institutions
CTAN_PKG="$CTAN_DIR/$PKG_NAME"
mkdir -p "$CTAN_PKG"

# README + LICENSE at top level of omnilatex/ directory (CTAN requirement #4)
cp "$REPO_ROOT/README.md" "$CTAN_PKG/"
cp "$REPO_ROOT/LICENSE" "$CTAN_PKG/"

# Class file
cp "$REPO_ROOT/omnilatex.cls" "$CTAN_PKG/"

# Modules (all 31 .sty files in lib/)
cp -r "$REPO_ROOT/lib" "$CTAN_PKG/lib"

# Config: document settings + document types
mkdir -p "$CTAN_PKG/config/document-types"
cp "$REPO_ROOT/config/omnilatex-document-settings.sty" "$CTAN_PKG/config/"
cp -r "$REPO_ROOT/config/document-types/." "$CTAN_PKG/config/document-types/"

# Config: institutions (exclude test fixtures)
mkdir -p "$CTAN_PKG/config/institutions"
for dir in "$REPO_ROOT/config/institutions/"*/; do
    inst_name="$(basename "$dir")"
    case "$inst_name" in
        test-univ|generic) continue ;;  # Exclude test fixtures (CTAN requirement #5)
        *) cp -r "$dir" "$CTAN_PKG/config/institutions/$inst_name" ;;
    esac
done

# Bibliography (sample -- not runtime, placed under doc/)
mkdir -p "$CTAN_PKG/doc/bib"
if [ -f "$REPO_ROOT/bib/bibliography.bib" ]; then
    cp "$REPO_ROOT/bib/bibliography.bib" "$CTAN_PKG/doc/bib/"
fi

# Documentation: PDF + source inside omnilatex/doc/
# Prefer the full manual PDF (examples/manual/main.pdf) over the
# auto-generated sample (doc/omnilatex.pdf).  The manual is ~250 pages
# covering all features; the sample is just a short extract.
mkdir -p "$CTAN_PKG/doc"
if [ -f "$REPO_ROOT/examples/manual/main.pdf" ]; then
    cp "$REPO_ROOT/examples/manual/main.pdf" "$CTAN_PKG/doc/omnilatex-doc.pdf"
elif [ -f "$REPO_ROOT/doc/omnilatex.pdf" ]; then
    cp "$REPO_ROOT/doc/omnilatex.pdf" "$CTAN_PKG/doc/omnilatex-doc.pdf"
elif [ -f "$REPO_ROOT/main.pdf" ]; then
    cp "$REPO_ROOT/main.pdf" "$CTAN_PKG/doc/omnilatex-doc.pdf"
fi
# Include the ACTUAL documentation source (self-contained omnilatex.tex)
if [ -f "$REPO_ROOT/doc/omnilatex.tex" ]; then
    cp "$REPO_ROOT/doc/omnilatex.tex" "$CTAN_PKG/doc/omnilatex.tex"
fi

# Include the self-contained doc source (CTAN requirement for open source compliance)
if [ -f "$REPO_ROOT/doc/omnilatex.tex" ]; then
    cp "$REPO_ROOT/doc/omnilatex.tex" "$CTAN_PKG/doc/omnilatex.tex"
elif [ -f "$REPO_ROOT/main.tex" ]; then
    cp "$REPO_ROOT/main.tex" "$CTAN_PKG/doc/omnilatex.tex"
fi

# Clean build artifacts from CTAN tree (preserve doc/ directory)
find "$CTAN_PKG" -path "*/doc/*" -prune -o \
    \( -name "*.aux" -o -name "*.log" -o -name "*.pdf" \
       -o -name "*.fdb_*" -o -name "*.fls" -o -name "*.synctex.gz" \
       -o -name "__pycache__" \) \
    -exec rm -f {} + 2>/dev/null || true
find "$CTAN_PKG" -name ".git" -type d -exec rm -rf {} + 2>/dev/null || true

# Package: just the omnilatex/ directory (no TDS zip)
mkdir -p "$REPO_ROOT/ctan"
(cd "$CTAN_DIR" && zip -r "$REPO_ROOT/ctan/${PKG_NAME}.zip" "$PKG_NAME/")

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "=== CTAN Package Zip ==="
unzip -l "$REPO_ROOT/ctan/${PKG_NAME}.zip" | head -40
echo "..."
echo ""
echo "CTAN zip written to: ctan/${PKG_NAME}.zip"
echo "Structure: omnilatex/{README.md,LICENSE,omnilatex.cls,lib/,config/}"
echo "  config/document-types/omnilatex-*.sty (27 files, prefixed per CTAN reviewer)"
echo "  config/institutions/ (20 real institutions, excludes test-univ and generic)"
echo "  doc/omnilatex-doc.pdf (documentation PDF)"
echo "  doc/omnilatex.tex (self-contained source for doc PDF)"
echo "  doc/bib/bibliography.bib (sample bibliography, not runtime)"
