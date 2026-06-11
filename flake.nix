{
  description = "OmniLaTeX -- Modular LaTeX template system";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # TeX Live with all OmniLaTeX collections (matches Docker profile)
        # Uses scheme-medium as base, then adds required collections
        texliveEnv = pkgs.texliveMedium.withPackages (ps: with ps; [
          # Core
          collection-basic
          collection-bibtexextra
          collection-binextra
          collection-fontsextra
          collection-fontsrecommended
          collection-fontutils
          collection-formatsextra
          collection-latex
          collection-latexextra
          collection-latexrecommended
          collection-luatex
          # Tooling
          collection-pictures
          collection-plaingeneric
          collection-publishers
          # Domain-specific
          collection-mathscience
          collection-humanities
          collection-music
          # Languages
          collection-langenglish
          collection-langeuropean
          collection-langgerman
          collection-langarabic
          collection-langchinese
          collection-langcjk
          collection-langcyrillic
          collection-langjapanese
          collection-langczechslovak
          collection-langfrench
          collection-langitalian
          collection-langpolish
          collection-langspanish
          collection-langportuguese
        ]);

        # Python 3.13 with project-specific packages
        pythonEnv = pkgs.python3.withPackages (ps: [
          ps.pygments
          ps.pytest
          ps.pymupdf
          ps.pyyaml
          ps.python-dateutil
          ps.papersize
          ps.hypothesis
          ps.pytest-timeout
          ps.pytest-cov
          ps.rich
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            # TeX Live
            texliveEnv

            # Python
            pythonEnv

            # LaTeX tools
            pkgs.latexmk
            pkgs.biber

            # Version control
            pkgs.git

            # Python linters / formatters
            pkgs.black
            pkgs.isort
            pkgs.flake8
            pkgs.bandit

            # Node.js 22 for Astro web site
            pkgs.nodejs_22

            # Build system
            pkgs.gnumake
          ];

          shellHook = ''
            echo "OmniLaTeX dev shell ready"
            echo "  TeX Live: $(lualatex --version 2>/dev/null | head -1)"
            echo "  Python:  $(python3 --version)"
            echo "  Node:    $(node --version 2>/dev/null || echo 'not found')"
            echo ""
            echo "Quick start:"
            echo "  python build.py build-example minimal-starter"
            echo "  python build.py --help"
          '';
        };
      }
    );
}
