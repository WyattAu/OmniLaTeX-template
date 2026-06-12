#!/bin/bash
# Build self-contained Overleaf Gallery showcase zips.
# Each zip contains omnilatex.cls, lib/, bib/, and the example files
# with paths adjusted for Overleaf's flat structure.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="$REPO_ROOT/.overleaf-gallery"
mkdir -p "$OUT_DIR"

# 5 showcase templates
SHOWCASES=(
    "thesis:OmniLaTeX Thesis Template:Academic thesis with chapters, bibliography, and front matter"
    "article:OmniLaTeX Article Template:Standard academic article with sections and references"
    "beamer-academic:OmniLaTeX Beamer Template:Academic presentation slides with sections"
    "cv:OmniLaTeX CV Template:Curriculum vitae with sections for experience, education, skills"
    "technical-report:OmniLaTeX Technical Report Template:Technical report with numbered sections"
)

for entry in "${SHOWCASES[@]}"; do
    IFS=':' read -r name title description <<< "$entry"
    example_dir="$REPO_ROOT/examples/$name"

    if [[ ! -d "$example_dir" ]]; then
        echo "SKIP: $name (directory not found)"
        continue
    fi

    zip_name="omnilatex-${name}.zip"
    tmp_dir=$(mktemp -d)
    trap "rm -rf $tmp_dir" EXIT

    echo "Building $zip_name..."

    # Copy example files
    cp "$example_dir/main.tex" "$tmp_dir/"

    # Copy config directory if it exists
    if [[ -d "$example_dir/config" ]]; then
        cp -r "$example_dir/config" "$tmp_dir/"
    fi

    # Copy .cls and lib/ at root level
    cp "$REPO_ROOT/omnilatex.cls" "$tmp_dir/"
    cp -r "$REPO_ROOT/lib" "$tmp_dir/"

    # Copy bib/ directory
    mkdir -p "$tmp_dir/bib"
    cp "$REPO_ROOT/bib/bibliography.bib" "$tmp_dir/bib/"

    # Fix paths in main.tex: ../../omnilatex -> omnilatex, ../../bib/ -> bib/
    sed -i 's|{../../omnilatex}|{omnilatex}|g' "$tmp_dir/main.tex"
    sed -i 's|{../../bib/|{bib/|g' "$tmp_dir/main.tex"

    # Copy any .bib files from example config
    if [[ -d "$example_dir/config" ]]; then
        for bib in "$example_dir/config/"*.bib; do
            [[ -f "$bib" ]] && cp "$bib" "$tmp_dir/bib/"
        done
    fi

    # Create zip
    (cd "$tmp_dir" && zip -r "$OUT_DIR/$zip_name" . -x '*.aux' '*.log' '*.out' '*.toc' '*.lof' '*.lot' '*.bbl' '*.blg' '*.fls' '*.fdb_latexmk' '*.synctex.gz')

    rm -rf "$tmp_dir"
    trap - EXIT
    echo "  -> $OUT_DIR/$zip_name"
done

echo ""
echo "Showcase zips created in $OUT_DIR/"
ls -lh "$OUT_DIR/"*.zip 2>/dev/null || echo "(no zips found)"
