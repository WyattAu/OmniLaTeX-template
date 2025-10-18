#!/usr/bin/env perl
$pdf_mode = 4;
set_tex_cmds("--shell-escape --synctex=1 --file-line-error --halt-on-error --interaction=nonstopmode %O %S");
$max_repeat = 2;
$clean_ext = "%R-*.aux %R-*.fls %R-*.fdb_latexmk %R-*.synctex.gz _minted-%R";
$cleanup_includes_cusdep_generated = 1;
