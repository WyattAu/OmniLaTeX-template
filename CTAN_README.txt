OmniLaTeX — Universal LaTeX Template System
============================================

A modular LaTeX template supporting 19+ document types with
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
---------------
  Academic:     thesis, dissertation, article, journal, homework,
                exam, research-proposal, inlinepaper
  Professional:  cv, cover-letter, letter, presentation, poster,
                technicalreport, standard, patent
  Reference:     book, manual, dictionary

Features
--------
  - 19 document type profiles with one-line switching
  - 15+ institution configurations (TUHH, TUM, ETH, MIT, ...)
  - 14 languages via polyglossia (EN, DE, FR, ES, ZH, JA, KO, AR, HE, ...)
  - CJK and RTL script support with font fallback chains
  - Color theme system with 7 built-in palettes and dark mode
  - Font setter commands for easy customization
  - Deterministic builds via Docker (multi-arch) and Nix flakes
  - Lean 4 formal verification for core algorithms

License
-------
  Apache License 2.0

Repository
----------
  https://github.com/WyattAu/OmniLaTeX-template

Documentation
-------------
  Full documentation and examples are available in the GitHub
  repository. Clone it for the complete experience:

    git clone https://github.com/WyattAu/Omnilatex-template

Homepage
--------
  https://omnilatex-template.wyattau.com/
