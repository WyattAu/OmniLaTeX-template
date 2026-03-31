#!/usr/bin/env bash
# Download custom fonts for OmniLaTeX local builds.
# Requires: curl, unzip
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Downloading fonts to: $SCRIPT_DIR"

# --- Monaspace Neon ---
echo ""
echo "=== Monaspace Neon ==="
echo "Manual download required from: https://github.com/chriskapp/neon-monospace"
echo "Copy OTF files to: $SCRIPT_DIR/"
echo "  Required: MonaspaceNeon-Regular.otf, MonaspaceNeon-Bold.otf"
echo "            MonaspaceNeon-Italic.otf, MonaspaceNeon-BoldItalic.otf"

# --- Atkinson Hyperlegible Next ---
echo ""
echo "=== Atkinson Hyperlegible Next ==="
echo "Manual download required from: https://github.com/BrailleInstitute/Atkinson-Hyperlegible-Next-Font"
echo "Copy OTF files to: $SCRIPT_DIR/"
echo "  Required: AtkinsonHyperlegibleNext-Regular.otf, AtkinsonHyperlegibleNext-Bold.otf"
echo "            AtkinsonHyperlegibleNext-Italic.otf, AtkinsonHyperlegibleNext-BoldItalic.otf"

echo ""
echo "Done. Place the font files in $SCRIPT_DIR/ and rebuild."
