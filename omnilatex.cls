%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% OmniLaTeX Universal Document Class
%
% A fully modular LaTeX template following SOLID principles
% Hard fork with complete modularization
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{omnilatex}[2024-10-11 v6.0.0 OmniLaTeX universal class]

\RequirePackage{iftex}
\RequireLuaTeX{}

\newcommand*{\@baseclass}{scrbook}

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
    \PassOptionsToPackage{paper=a5}{typearea}
    \PassOptionsToClass{fontsize=10pt}{\@baseclass}%
}%

\DeclareDefaultOption{\PassOptionsToClass{\CurrentOption}{\@baseclass}}
\ProcessKeyvalOptions*

\PassOptionsToClass{%
    \omnilatex@language,
    listof=totoc,
    bibliography=totoc,
    chapterprefix=true,
    open=right,
    numbers=noenddot,
}{\@baseclass}

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
