{
  description = "OmniLaTeX — Modular LaTeX template system";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      # Development shell with TeX Live + Python
      devShells = forAllSystems (system:
        let pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            packages = [
              pkgs.texlive.combined.scheme-full
              (pkgs.python3.withPackages (ps: [ ps.pygments ]))
              pkgs.latexmk
              pkgs.biber
              pkgs.bib2gls
            ];

            shellHook = ''
              echo "OmniLaTeX dev shell ready"
              echo "  TeX Live: $(lualatex --version | head -1)"
              echo "  Python:  $(python3 --version)"
              echo ""
              echo "Quick start:"
              echo "  python build.py build-example minimal-starter"
              echo "  python build.py --help"
            '';

            SOURCE_DATE_EPOCH = "1700000000";
          };
        }
      );

      # Nix packages for registry publishing
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          tex = pkgs.texlive.combined.scheme-full;
          pyenv = pkgs.python3.withPackages (ps: [ ps.pygments ]);
        in {
          # Full OmniLaTeX package (all files)
          omnilatex = pkgs.stdenv.mkDerivation {
            pname = "omnilatex";
            version = "2.4.0";
            src = self;
            buildPhase = ''
              # Validate structure
              test -f omnilatex.cls
              test -d lib
              test -d config
              test -d examples
            '';
            installPhase = ''
              mkdir -p $out/share/texmf/tex/latex/omnilatex
              cp -r . $out/share/texmf/tex/latex/omnilatex/
            '';
            meta = with pkgs.lib; {
              description = "Modular LaTeX document class with 27 doctypes, 25 languages, 21 institutions";
              homepage = "https://github.com/WyattAu/OmniLaTeX-template";
              license = licenses.asl20;
              platforms = platforms.all;
            };
          };

          # Build app (compiles minimal-starter)
          default = {
            type = "app";
            program = "${pkgs.writeShellScript "omnilatex-build" ''
              set -euo pipefail

              export PATH="${pkgs.lib.makeBinPath [ tex pyenv pkgs.coreutils pkgs.latexmk ]}"
              export SOURCE_DATE_EPOCH=''${SOURCE_DATE_EPOCH:-1700000000}
              export HOME=$(mktemp -d)

              src="${self}"
              tmpdir=$(mktemp -d)
              trap 'rm -rf "$tmpdir"' EXIT

              mkdir -p "$tmpdir/repo/examples/minimal-starter"
              cp -r "$src/examples/minimal-starter/"* "$tmpdir/repo/examples/minimal-starter/"

              for f in omnilatex.cls lib lua config assets bib; do
                [ -e "$src/$f" ] && ln -s "$src/$f" "$tmpdir/repo/$f"
              done
              ln -s "$src/.latexmkrc" "$tmpdir/repo/.latexmkrc"

              cd "$tmpdir/repo/examples/minimal-starter"
              latexmk -lualatex -interaction=nonstopmode main.tex

              outdir="''${1:-''${PWD}}"
              cp main.pdf "$outdir/omnilatex-minimal.pdf"
              echo "PDF: $outdir/omnilatex-minimal.pdf"
            ''}";
          };

          # Build all examples
          build-all = {
            type = "app";
            program = "${pkgs.writeShellScript "omnilatex-build-all" ''
              set -euo pipefail

              export PATH="${pkgs.lib.makeBinPath [ tex pyenv pkgs.coreutils pkgs.latexmk ]}"
              export SOURCE_DATE_EPOCH=''${SOURCE_DATE_EPOCH:-1700000000}
              export HOME=$(mktemp -d)

              src="${self}"
              cd "$src"
              python build.py --jobs $(nproc) build-examples
            ''}";
          };
        }
      );

      # Overlay for adding to other Nix configurations
      overlays.default = final: prev: {
        omnilatex = final.callPackage ({ stdenv, texlive, python3, ... }:
          stdenv.mkDerivation {
            pname = "omnilatex";
            version = "2.4.0";
            src = self;
            buildPhase = "true";
            installPhase = ''
              mkdir -p $out/share/texmf/tex/latex/omnilatex
              cp -r . $out/share/texmf/tex/latex/omnilatex/
            '';
            meta = with final.lib; {
              description = "Modular LaTeX document class";
              homepage = "https://github.com/WyattAu/OmniLaTeX-template";
              license = licenses.asl20;
            };
          }
        ) {};
      };
    };
}
