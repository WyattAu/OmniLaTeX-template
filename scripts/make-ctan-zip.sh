#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

PKG_NAME="omnilatex"
PKG_DIR="$TMPDIR/$PKG_NAME"
TDS_DIR="$TMPDIR/tds"
CTAN_DIR="$TMPDIR/ctan"

mkdir -p "$CTAN_DIR"
mkdir -p "$TDS_DIR"/{tex/latex/$PKG_NAME,doc/latex/$PKG_NAME,source/latex/$PKG_NAME}

# ── TDS: tex/latex/omnilatex/ ────────────────────────────────────────────────
cp "$REPO_ROOT/omnilatex.cls" "$TDS_DIR/tex/latex/$PKG_NAME/"
cp -r "$REPO_ROOT/lib" "$TDS_DIR/tex/latex/$PKG_NAME/lib"

mkdir -p "$TDS_DIR/tex/latex/$PKG_NAME/config/document-types"
mkdir -p "$TDS_DIR/tex/latex/$PKG_NAME/config/institutions"
cp "$REPO_ROOT/config/omnilatex-document-settings.sty" "$TDS_DIR/tex/latex/$PKG_NAME/config/"
cp -r "$REPO_ROOT/config/document-types/." "$TDS_DIR/tex/latex/$PKG_NAME/config/document-types/"
cp -r "$REPO_ROOT/config/institutions/." "$TDS_DIR/tex/latex/$PKG_NAME/config/institutions/"

# ── TDS: source/latex/omnilatex/ ────────────────────────────────────────────
cp "$REPO_ROOT/omnilatex.cls" "$TDS_DIR/source/latex/$PKG_NAME/omnilatex.tex"

# ── TDS: doc/latex/omnilatex/ ────────────────────────────────────────────────
cp "$REPO_ROOT/CTAN_README.txt" "$TDS_DIR/doc/latex/$PKG_NAME/README"
cp "$REPO_ROOT/LICENSE" "$TDS_DIR/doc/latex/$PKG_NAME/"
cp "$REPO_ROOT/CHANGELOG.md" "$TDS_DIR/doc/latex/$PKG_NAME/"
cp "$REPO_ROOT/VERSION.md" "$TDS_DIR/doc/latex/$PKG_NAME/"

if [ -f "$REPO_ROOT/main.pdf" ]; then
    cp "$REPO_ROOT/main.pdf" "$TDS_DIR/doc/latex/$PKG_NAME/${PKG_NAME}.pdf"
elif [ -f "$REPO_ROOT/doc/omnilatex.pdf" ]; then
    cp "$REPO_ROOT/doc/omnilatex.pdf" "$TDS_DIR/doc/latex/$PKG_NAME/${PKG_NAME}.pdf"
fi

# ── Clean build artifacts from TDS ───────────────────────────────────────────
find "$TDS_DIR" -name "*.aux" -o -name "*.log" -o -name "*.pdf" \
    -o -name "*.fdb_*" -o -name "*.fls" -o -name "*.synctex.gz" \
    -o -name "__pycache__" -o -name ".git" -type d \
    -exec rm -rf {} + 2>/dev/null || true

# ── Build TDS zip ────────────────────────────────────────────────────────────
mkdir -p "$REPO_ROOT/ctan"
(cd "$TDS_DIR" && zip -r "$REPO_ROOT/ctan/${PKG_NAME}.tds.zip" .)

# ── Build CTAN package zip (TDS + flat tree) ──────────────────────────────────
CTAN_PKG="$CTAN_DIR/$PKG_NAME"
mkdir -p "$CTAN_PKG"

# Flat tree: all installable files under omnilatex/
cp "$REPO_ROOT/omnilatex.cls" "$CTAN_PKG/"
cp -r "$REPO_ROOT/lib" "$CTAN_PKG/lib"

mkdir -p "$CTAN_PKG/config/document-types"
mkdir -p "$CTAN_PKG/config/institutions"
cp "$REPO_ROOT/config/omnilatex-document-settings.sty" "$CTAN_PKG/config/"
cp -r "$REPO_ROOT/config/document-types/." "$CTAN_PKG/config/document-types/"
cp -r "$REPO_ROOT/config/institutions/." "$CTAN_PKG/config/institutions/"

