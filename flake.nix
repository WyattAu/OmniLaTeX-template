{
  description = "OmniLaTeX — Modular LaTeX template system";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      devShells = forAllSystems (system:
        let pkgs = nixpkgs.legacyPackages.${system};
        in {
          default = pkgs.mkShell {
            packages = [
              pkgs.texlive.combined.scheme-full
              (pkgs.python3.withPackages (ps: [ ps.pygments ]))
            ];

            SOURCE_DATE_EPOCH = "1700000000";
          };
        }
      );

      apps = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          tex = pkgs.texlive.combined.scheme-full;
          pyenv = pkgs.python3.withPackages (ps: [ ps.pygments ]);
        in {
          default = {
            type = "app";
            program = "${pkgs.writeShellScript "omnilatex-build" ''
              set -euo pipefail

              export PATH="${pkgs.lib.makeBinPath [ tex pyenv pkgs.coreutils ]}"
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
        }
      );
    };
}
