{
  description = "OmniLaTeX — Modular LaTeX template system";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # TODO: Replace scheme-full with scheme-medium + explicit package list
        # to reduce closure size. scheme-full is ~4 GB; scheme-medium + pkgs is
        # ~1 GB. For now, scheme-full ensures all LaTeX packages are available
        # without exhaustive enumeration.
        texlive = pkgs.texlive.combine {
          inherit (pkgs.texlive)
            scheme-full
          ;
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          pygments
          pymupdf
          pytest
          hypothesis
        ]);

        # NOTE: Custom fonts (Monaspace Neon, Atkinson Hyperlegible Next) are
        # not available in nixpkgs. Users needing these fonts should either:
        #   1. Install them system-wide and use NIX_FONTS or fontconfig overrides
        #   2. Use the Docker image which bundles them
        # Libertinus and Font Awesome 5 are included via scheme-full.
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            texlive
            pythonEnv
            pkgs.gnumake
          ];

          shellHook = ''
            echo "OmniLaTeX development environment"
            echo "TeX Live: $(tex --version | head -1)"
            echo "Python: $(python3 --version)"
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
