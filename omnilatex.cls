%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% OmniLaTeX Universal Document Class
%
% A modular LaTeX template
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{omnilatex}[2026-04-25 v1.5.0 OmniLaTeX universal class]

\RequirePackage{iftex}
\RequirePackage{etoolbox}
\RequirePackage{expl3}
\RequireLuaTeX{}

\newcommand*{\@baseclass}{scrbook}
\newcommand*{\omnilatexclassoptions}{}
\newcommand*{\omnilatexuserclassoptions}{}
\newcommand*{\omnilatex@doctypeprofile}{}
\newif\ifomnilatex@haschapters
\omnilatex@haschaptersfalse
\newif\ifomnilatex@doctypematched
\omnilatex@doctypematchedfalse

\ExplSyntaxOn
\tl_new:N \l__omnilatex_tmp_tl
\tl_new:N \g__omnilatex_user_options_tl
\cs_new_protected:Npn \omnilatex@adduseroption #1
{
    \tl_set:Nn \l__omnilatex_tmp_tl { #1 }
    \tl_trim_spaces:N \l__omnilatex_tmp_tl
    \tl_if_blank:VTF \l__omnilatex_tmp_tl
    { }
    {
        \tl_if_empty:NTF \g__omnilatex_user_options_tl
        { \tl_gset_eq:NN \g__omnilatex_user_options_tl \l__omnilatex_tmp_tl }
        {
            \tl_gput_right:Nn \g__omnilatex_user_options_tl { , }
            \tl_gput_right:NV \g__omnilatex_user_options_tl \l__omnilatex_tmp_tl
        }
        \xdef\omnilatexuserclassoptions{\tl_use:N \g__omnilatex_user_options_tl}
    }
}
\ExplSyntaxOff

\newcommand*{\omnilatex@setdoctype}[3]{%
    \renewcommand*{\@baseclass}{#2}%
    \renewcommand*{\omnilatexclassoptions}{\omnilatex@language,#3}%
    \gdef\omnilatex@doctypeprofile{#1}%
    \omnilatex@haschaptersfalse
    \ifdefstring{#2}{scrbook}{\omnilatex@haschapterstrue}{%
        \ifdefstring{#2}{scrreprt}{\omnilatex@haschapterstrue}{}%
    }%
    \omnilatex@doctypematchedtrue
    \ClassInfo{omnilatex}{Selected doctype '#1' (base=#2)}%
}

\newcommand*{\omnilatex@matchdoctype}[2]{%
    \ifdefstring{\omnilatex@doctype}{#1}{#2\ClassInfo{omnilatex}{Matched doctype '#1'}}{}%
}

\newcommand*{\omnilatex@matchdoctypes}[2]{%
    \def\omnilatex@tmp@handler##1{\omnilatex@matchdoctype{##1}{#2}}%
    \forcsvlist{\omnilatex@tmp@handler}{#1}%
}

\newcommand*{\omnilatex@bookoptions}{listof=totoc,bibliography=totoc,chapterprefix=true,open=right,numbers=noenddot}
\newcommand*{\omnilatex@reportoptions}{listof=totoc,bibliography=totoc,chapterprefix=false,open=any,numbers=noenddot}
\newcommand*{\omnilatex@articleoptions}{bibliography=totoc,numbers=noenddot,parskip=half}
\newcommand*{\omnilatex@inlinepaperoptions}{bibliography=totoc,numbers=noenddot,parskip=half,titlepage=false}
\newcommand*{\omnilatex@journaloptions}{bibliography=totoc,numbers=noenddot,parskip=half,titlepage=true}
\newcommand*{\omnilatex@cvoptions}{numbers=noenddot,parskip=full,fontsize=11pt}

\RequirePackage{kvoptions}
\SetupKeyvalOptions{family=omnilatex,prefix=omnilatex@}

\DeclareStringOption[english]{language}[english]
\DeclareStringOption[thesis]{doctype}[thesis]
\DeclareStringOption[book]{titlestyle}[book]
\DeclareStringOption[none]{institution}[none]
\DeclareBoolOption{censoring}
\DeclareBoolOption{loadGlossaries}
\DeclareBoolOption{todonotes}
\DeclareBoolOption{enablefonts}
\DeclareBoolOption{enablegraphics}
\DeclareBoolOption[true]{enablemath}
\DeclareBoolOption[true]{enabletikz}
\DeclareBoolOption[true]{enableengineering}
\DeclareBoolOption[true]{enablecode}
\DeclareBoolOption[true]{enabletables}

\DeclareVoidOption{a5}{%
    \PassOptionsToPackage{paper=a5}{typearea}%
    \omnilatex@adduseroption{fontsize=10pt}%
}%

\DeclareDefaultOption{\omnilatex@adduseroption{\CurrentOption}}
\ProcessKeyvalOptions*

\ExplSyntaxOn
\tl_set:Nn \l__omnilatex_tmp_tl {\omnilatex@doctype}
\tl_trim_spaces:N \l__omnilatex_tmp_tl
\tl_set:Nx \l__omnilatex_tmp_tl {\tl_lower_case:n {\l__omnilatex_tmp_tl}}
\edef\omnilatex@doctype{\tl_use:N \l__omnilatex_tmp_tl}
\tl_set:Nn \l__omnilatex_tmp_tl {\omnilatex@titlestyle}
\tl_trim_spaces:N \l__omnilatex_tmp_tl
\tl_set:Nx \l__omnilatex_tmp_tl {\tl_lower_case:n {\l__omnilatex_tmp_tl}}
\edef\omnilatex@titlestyle{\tl_use:N \l__omnilatex_tmp_tl}
\ExplSyntaxOff
\ClassInfo{omnilatex}{Option doctype=\omnilatex@doctype, titlestyle=\omnilatex@titlestyle}

\omnilatex@setdoctype{book}{scrbook}{\omnilatex@bookoptions}
\omnilatex@matchdoctypes{book}{\omnilatex@setdoctype{book}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{thesis,theses}{\omnilatex@setdoctype{thesis}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{dissertation,dissertations}{\omnilatex@setdoctype{dissertation}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{manual,manuals,guide,guides,handbook,handbooks}{\omnilatex@setdoctype{manual}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{report,reports,technicalreport,technical-report,technicalreports,technical-reports,techreport,tech-report,techreports}{\omnilatex@setdoctype{technicalreport}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{standard,standards}{\omnilatex@setdoctype{standard}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{patent,patents}{\omnilatex@setdoctype{patent}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{article,articles,paper,papers}{\omnilatex@setdoctype{article}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{inlinepaper,inlinepapers,inline-research,inline-research-paper}{\omnilatex@setdoctype{inlinepaper}{scrartcl}{\omnilatex@inlinepaperoptions}}%
\omnilatex@matchdoctypes{journal,journals,magazine,magazines}{\omnilatex@setdoctype{journal}{scrartcl}{\omnilatex@journaloptions}}%
\omnilatex@matchdoctypes{dictionary,dictionaries,lexicon,lexicons}{\omnilatex@setdoctype{dictionary}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{cv,resume,resumes,curriculumvitae}{\omnilatex@setdoctype{cv}{scrartcl}{\omnilatex@cvoptions}}%
\omnilatex@matchdoctypes{cover-letter,coverletter}{\omnilatex@setdoctype{cover-letter}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{poster,posters}{\omnilatex@setdoctype{poster}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{presentation,presentations,slides,talk,talks}{\omnilatex@setdoctype{presentation}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{letter,letters}{\omnilatex@setdoctype{letter}{scrartcl}{\omnilatex@articleoptions}}%

% Validate doctype: warn if user passed an unknown doctype that didn't match
\ifomnilatex@doctypematched\else
    \ClassWarning{omnilatex}{Unknown doctype '\omnilatex@doctype'.%
        Falling back to 'book'. Valid options: book, thesis, dissertation,%
        manual, guide, handbook, report, technicalreport, standard, patent,%
        article, inlinepaper, journal, dictionary, cv, cover-letter, poster, presentation, letter}%
\fi

% Validate titlestyle
\ExplSyntaxOn
\str_case:VnF \omnilatex@titlestyle
{
    { book } { }
    { thesis } { }
    { article } { }
    { simple } { }
    { tuhh } { }
    { TUHH } { }
}
{
    \ClassInfo{omnilatex}{Unknown~titlestyle~'\omnilatex@titlestyle'.~
        Using~default~title~page~layout.}
}
\ExplSyntaxOff

\ifx\omnilatexuserclassoptions\@empty
    \PassOptionsToClass{\omnilatexclassoptions}{\@baseclass}
\else
    \PassOptionsToClass{\omnilatexclassoptions,\omnilatexuserclassoptions}{\@baseclass}
\fi

\LoadClass{\@baseclass}
\RequirePackage[\omnilatex@language]{tracklang}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Load Core Modules (Always)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Core modules (always loaded)
\RequirePackage{lib/core/omnilatex-base}
\RequirePackage{lib/utils/omnilatex-colors}
\RequirePackage{lib/utils/omnilatex-utils}
\RequirePackage{lib/typography/omnilatex-fonts}
\RequirePackage{lib/typography/omnilatex-lists}
\RequirePackage{lib/typography/omnilatex-typesetting}
\RequirePackage{lib/layout/omnilatex-page}
\RequirePackage{lib/layout/omnilatex-koma}
\RequirePackage{lib/layout/omnilatex-floats}
\RequirePackage{lib/layout/omnilatex-boxes}
\RequirePackage{lib/layout/omnilatex-document}
\RequirePackage{lib/references/omnilatex-hyperref}
% Workaround: luaotfload-multiscript.lua calls kpse.find_file('ScriptExtensions.txt')
% which returns nil in Nix/TL2025, then calls os.exit(-1). Patch kpse.find_file
% to return a dummy temp file when the real file is missing.
\directlua{dofile(kpse.find_file("lib/utils/luaotfload-workaround.lua") or "lib/utils/luaotfload-workaround.lua")}%

% Pre-define script fonts for polyglossia (TL2025 checks main font).
% Without these, polyglossia errors with --halt-on-error.
\@ifundefined{cjkfont}{%
  \def\omnilatex@check@cjk@lang#1{%
    \IfStrEq{\omnilatex@language}{#1}{%
      \IfFontExistsTF{Noto Serif CJK SC}{%
        \newfontfamily\cjkfont[Script=CJK]{Noto Serif CJK SC}%
      }{%
        \IfFontExistsTF{Haranoaji Mincho}{%
          \newfontfamily\cjkfont[Script=CJK]{Haranoaji Mincho}%
        }{}%
      }%
    }{}%
  }%
  \omnilatex@check@cjk@lang{chinese}%
  \omnilatex@check@cjk@lang{japanese}%
  \omnilatex@check@cjk@lang{korean}%
}{}%
\@ifundefined{cjkfontsf}{%
  \def\omnilatex@check@cjk@sf@lang#1{%
    \IfStrEq{\omnilatex@language}{#1}{%
      \IfFontExistsTF{Noto Sans CJK SC}{%
        \newfontfamily\cjkfontsf[Script=CJK]{Noto Sans CJK SC}%
      }{%
        \IfFontExistsTF{Noto Sans CJK JP}{%
          \newfontfamily\cjkfontsf[Script=CJK]{Noto Sans CJK JP}%
        }{}%
      }%
    }{}%
  }%
  \omnilatex@check@cjk@sf@lang{chinese}%
  \omnilatex@check@cjk@sf@lang{japanese}%
  \omnilatex@check@cjk@sf@lang{korean}%
}{}%
\@ifundefined{hangulfont}{%
  \IfStrEq{\omnilatex@language}{korean}{%
    \IfFontExistsTF{Noto Sans CJK KR}{%
      \newfontfamily\hangulfont[Script=Hangul]{Noto Sans CJK KR}%
    }{%
      \IfFontExistsTF{Noto Serif CJK KR}{%
        \newfontfamily\hangulfont[Script=Hangul]{Noto Serif CJK KR}%
      }{}%
    }%
  }{}%
}{}%
\@ifundefined{hangulfontsf}{%
  \IfStrEq{\omnilatex@language}{korean}{%
    \IfFontExistsTF{Noto Sans CJK KR}{%
      \newfontfamily\hangulfontsf[Script=Hangul,BoldFont=Noto Sans CJK KR,BoldFeatures={FakeBold=2}]{Noto Sans CJK KR}%
    }{%
      \IfFontExistsTF{Noto Serif CJK KR}{%
        \newfontfamily\hangulfontsf[Script=Hangul,BoldFont=Noto Serif CJK KR,BoldFeatures={FakeBold=2}]{Noto Serif CJK KR}%
      }{}%
    }%
  }{}%
}{}%
\@ifundefined{arabicfont}{%
  \IfStrEq{\omnilatex@language}{arabic}{%
    \IfFontExistsTF{Noto Naskh Arabic}{%
      \newfontfamily\arabicfont[Script=Arabic,BoldFont=Noto Naskh Arabic,BoldFeatures={FakeBold=2}]{Noto Naskh Arabic}%
      \newfontfamily\arabicfontfamily[Script=Arabic,BoldFont=Noto Naskh Arabic,BoldFeatures={FakeBold=2}]{Noto Naskh Arabic}%
      \newfontfamily\arabicfontsf[Script=Arabic,BoldFont=Noto Naskh Arabic,BoldFeatures={FakeBold=2}]{Noto Naskh Arabic}%
    }{%
      \IfFontExistsTF{Amiri}{%
        \newfontfamily\arabicfont[Script=Arabic,BoldFont=Amiri,BoldFeatures={FakeBold=2}]{Amiri}%
        \newfontfamily\arabicfontfamily[Script=Arabic,BoldFont=Amiri,BoldFeatures={FakeBold=2}]{Amiri}%
        \newfontfamily\arabicfontsf[Script=Arabic,BoldFont=Amiri,BoldFeatures={FakeBold=2}]{Amiri}%
      }{}%
    }%
  }{}%
}{}%
\@ifundefined{hebrewfont}{%
  \IfStrEq{\omnilatex@language}{hebrew}{%
    \IfFontExistsTF{Noto Serif Hebrew}{%
      \newfontfamily\hebrewfont[Script=Hebrew,
        BoldFont=Noto Serif Hebrew,BoldFeatures={FakeBold=2}]{Noto Serif Hebrew}%
      \newfontfamily\hebrewfontfamily[Script=Hebrew,BoldFont=Noto Serif Hebrew,BoldFeatures={FakeBold=2}]{Noto Serif Hebrew}%
      \newfontfamily\hebrewfontsf[Script=Hebrew,BoldFont=Noto Serif Hebrew,BoldFeatures={FakeBold=2}]{Noto Serif Hebrew}%
    }{%
      \IfFontExistsTF{Frank Ruehl CLM}{%
        \newfontfamily\hebrewfont[Script=Hebrew,BoldFont=Frank Ruehl CLM,BoldFeatures={FakeBold=2}]{Frank Ruehl CLM}%
        \newfontfamily\hebrewfontfamily[Script=Hebrew,BoldFont=Frank Ruehl CLM,BoldFeatures={FakeBold=2}]{Frank Ruehl CLM}%
        \newfontfamily\hebrewfontsf[Script=Hebrew,BoldFont=Frank Ruehl CLM,BoldFeatures={FakeBold=2}]{Frank Ruehl CLM}%
      }{%
        \IfFontExistsTF{David CLM}{%
          \newfontfamily\hebrewfont[Script=Hebrew,BoldFont=David CLM,BoldFeatures={FakeBold=2}]{David CLM}%
          \newfontfamily\hebrewfontfamily[Script=Hebrew,BoldFont=David CLM,BoldFeatures={FakeBold=2}]{David CLM}%
          \newfontfamily\hebrewfontsf[Script=Hebrew,BoldFont=David CLM,BoldFeatures={FakeBold=2}]{David CLM}%
        }{}%
      }%
    }%
  }{}%
}{}%

\RequirePackage{lib/language/omnilatex-i18n}

% Auto-load CJK support for Chinese, Japanese, Korean
\def\omnilatex@cjk@check@lang#1{%
  \IfStrEq{\omnilatex@language}{#1}{\RequirePackage{lib/language/omnilatex-cjk}}{}%
}
\omnilatex@cjk@check@lang{chinese}%
\omnilatex@cjk@check@lang{japanese}%
\omnilatex@cjk@check@lang{korean}%

% Auto-load RTL support for Arabic, Hebrew
\def\omnilatex@rtl@check@lang#1{%
  \IfStrEq{\omnilatex@language}{#1}{\RequirePackage{lib/language/omnilatex-rtl}}{}%
}
\omnilatex@rtl@check@lang{arabic}%
\omnilatex@rtl@check@lang{hebrew}%

%% setspaceenhanced is loaded by omnilatex-base.sty instead

% Conditional modules (default: all enabled for backward compatibility)
\ifomnilatex@enablemath
    \RequirePackage{lib/typography/omnilatex-math}
\fi
\ifomnilatex@enabletikz
    \RequirePackage{lib/graphics/omnilatex-graphics}
    \RequirePackage{lib/graphics/omnilatex-tikz-core}
\fi
\ifomnilatex@enableengineering
    \RequirePackage{lib/graphics/omnilatex-tikz-engineering}
\fi
\ifomnilatex@enablecode
    \RequirePackage{lib/code/omnilatex-listings}
\fi
\ifomnilatex@enabletables
    \RequirePackage{lib/tables/omnilatex-tables}
\fi
\ifomnilatex@loadGlossaries
    \RequirePackage{lib/references/omnilatex-glossary}
\fi
\RequirePackage{lib/references/omnilatex-biblio}

\def\@doctypefile{}
\edef\@doctypecandidate{config/document-types/\omnilatex@doctypeprofile}
\IfFileExists{\@doctypecandidate.sty}{\edef\@doctypefile{\@doctypecandidate}}{%
    \IfFileExists{config/document-types/\omnilatex@doctypeprofile/\omnilatex@doctypeprofile.sty}{%
        \edef\@doctypefile{config/document-types/\omnilatex@doctypeprofile/\omnilatex@doctypeprofile}%
    }{}
}
\ifx\@doctypefile\@empty\else\RequirePackage{\@doctypefile}\fi

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Load Institution Configuration
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Priority:
% 1. Local config/institution.sty (example-specific)
% 2. Root config/institutions/INSTITUTION/INSTITUTION.sty (shared)
% 3. None (generic template)

\def\@institutionfile{}%
\ifdefstring{\omnilatex@institution}{none}{%
    \ClassInfo{omnilatex}{Using generic template (no institution)}%
}{%
    % First, try to load local institution config (for examples)
    \IfFileExists{config/institution.sty}{%
        \ClassInfo{omnilatex}{Loading local institution configuration from config/institution.sty}%
        \def\@institutionfile{config/institution}%
    }{%
        % Fallback to shared institution configs (for root template)
        \ifdefstring{\omnilatex@institution}{tuhh}{%
            \ClassInfo{omnilatex}{Loading TUHH configuration from shared config}%
            \def\@institutionfile{config/institutions/tuhh/tuhh}%
        }{%
            \IfFileExists{config/institutions/\omnilatex@institution/\omnilatex@institution.sty}{%
                \ClassInfo{omnilatex}{Loading \omnilatex@institution{} configuration from shared config}%
                \edef\@institutionfile{config/institutions/\omnilatex@institution/\omnilatex@institution}%
            }{%
                \ClassWarning{omnilatex}{Institution '\omnilatex@institution' not found}%
            }%
        }%
    }%
}%

\ifx\@institutionfile\@empty\else\RequirePackage{\@institutionfile}\fi

\endinput
