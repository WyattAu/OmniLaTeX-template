#!/usr/bin/env bash
# Build a CTAN-ready .tds.zip from the OmniLaTeX repository.
#
# Usage:
#   bash scripts/make-ctan-zip.sh
#
# Produces:
#   ctan/omnilatex.tds.zip       — TDS-compliant zip for CTAN upload
#   ctan/omnilatex.zip          — CTAN upload package (README + tds.zip)
#
# TDS structure:
#   tex/latex/omnilatex/         — .cls and .sty files
#   doc/latex/omnilatex/         — documentation
#   source/latex/omnilatex/      — documentation sources

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CTAN_DIR="$REPO_ROOT/ctan"
TMPDIR="$(mktemp -d)"

trap 'rm -rf "$TMPDIR"' EXIT

echo "Building CTAN package..."

# ── TDS structure ────────────────────────────────────
TDS="$TMPDIR/tds"
mkdir -p "$TDS/tex/latex/omnilatex"
mkdir -p "$TDS/doc/latex/omnilatex"
mkdir -p "$TDS/source/latex/omnilatex"

# tex/ — class + modules
cp "$REPO_ROOT/omnilatex.cls" "$TDS/tex/latex/omnilatex/"

# Modules: preserve lib/ structure as tex/latex/omnilatex/lib/
cp -r "$REPO_ROOT/lib" "$TDS/tex/latex/omnilatex/"

# Lua scripts
mkdir -p "$TDS/tex/latex/omnilatex/lua"
cp "$REPO_ROOT/lua/"*.lua "$TDS/tex/latex/omnilatex/lua/" 2>/dev/null || true

# Config: document types and settings
mkdir -p "$TDS/tex/latex/omnilatex/config/document-types"
cp "$REPO_ROOT/config/document-settings.sty" "$TDS/tex/latex/omnilatex/config/" 2>/dev/null || true
cp -r "$REPO_ROOT/config/document-types/"*.sty "$TDS/tex/latex/omnilatex/config/document-types/" 2>/dev/null || true

# doc/ — README + LICENSE + documentation PDF
cp "$REPO_ROOT/LICENSE" "$TDS/doc/latex/omnilatex/"
cp "$REPO_ROOT/CHANGELOG.md" "$TDS/doc/latex/omnilatex/"

# CTAN requires a plain-text README (not Markdown)
if [ -f "$REPO_ROOT/doc/ctan-README" ]; then
  cp "$REPO_ROOT/doc/ctan-README" "$TDS/doc/latex/omnilatex/README"
else
  # Auto-generate plain text README from first section of GitHub README
  sed -n '1,/^## /p' "$REPO_ROOT/README.md" \
    | grep -v '^#' \
    | grep -v '^\[' \
    | grep -v '^|' \
    | grep -v '^$' \
    | head -20 \
    > "$TDS/doc/latex/omnilatex/README"
  echo "" >> "$TDS/doc/latex/omnilatex/README"
  echo "Installation: tlmgr install omnilatex" >> "$TDS/doc/latex/omnilatex/README"
  echo "Documentation: https://github.com/WyattAu/OmniLaTeX-template" >> "$TDS/doc/latex/omnilatex/README"
  echo "License: Apache-2.0" >> "$TDS/doc/latex/omnilatex/README"
fi

# Documentation PDF (if built)
if [ -f "$REPO_ROOT/doc/omnilatex.pdf" ]; then
  cp "$REPO_ROOT/doc/omnilatex.pdf" "$TDS/doc/latex/omnilatex/"
fi

# source/ — documentation source
if [ -f "$REPO_ROOT/doc/omnilatex.tex" ]; then
  cp "$REPO_ROOT/doc/omnilatex.tex" "$TDS/source/latex/omnilatex/"
fi

# ── Create TDS zip ──────────────────────────────────
mkdir -p "$CTAN_DIR"
(cd "$TDS" && zip -r "$CTAN_DIR/omnilatex.tds.zip" .)
TDS_SIZE=$(du -h "$CTAN_DIR/omnilatex.tds.zip" | cut -f1)
echo "✓ TDS zip: ctan/omnilatex.tds.zip ($TDS_SIZE)"

# ── Create upload zip ───────────────────────────────
UPLOAD="$TMPDIR/upload"
mkdir -p "$UPLOAD"

# CTAN upload zip contains: README at root + tds.zip
cp "$TDS/doc/latex/omnilatex/README" "$UPLOAD/README"
cp "$REPO_ROOT/LICENSE" "$UPLOAD/LICENSE"
cp "$CTAN_DIR/omnilatex.tds.zip" "$UPLOAD/"

# Documentation PDF at root (CTAN convention)
if [ -f "$REPO_ROOT/doc/omnilatex.pdf" ]; then
  cp "$REPO_ROOT/doc/omnilatex.pdf" "$UPLOAD/omnilatex.pdf"
fi

(cd "$UPLOAD" && zip -r "$CTAN_DIR/omnilatex.zip" .)
UPLOAD_SIZE=$(du -h "$CTAN_DIR/omnilatex.zip" | cut -f1)
echo "✓ Upload zip: ctan/omnilatex.zip ($UPLOAD_SIZE)"

echo ""
echo "To submit to CTAN:"
echo "  1. Build documentation: cd doc && latexmk -lualatex omnilatex.tex"
echo "  2. Upload ctan/omnilatex.zip to https://ctan.org/upload"
echo ""
echo "TDS structure:"
find "$TDS" -type f | sort | sed "s|$TDS/||"