mkdir -p "$CTAN_PKG/bib"
if [ -f "$REPO_ROOT/bib/bibliography.bib" ]; then
    cp "$REPO_ROOT/bib/bibliography.bib" "$CTAN_PKG/bib/"
fi

# README + LICENSE at top level inside CTAN zip (not inside omnilatex/)
cp "$REPO_ROOT/CTAN_README.txt" "$CTAN_DIR/README"
cp "$REPO_ROOT/LICENSE" "$CTAN_DIR/"

# TDS zip goes alongside the flat tree
TDS_ZIP="$REPO_ROOT/ctan/${PKG_NAME}.tds.zip"
cp "$TDS_ZIP" "$CTAN_DIR/"

# Documentation PDF
DOC_PDF=""
if [ -f "$TDS_DIR/doc/latex/$PKG_NAME/${PKG_NAME}.pdf" ]; then
    cp "$TDS_DIR/doc/latex/$PKG_NAME/${PKG_NAME}.pdf" "$CTAN_DIR/"
    DOC_PDF="${PKG_NAME}.pdf"
fi

# Clean build artifacts from flat tree
find "$CTAN_PKG" -name "*.aux" -o -name "*.log" -o -name "*.pdf" \
    -o -name "*.fdb_*" -o -name "*.fls" -o -name "*.synctex.gz" \
    -o -name "__pycache__" -o -name ".git" -type d \
    -exec rm -rf {} + 2>/dev/null || true

CTAN_FILES="README LICENSE $PKG_NAME ${PKG_NAME}.tds.zip"
[ -n "$DOC_PDF" ] && CTAN_FILES="$CTAN_FILES $DOC_PDF"
(cd "$CTAN_DIR" && zip -r "$REPO_ROOT/ctan/${PKG_NAME}.zip" $CTAN_FILES)

# ── Also build simple flat zip (for non-TDS distribution) ────────────────────
mkdir -p "$PKG_DIR"
cp "$REPO_ROOT/omnilatex.cls" "$PKG_DIR/"
cp -r "$REPO_ROOT/lib" "$PKG_DIR/lib"

mkdir -p "$PKG_DIR/config/document-types"
mkdir -p "$PKG_DIR/config/institutions"
cp "$REPO_ROOT/config/omnilatex-document-settings.sty" "$PKG_DIR/config/"
cp -r "$REPO_ROOT/config/document-types/." "$PKG_DIR/config/document-types/"
cp -r "$REPO_ROOT/config/institutions/." "$PKG_DIR/config/institutions/"

mkdir -p "$PKG_DIR/bib"
cp "$REPO_ROOT/bib/bibliography.bib" "$PKG_DIR/bib/"

cp "$REPO_ROOT/README.md" "$PKG_DIR/"
cp "$REPO_ROOT/LICENSE" "$PKG_DIR/"
cp "$REPO_ROOT/CHANGELOG.md" "$PKG_DIR/"
cp "$REPO_ROOT/VERSION.md" "$PKG_DIR/"

find "$PKG_DIR" -name "*.aux" -o -name "*.log" -o -name "*.pdf" \
    -o -name "*.fdb_*" -o -name "*.fls" -o -name "*.synctex.gz" \
    -o -name "__pycache__" -o -name ".git" -type d \
    -exec rm -rf {} + 2>/dev/null || true

(cd "$TMPDIR" && zip -r "$REPO_ROOT/${PKG_NAME}.zip" "$PKG_NAME/")

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo "=== CTAN Package Zip ==="
unzip -l "$REPO_ROOT/ctan/${PKG_NAME}.zip"
echo ""
echo "=== TDS Zip ==="
unzip -l "$REPO_ROOT/ctan/${PKG_NAME}.tds.zip" | tail -5
echo ""
echo "=== Flat Distribution Zip ==="
unzip -l "$REPO_ROOT/${PKG_NAME}.zip" | tail -5
