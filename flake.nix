{
  description = "OmniLaTeX — Modular LaTeX template system";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # scheme-medium (~1 GB) + explicit packages replaces scheme-full (~4 GB).
        # Packages already included in scheme-medium are harmlessly deduplicated
        # by texlive.combine.  The list below was extracted from every
        # \usepackage / \RequirePackage call in lib/*.sty and omnilatex.cls.
        #
        # Not listed here because they are already in scheme-medium:
        #   expl3, multicol, scrlayer-scrpage, xparse, array, subcaption,
        #   graphicx, pgfplotstable, longtable, flafter, shellesc, ifthen
        #
        # Bundled with their parent packages in nixpkgs:
        #   amssymb → amsfonts, empheq → mathtools, pgfplotstable → pgfplots,
        #   subcaption → caption, glossary-{longextra,bookindex,mcols} → glossaries-extra
        texlive = pkgs.texlive.combine {
          inherit (pkgs.texlive)
            scheme-medium
            # ── Collections for packages not available as standalone attrs ──
            collection-fontsextra     # amssymb, fix-cm, libertinus, extra fonts
            collection-latexextra     # extdash, nicefrac, suffix, todonotes extras
            # ── Core (omnilatex.cls) ──
            iftex
            etoolbox
            kvoptions
            setspace
            adjustbox
            xkeyval
            # ── lib/core/omnilatex-base ──
            import
            nth
            xstring
            datetime2
            # ── lib/utils/* ──
            xcolor
            todonotes
            hologo
            censor
            cancel
            # ── lib/typography/omnilatex-fonts ──
            fontspec
            amsmath
            amsfonts
            lualatex-math
            fontawesome5
            unicode-math
            # ── lib/typography/omnilatex-typesetting ──
            microtype
            ragged2e
            blindtext
            pdflscape
            url
            # ── lib/typography/omnilatex-lists ──
            enumitem
            # ── lib/typography/omnilatex-math ──
            mathtools
            chemmacros
            siunitx
            eurosym
            xfrac
            # ── lib/layout/* ──
            caption
            tcolorbox
            # ── lib/graphics/* ──
            svg
            scalerel
            contour
            pgfplots
            tikz-3dplot
            circuitikz
            # ── lib/code/omnilatex-listings ──
            minted
            accsupp
            fvextra
            # ── lib/tables/omnilatex-tables ──
            multirow
            booktabs
            tabularray
            # ── lib/references/* ──
            hyperref
            bookmark
            glossaries-extra          # includes glossary-{longextra,bookindex,mcols}
            biblatex-ext              # ext-authoryear, ext-numeric, etc.
            biber                     # bibliography processor
            bib2gls
            # ── lib/language/omnilatex-i18n ──
            polyglossia
            translations
            tracklang
            luatexja
            haranoaji
            luabidi
            bidi
            tagpdf
            setspaceenhanced
          ;
        };

         pythonEnv = pkgs.python3.withPackages (ps: with ps; [
           pygments
           pytest
           pytest-timeout
           hypothesis
           pyyaml
           python-dateutil
           tqdm
           rich
          # NOTE: papersize is not in nixpkgs. test_pdfs.py (which depends on it)
          # is automatically skipped when pymupdf/fitz is unavailable.
        ]);

        # NOTE: Custom fonts (Monaspace Neon, Atkinson Hyperlegible Next) are
        # not available in nixpkgs. Users needing these fonts should either:
        #   1. Install them system-wide and use NIX_FONTS or fontconfig overrides
        #   2. Use the Docker image which bundles them
        # Libertinus is in collection-fontsextra; Font Awesome 5 via fontawesome5 above.
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            texlive
            pythonEnv
            pkgs.gnumake
            pkgs.inkscape
            pkgs.gnuplot
            pkgs.lean4
          ];

          shellHook = ''
            echo "OmniLaTeX development environment"
            echo "TeX Live: $(tex --version | head -1)"
            echo "Python: $(python3 --version)"
            echo "Lean 4: $(lean --version 2>/dev/null | head -1 || echo 'not found')"
          '';
        };

        packages.default = pkgs.stdenvNoCC.mkDerivation {
          name = "omnilatex-example";
          src = ./.;

          nativeBuildInputs = [ texlive pythonEnv ];

          buildPhase = ''
            export HOME=$(mktemp -d)
            export SOURCE_DATE_EPOCH=1700000000
            export TEXINPUTS=$PWD/:
            cd examples/thesis
            ln -sf ../../.latexmkrc .
            latexmk -lualatex -interaction=nonstopmode main.tex
          '';

          installPhase = ''
            mkdir -p $out
            cp main.pdf $out/omnilatex-example.pdf
          '';
        };

        checks.reproducibility = pkgs.stdenvNoCC.mkDerivation {
          name = "omnilatex-reproducibility-check";
          src = ./.;

          nativeBuildInputs = [ texlive pythonEnv ];

          buildPhase = ''
            export SOURCE_DATE_EPOCH=1700000000
            export TEXINPUTS=$PWD/:
            cd examples/thesis
            ln -sf ../../.latexmkrc .

            # Build 1: in-place
            export HOME=$(mktemp -d)
            latexmk -lualatex -interaction=nonstopmode main.tex
            hash1=$(sha256sum main.pdf | cut -d' ' -f1)
            cp main.pdf $TMPDIR/build1.pdf

            # Clean all generated files
            latexmk -C
            # Also remove any leftover files latexmk -C might miss
            rm -f main.bbl main.run.xml main-blx.bib main.fls main.fdb_latexmk main.acn main.acr main.aux main.glo main.ist main.log main.out main.toc main.loe main.xdv main.bcf main.glg main.glstex main.run tcache/

            # Build 2: in-place (same environment, fresh HOME)
            export HOME=$(mktemp -d)
            latexmk -lualatex -interaction=nonstopmode main.tex
            hash2=$(sha256sum main.pdf | cut -d' ' -f1)

            echo "Build 1 hash: $hash1"
            echo "Build 2 hash: $hash2"

            if [ "$hash1" != "$hash2" ]; then
              echo "FAIL: Reproducibility check failed — hashes differ"
              exit 1
            fi
            echo "PASS: Reproducibility check passed — hashes match"
          '';

          installPhase = "mkdir $out";
        };

        checks.formatting = pkgs.runCommand "check-formatting" {
          nativeBuildInputs = [ pkgs.python3 ];
          src = ./.;
        } ''
          # Compile to /dev/null to avoid writing __pycache__ in read-only /nix/store
          python3 -c "
import py_compile, tempfile, shutil
tmpdir = tempfile.mkdtemp()
try:
    py_compile.compile('$src/build.py', cfile=tmpdir + '/build.pyc', doraise=True)
finally:
    shutil.rmtree(tmpdir)
"
          echo "PASS: Python syntax check"
          mkdir $out
        '';
      }
    ) // {
      # Overlays must be functions (not per-system sets), so they live
      # outside eachDefaultSystem.
      overlays.default = final: prev: {
        omnilatex = final.callPackage self.packages.${final.system or final.stdenv.system}.default {};
      };
    };
}
