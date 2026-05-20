OmniLaTeX — Universal LaTeX Template System
============================================

A modular LaTeX document class supporting 27 document types with
consistent branding, multi-language support, and reproducible
builds via Docker and Nix.

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
  25 languages via polyglossia: English, German, French, Spanish,
  Portuguese, Italian, Dutch, Danish, Russian, Chinese (Simplified
  and Traditional), Japanese, Korean, Arabic, Hebrew, Persian,
  Vietnamese, Hindi, Swedish, Finnish, Norwegian, Polish, Czech,
  Greek, Turkish.

  CJK and RTL script support with automatic font fallback chains.

  18 translation languages (EN, DE, FR, ES, PT, IT, NL, PL,
  CZ, EL, TR, RU, VI, HI, SV, FI, DA, NO) for UI strings.

Features
--------
  - 26 document type profiles with one-line switching
  - 55+ doctype aliases
  - 21 institution configurations (TUHH, TUM, ETH, MIT, ...)
  - 25 languages via polyglossia (EN, DE, FR, ES, PT, IT, NL,
    DA, RU, ZH, JA, KO, AR, HE, VI, HI, SV, FI, NO, PL, CZ,
    EL, TR)
  - CJK and RTL script support with font fallback chains
  - Color theme system with 6 built-in palettes and dark mode
  - Font setter commands for easy customization
  - 9 citation styles (IEEE, ACM, APA, Chicago, Nature, Science,
    Harvard, Vancouver, MLA)
  - Deterministic builds via Docker (multi-arch) and Nix flakes
  - Lean 4 formal verification for core algorithms
  - VS Code extension with doctype picker and build commands
  - 47 example templates

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
  Full documentation, 47 example templates, and performance
  benchmarks are available in the GitHub repository:

    git clone https://github.com/WyattAu/OmniLaTeX-template.git

  Performance documentation:
    https://github.com/WyattAu/OmniLaTeX-template/blob/main/docs/PERFORMANCE.md

Homepage
--------
  https://omnilatex-template.wyattau.com/
