# OmniLaTeX Bundled Fonts

This directory contains custom fonts bundled with OmniLaTeX for portable builds.

## Required Fonts

### Monaspace Neon (Monospace)
- **Source:** https://github.com/chriskapp/neon-monospace
- **Files needed:** `MonaspaceNeon-Regular.otf`, `MonaspaceNeon-Bold.otf`, `MonaspaceNeon-Italic.otf`, `MonaspaceNeon-BoldItalic.otf`
- **Download:** Clone the repo and copy the OTF files from the `fonts/otf/` directory
- **Fallback (if missing):** Latin Modern Mono

### Atkinson Hyperlegible Next (Sans-serif)
- **Source:** https://github.com/BrailleInstitute/Atkinson-Hyperlegible-Next-Font
- **Files needed:** `AtkinsonHyperlegibleNext-Regular.otf`, `AtkinsonHyperlegibleNext-Bold.otf`, `AtkinsonHyperlegibleNext-Italic.otf`, `AtkinsonHyperlegibleNext-BoldItalic.otf`
- **Download:** Download from the Braille Institute GitHub releases
- **Fallback (if missing):** Libertinus Sans

## Setup

Run the included download script:
```
./assets/fonts/download.sh
```

Or manually download and place the OTF/TTF files in this directory.

## Note

These fonts are NOT in TeX Live. The OmniLaTeX build system (`omnilatex-fonts.sty`) will:
1. First try to load fonts from this `assets/fonts/` directory
2. Fall back to system-installed fonts
3. Fall back to TeX Live bundled fonts with a warning

The Docker image (`ghcr.io/wyattau/omnilatex-docker`) already includes these fonts.
