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
            ];

            env = {
              SOURCE_DATE_EPOCH = "1700000000";
            };

            shellHook = ''
              echo "OmniLaTeX dev shell ready"
              echo "  TeX Live: $(lualatex --version | head -1)"
              echo "  Python:  $(python3 --version)"
              echo ""
              echo "Quick start:"
              echo "  python build.py build-example minimal-starter"
              echo "  python build.py --help"
            '';
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
            dontBuild = true;
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

          default = self.packages.${system}.omnilatex;
        }
      );

      # Build applications
      apps = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          tex = pkgs.texlive.combined.scheme-full;
          pyenv = pkgs.python3.withPackages (ps: [ ps.pygments ]);
        in {
          # Build minimal-starter example
          default = {
            type = "app";
            program = "${pkgs.writeShellScript "omnilatex-build" ''
              set -euo pipefail

              export PATH="${pkgs.lib.makeBinPath [ tex pyenv pkgs.coreutils ]}"
              export SOURCE_DATE_EPOCH=''${SOURCE_DATE_EPOCH:-1700000000}
              export HOME=$(mktemp -d)

              src="${self}"
              tmpdir=$(mktemp -d)
              trap 'rm -rf "$tmpdir" 2>/dev/null; true' EXIT

              mkdir -p "$tmpdir/repo/examples/minimal-starter"
              cp -r "$src/examples/minimal-starter/"* "$tmpdir/repo/examples/minimal-starter/"

              for f in omnilatex.cls lib lua config assets bib; do
                [ -e "$src/$f" ] && ln -s "$src/$f" "$tmpdir/repo/$f"
              done
              ln -s "$src/.latexmkrc" "$tmpdir/repo/.latexmkrc"

              cd "$tmpdir/repo/examples/minimal-starter"
              latexmk -lualatex -interaction=nonstopmode main.tex

              outdir="''${1:-.}"
              cp main.pdf "$outdir/omnilatex-minimal.pdf"
              echo "PDF: $outdir/omnilatex-minimal.pdf"
            ''}";
          };

          # Build all examples
          build-all = {
            type = "app";
            program = "${pkgs.writeShellScript "omnilatex-build-all" ''
              set -euo pipefail

              export PATH="${pkgs.lib.makeBinPath [ tex pyenv pkgs.coreutils ]}"
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
        omnilatex = final.stdenv.mkDerivation {
          pname = "omnilatex";
          version = "2.4.0";
          src = self;
          dontBuild = true;
          installPhase = ''
            mkdir -p $out/share/texmf/tex/latex/omnilatex
            cp -r . $out/share/texmf/tex/latex/omnilatex/
          '';
          meta = with final.lib; {
            description = "Modular LaTeX document class";
            homepage = "https://github.com/WyattAu/OmniLaTeX-template";
            license = licenses.asl20;
          };
        };
      };
    };
}
