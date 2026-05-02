#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

PKG_DIR="$TMPDIR/omnilatex"
mkdir -p "$PKG_DIR"

cp "$REPO_ROOT/omnilatex.cls" "$PKG_DIR/"

cp -r "$REPO_ROOT/lib" "$PKG_DIR/lib"

mkdir -p "$PKG_DIR/config/document-types"
cp "$REPO_ROOT/config/document-settings.sty" "$PKG_DIR/config/"
cp -r "$REPO_ROOT/config/document-types/." "$PKG_DIR/config/document-types/"

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

cd "$TMPDIR"
zip -r "$REPO_ROOT/omnilatex.zip" omnilatex/

SIZE=$(du -sh "$REPO_ROOT/omnilatex.zip" | cut -f1)
echo "Created omnilatex.zip ($SIZE)"
echo "Location: $REPO_ROOT/omnilatex.zip"
echo ""
echo "Contents:"
unzip -l "$REPO_ROOT/omnilatex.zip" | tail -5
