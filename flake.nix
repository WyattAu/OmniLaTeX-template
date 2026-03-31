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
          packages = with pkgs; [
            texlive
            pythonEnv
            latexmk
            inkscape
            biber
            gnumake
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

          nativeBuildInputs = [ texlive pythonEnv pkgs.latexmk ];

          buildPhase = ''
            export HOME=$(mktemp -d)
            export SOURCE_DATE_EPOCH=1700000000
            latexmk -lualatex -interaction=nonstopmode \
              examples/thesis/main.tex
          '';

          installPhase = ''
            mkdir -p $out
            cp examples/thesis/main.pdf $out/omnilatex-example.pdf
          '';
        };

        overlays.default = final: prev: {
          omnilatex = self.packages.${system}.default;
        };

        checks.reproducibility = pkgs.stdenvNoCC.mkDerivation {
          name = "omnilatex-reproducibility-check";
          src = ./.;

          nativeBuildInputs = [ texlive pythonEnv pkgs.latexmk ];

          buildPhase = ''
            export HOME=$(mktemp -d)
            export SOURCE_DATE_EPOCH=1700000000

            latexmk -lualatex -interaction=nonstopmode \
              -outdir=$TMPDIR/build1 \
              examples/thesis/main.tex
            hash1=$(sha256sum $TMPDIR/build1/main.pdf | cut -d' ' -f1)

            rm -rf $TMPDIR/build1
            export HOME=$(mktemp -d)

            latexmk -lualatex -interaction=nonstopmode \
              -outdir=$TMPDIR/build2 \
              examples/thesis/main.tex
            hash2=$(sha256sum $TMPDIR/build2/main.pdf | cut -d' ' -f1)

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
          python3 -m py_compile $src/build.py
          echo "PASS: Python syntax check"
          mkdir $out
        '';
      }
    );
}
