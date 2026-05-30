OmniLaTeX — Universal LaTeX Template System
============================================

A modular LaTeX document class supporting multiple document types
with consistent branding, multi-language support, and reproducible
builds via Docker and Nix.  Requires LuaLaTeX.

Installation
------------
  tlmgr install omnilatex

Quick Start
-----------
  \documentclass[doctype=thesis,language=english]{omnilatex}
  \begin{document}
    \maketitle
    \tableofcontents
    \chapter{Introduction}
    Your content here.
  \end{document}

Document Types
--------------
  Academic:     thesis, dissertation, article, journal, homework,
                exam, research-proposal, inlinepaper,
                lecture-notes, syllabus, handout, memo
  Professional:  cv, cover-letter, letter, presentation, poster,
                 technicalreport, standard, patent, invoice,
                 white-paper
  Reference:     book, manual, dictionary

Languages
---------
  Multiple languages via polyglossia: English, German, French,
  Spanish, Portuguese, Italian, Dutch, Danish, Russian, Chinese
  (Simplified and Traditional), Japanese, Korean, Arabic, Hebrew,
  Persian, Vietnamese, Hindi, Swedish, Finnish, Norwegian, Polish,
  Czech, Greek, Turkish.

  CJK and RTL script support with automatic font fallback chains.

  UI string translations for many languages (EN, DE, FR, ES, PT,
  IT, NL, PL, CZ, EL, TR, RU, VI, HI, SV, FI, DA, NO).

Features
--------
  - Multiple document type profiles with one-line switching
  - Institution configurations (TUHH, TUM, ETH, MIT, and others)
  - Multi-language support via polyglossia (CJK, RTL, Cyrillic)
  - Color theme system with built-in palettes and dark mode
  - Font setter commands for easy customization
  - Citation styles (IEEE, ACM, APA, Chicago, Nature, Science,
    Harvard, Vancouver, MLA)
  - Deterministic builds via Docker (multi-arch) and Nix flakes
  - Lean 4 formal verification for core algorithms
  - VS Code extension with doctype picker and build commands

Overleaf
--------
  An Overleaf-ready zip can be generated from any example:

    bash scripts/make-overleaf-zip.sh thesis

  Upload the resulting zip to Overleaf and set the compiler to
  LuaLaTeX. See overleaf/README.md for details.

License
-------
  Apache License 2.0

Repository
----------
  https://github.com/WyattAu/OmniLaTeX-template

Documentation
-------------
  Full documentation, example templates, and performance benchmarks
  are available in the GitHub repository:

    git clone https://github.com/WyattAu/OmniLaTeX-template.git

Homepage
--------
  https://omnilatex-template.wyattau.com/

Development
-----------
  This package was developed with assistance from AI tools for code
  generation, testing, and documentation. All code has been reviewed
  and tested by human maintainers. See the repository for details.
