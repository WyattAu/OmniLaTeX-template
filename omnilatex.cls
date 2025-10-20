%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% OmniLaTeX Universal Document Class
%
% A fully modular LaTeX template following SOLID principles
% Hard fork with complete modularization
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{omnilatex}[2024-10-11 v6.0.0 OmniLaTeX universal class]

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
\omnilatex@matchdoctypes{journal,journals,magazine,magazines}{\omnilatex@setdoctype{journal}{scrartcl}{\omnilatex@journaloptions}}%
\omnilatex@matchdoctypes{dictionary,dictionaries,lexicon,lexicons}{\omnilatex@setdoctype{dictionary}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{cv,resume,resumes,curriculumvitae}{\omnilatex@setdoctype{cv}{scrartcl}{\omnilatex@cvoptions}}%

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

\RequirePackage{lib/core/omnilatex-base}
\RequirePackage{lib/utils/omnilatex-colors}
\RequirePackage{lib/utils/omnilatex-utils}
\RequirePackage{lib/typography/omnilatex-fonts}
\RequirePackage{lib/typography/omnilatex-math}
\RequirePackage{lib/typography/omnilatex-lists}
\RequirePackage{lib/typography/omnilatex-typesetting}
\RequirePackage{lib/graphics/omnilatex-graphics}
\RequirePackage{lib/graphics/omnilatex-tikz-core}
\RequirePackage{lib/graphics/omnilatex-tikz-engineering}
\RequirePackage{lib/language/omnilatex-i18n}
\RequirePackage{lib/tables/omnilatex-tables}
\RequirePackage{lib/code/omnilatex-listings}
\RequirePackage{lib/layout/omnilatex-page}
\RequirePackage{lib/layout/omnilatex-koma}
\RequirePackage{lib/layout/omnilatex-floats}
\RequirePackage{lib/references/omnilatex-biblio}
\RequirePackage{lib/references/omnilatex-glossary}
\RequirePackage{lib/references/omnilatex-hyperref}
\RequirePackage{lib/layout/omnilatex-boxes}
\RequirePackage{lib/layout/omnilatex-document}

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
