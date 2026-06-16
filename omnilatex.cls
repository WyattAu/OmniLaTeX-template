%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% OmniLaTeX Universal Document Class
%
% A modular LaTeX template
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{omnilatex}[2026/06/07 v2.5.0 OmniLaTeX universal class]

\RequirePackage{iftex}
\RequirePackage{etoolbox}
% expl3 is part of the LaTeX2e kernel since 2020; no explicit load needed.
\RequireLuaTeX{}

\newcommand*{\@baseclass}{scrbook}
\newcommand*{\omnilatexclassoptions}{}
\newcommand*{\omnilatexuserclassoptions}{}
\newcommand*{\omnilatex@doctypeprofile}{}
\newif\ifomnilatex@haschapters
\omnilatex@haschaptersfalse
\newif\ifomnilatex@doctypematched
\omnilatex@doctypematchedfalse
\newif\ifomnilatex@beamer
\omnilatex@beamerfalse

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
\newcommand*{\omnilatex@grantproposaloptions}{bibliography=totoc,numbers=noenddot,parskip=half,DIV=12,BCOR=0mm}
\newcommand*{\omnilatex@ieeeoptions}{bibliography=totoc,numbers=noenddot,parskip=off,DIV=9,BCOR=0mm,twocolumn}
\newcommand*{\omnilatex@bookchapteroptions}{bibliography=totoc,numbers=noenddot,parskip=half}
\newcommand*{\omnilatex@inlinepaperoptions}{bibliography=totoc,numbers=noenddot,parskip=half,titlepage=false}
\newcommand*{\omnilatex@journaloptions}{bibliography=totoc,numbers=noenddot,parskip=half,titlepage=true}
\newcommand*{\omnilatex@cvoptions}{numbers=noenddot,parskip=full,fontsize=11pt}
\newcommand*{\omnilatex@beameraoptions}{}

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
\DeclareBoolOption[true]{enablelayout}
\DeclareBoolOption[true]{enablebibliography}
\DeclareBoolOption[true]{enablehyperref}
\DeclareBoolOption{minimal}

\DeclareStringOption[169]{beameraspectratio}[169]
\DeclareBoolOption[true]{beamernavigationsymbols}
\DeclareStringOption[default]{beamertheme}[default]

\DeclareVoidOption{a5}{%
    \PassOptionsToPackage{paper=a5}{typearea}%
    \omnilatex@adduseroption{fontsize=10pt}%
}%

\DeclareDefaultOption{\omnilatex@adduseroption{\CurrentOption}}
\ProcessKeyvalOptions*

% Minimal mode: disable all optional module groups at once
\ifomnilatex@minimal
    \omnilatex@enablelayoutfalse
    \omnilatex@enablemathfalse
    \omnilatex@enabletikzfalse
    \omnilatex@enableengineeringfalse
    \omnilatex@enablecodefalse
    \omnilatex@enabletablesfalse
    \omnilatex@enablebibliographyfalse
    \omnilatex@enablehyperreffalse
\fi

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
\omnilatex@matchdoctypes{letter,letters}{\omnilatex@setdoctype{letter}{scrartcl}{\omnilatex@articleoptions}}
\omnilatex@matchdoctypes{homework,homeworks}{\omnilatex@setdoctype{homework}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{exam,exams,examination,examinations}{\omnilatex@setdoctype{exam}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{research-proposal,researchproposal,research-proposals}{\omnilatex@setdoctype{research-proposal}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{lecture-notes,lecturenotes,lecture-note}{\omnilatex@setdoctype{lecture-notes}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{syllabus,syllabi}{\omnilatex@setdoctype{syllabus}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{handout,handouts}{\omnilatex@setdoctype{handout}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{memo,memos,memorandum,memorandums}{\omnilatex@setdoctype{memo}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{white-paper,whitepapers}{\omnilatex@setdoctype{white-paper}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{invoice,invoices}{\omnilatex@setdoctype{invoice}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{recipe,recipes}{\omnilatex@setdoctype{recipe}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{grant-proposal,grantproposal,nsf-proposal,erc-proposal}{\omnilatex@setdoctype{grant-proposal}{scrartcl}{\omnilatex@grantproposaloptions}}%
\omnilatex@matchdoctypes{ieee,ieee-paper,ieee-conference,ieeetran}{\omnilatex@setdoctype{ieee}{scrartcl}{\omnilatex@ieeeoptions}}%
\omnilatex@matchdoctypes{book-chapter,bookchapter,chapter}{\omnilatex@setdoctype{book-chapter}{scrartcl}{\omnilatex@bookchapteroptions}}%
% --- Academic / Research ---
\omnilatex@matchdoctypes{lab-report,labreport,lab-report-course}{\omnilatex@setdoctype{lab-report}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{literature-review,literaturereview,lit-review}{\omnilatex@setdoctype{literature-review}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{thesis-proposal,thesisproposal,prospectus}{\omnilatex@setdoctype{thesis-proposal}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{annotated-bibliography,annotatedbibliography,annotated-bib}{\omnilatex@setdoctype{annotated-bibliography}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{proceedings,conference-proceedings}{\omnilatex@setdoctype{proceedings}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{preprint,preprints,eprint}{\omnilatex@setdoctype{preprint}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{working-paper,workingpaper,discussion-paper,discussionpaper}{\omnilatex@setdoctype{working-paper}{scrartcl}{\omnilatex@articleoptions}}%
% --- Business / Professional ---
\omnilatex@matchdoctypes{business-letter,businessletter}{\omnilatex@setdoctype{business-letter}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{meeting-minutes,meetingminutes,minutes}{\omnilatex@setdoctype{meeting-minutes}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{quarterly-report,quarterlyreport,quarterly}{\omnilatex@setdoctype{quarterly-report}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{strategic-plan,strategicplan,strategy}{\omnilatex@setdoctype{strategic-plan}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{product-spec,productspec,specification,spec}{\omnilatex@setdoctype{product-spec}{scrreprt}{\omnilatex@reportoptions}}%
% --- Education ---
\omnilatex@matchdoctypes{course-material,coursematerial,course-pack}{\omnilatex@setdoctype{course-material}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{course-notes,coursenotes}{\omnilatex@setdoctype{course-notes}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{textbook,text-books}{\omnilatex@setdoctype{textbook}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{worksheet,worksheets}{\omnilatex@setdoctype{worksheet}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{quiz,quizzes,test,tests,examination-sheet}{\omnilatex@setdoctype{quiz}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{lesson-plan,lessonplan}{\omnilatex@setdoctype{lesson-plan}{scrartcl}{\omnilatex@articleoptions}}%
% --- Technical / Documentation ---
\omnilatex@matchdoctypes{software-documentation,softwaredocumentation,sw-docs}{\omnilatex@setdoctype{software-documentation}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{api-reference,apireference,apidocs}{\omnilatex@setdoctype{api-reference}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{changelog,change-log,release-notes,releasenotes}{\omnilatex@setdoctype{changelog}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{technical-spec,technicalspec,tech-spec}{\omnilatex@setdoctype{technical-spec}{scrreprt}{\omnilatex@reportoptions}}%
% --- Creative / Lifestyle ---
\omnilatex@matchdoctypes{blog-post,blogpost,article-web}{\omnilatex@setdoctype{blog-post}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{newsletter,newsletters}{\omnilatex@setdoctype{newsletter}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{brochure,brochures}{\omnilatex@setdoctype{brochure}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{invitation,invitations,invitation-card}{\omnilatex@setdoctype{invitation}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{program,programme,event-programme}{\omnilatex@setdoctype{program}{scrartcl}{\omnilatex@articleoptions}}%
% --- Government / Legal ---
\omnilatex@matchdoctypes{legislation,act,statute}{\omnilatex@setdoctype{legislation}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{regulation,regulations,rules}{\omnilatex@setdoctype{regulation}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{annual-report,annualreport}{\omnilatex@setdoctype{annual-report}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{case-study,casestudy}{\omnilatex@setdoctype{case-study}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{whitepaper,white-paper-report}{\omnilatex@setdoctype{whitepaper}{scrreprt}{\omnilatex@reportoptions}}%
% --- Academic / Research (expanded) ---
\omnilatex@matchdoctypes{conference-paper,conferencepaper,conf-paper}{\omnilatex@setdoctype{conference-paper}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{meta-analysis,metaanalysis,systematic-review}{\omnilatex@setdoctype{meta-analysis}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{research-notebook,researchnotebook,lab-notebook}{\omnilatex@setdoctype{research-notebook}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{clinical-report,clinicalreport,clinical-study}{\omnilatex@setdoctype{clinical-report}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{data-sheet,datasheet,material-safety,msds}{\omnilatex@setdoctype{data-sheet}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{experiment-log,experimentlog,lab-journal}{\omnilatex@setdoctype{experiment-log}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{survey-report,surveyreport,survey-analysis}{\omnilatex@setdoctype{survey-report}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{review-article,reviewarticle,reviews}{\omnilatex@setdoctype{review-article}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{dissertation-proposal,dissertationproposal,phd-proposal}{\omnilatex@setdoctype{dissertation-proposal}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{postdoc-report,postdocreport,fellowship-report}{\omnilatex@setdoctype{postdoc-report}{scrreprt}{\omnilatex@reportoptions}}%
% --- Business / Professional (expanded) ---
\omnilatex@matchdoctypes{business-plan,businessplan,bizplan}{\omnilatex@setdoctype{business-plan}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{market-analysis,marketanalysis,market-report}{\omnilatex@setdoctype{market-analysis}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{financial-report,financialreport,finance-report}{\omnilatex@setdoctype{financial-report}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{employee-handbook,employeehandbook,hr-handbook}{\omnilatex@setdoctype{employee-handbook}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{onboarding-guide,onboardingguide,new-hire-guide}{\omnilatex@setdoctype{onboarding-guide}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{performance-review,performancereview,appraisal}{\omnilatex@setdoctype{performance-review}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{project-charter,projectcharter,charter}{\omnilatex@setdoctype{project-charter}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{risk-assessment,riskassessment,risk-report}{\omnilatex@setdoctype{risk-assessment}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{stakeholder-report,stakeholderreport,investor-report}{\omnilatex@setdoctype{stakeholder-report}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{pitch-deck,pitchdeck,investor-deck}{\omnilatex@setdoctype{pitch-deck}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{press-release,pressrelease,pr}{\omnilatex@setdoctype{press-release}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{media-kit,mediakit,press-kit}{\omnilatex@setdoctype{media-kit}{scrreprt}{\omnilatex@reportoptions}}%
% --- Technical / Documentation (expanded) ---
\omnilatex@matchdoctypes{user-guide,userguide,ug}{\omnilatex@setdoctype{user-guide}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{developer-guide,developerguide,devguide}{\omnilatex@setdoctype{developer-guide}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{operations-manual,operationsmanual,ops-manual}{\omnilatex@setdoctype{operations-manual}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{architecture-document,architecturedocument,arch-doc}{\omnilatex@setdoctype{architecture-document}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{design-document,designdocument,design-spec}{\omnilatex@setdoctype{design-document}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{test-plan,testplan,test-specification}{\omnilatex@setdoctype{test-plan}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{deployment-guide,deploymentguide,deploy-guide}{\omnilatex@setdoctype{deployment-guide}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{troubleshooting-guide,troubleshootingguide,triage-guide}{\omnilatex@setdoctype{troubleshooting-guide}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{coding-standards,codingstandards,style-guide,styleguide}{\omnilatex@setdoctype{coding-standards}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{data-dictionary,datadictionary,data-model}{\omnilatex@setdoctype{data-dictionary}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{system-design,systemdesign,system-architecture}{\omnilatex@setdoctype{system-design}{scrreprt}{\omnilatex@reportoptions}}%
% --- Legal / Government (expanded) ---
\omnilatex@matchdoctypes{contract,contracts,agreement}{\omnilatex@setdoctype{contract}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{terms-of-service,termsofservice,tos,eula}{\omnilatex@setdoctype{terms-of-service}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{privacy-policy,privacypolicy,data-protection}{\omnilatex@setdoctype{privacy-policy}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{legal-brief,legalbrief,brief,memo-of-law}{\omnilatex@setdoctype{legal-brief}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{court-filing,courtfiling,pleading}{\omnilatex@setdoctype{court-filing}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{affidavit,affidavits}{\omnilatex@setdoctype{affidavit}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{compliance-document,compliancedocument,compliance-report}{\omnilatex@setdoctype{compliance-document}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{policy-document,policydocument,policy}{\omnilatex@setdoctype{policy-document}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{public-comment,publiccomment,regulatory-comment}{\omnilatex@setdoctype{public-comment}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{impact-report,impactreport,social-impact}{\omnilatex@setdoctype{impact-report}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{audit-report,auditreport,audit}{\omnilatex@setdoctype{audit-report}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{feasibility-study,feasibilitystudy,feasibility}{\omnilatex@setdoctype{feasibility-study}{scrreprt}{\omnilatex@reportoptions}}%
% --- Creative / Lifestyle (expanded) ---
\omnilatex@matchdoctypes{novel,novels,fiction}{\omnilatex@setdoctype{novel}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{short-story,shortstory,stories}{\omnilatex@setdoctype{short-story}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{poetry-collection,poetrycollection,poetry,poems}{\omnilatex@setdoctype{poetry-collection}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{screenplay,screenplay,script-film}{\omnilatex@setdoctype{screenplay}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{comic-book,comicbook,graphic-novel}{\omnilatex@setdoctype{comic-book}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{zine,zines,fanzine}{\omnilatex@setdoctype{zine}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{art-catalogue,artcatalogue,exhibition-catalogue}{\omnilatex@setdoctype{art-catalogue}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{photo-book,photobook,photo-album}{\omnilatex@setdoctype{photo-book}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{travel-guide,travelguide,travel}{\omnilatex@setdoctype{travel-guide}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{greeting-card,greetingcard,card}{\omnilatex@setdoctype{greeting-card}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{wedding-invitation,weddinginvitation}{\omnilatex@setdoctype{wedding-invitation}{scrartcl}{\omnilatex@articleoptions}}%
% --- Education (expanded) ---
\omnilatex@matchdoctypes{flashcards,flash-cards,study-cards}{\omnilatex@setdoctype{flashcards}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{study-guide,studyguide,revision-guide}{\omnilatex@setdoctype{study-guide}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{curriculum,curricula,syllabus-collection}{\omnilatex@setdoctype{curriculum}{scrreprt}{\omnilatex@reportoptions}}%
\omnilatex@matchdoctypes{activity-book,activitybook,workbook}{\omnilatex@setdoctype{activity-book}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{workbook,workbooks,exercise-book}{\omnilatex@setdoctype{workbook}{scrbook}{\omnilatex@bookoptions}}%
% --- Personal / Lifestyle ---
\omnilatex@matchdoctypes{journal,journals,diary,diaries}{\omnilatex@setdoctype{journal}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{recipe-book,recipebook,cookbook,cook-book}{\omnilatex@setdoctype{recipe-book}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{personal-portfolio,portfolio,portfolio-book}{\omnilatex@setdoctype{personal-portfolio}{scrbook}{\omnilatex@bookoptions}}%
\omnilatex@matchdoctypes{family-tree,familytree,genealogy}{\omnilatex@setdoctype{family-tree}{scrartcl}{\omnilatex@articleoptions}}%
% --- Media / Content ---
\omnilatex@matchdoctypes{podcast-script,podcastscript,podcast}{\omnilatex@setdoctype{podcast-script}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{video-script,videoscript,youtube-script}{\omnilatex@setdoctype{video-script}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{advertising-copy,advertisingcopy,ad-copy,adcopy}{\omnilatex@setdoctype{advertising-copy}{scrartcl}{\omnilatex@articleoptions}}%
% --- Religious / Spiritual ---
\omnilatex@matchdoctypes{sermon,sermons,homily}{\omnilatex@setdoctype{sermon}{scrartcl}{\omnilatex@articleoptions}}%
\omnilatex@matchdoctypes{liturgy,liturgies,worship}{\omnilatex@setdoctype{liturgy}{scrreprt}{\omnilatex@reportoptions}}%
% --- Beamer ---
\omnilatex@matchdoctypes{beamer,beamers}{\omnilatex@setdoctype{beamer}{beamer}{\omnilatex@beameraoptions}\omnilatex@beamertrue}%

% Validate doctype: warn if user passed an unknown doctype that didn't match
\ifomnilatex@doctypematched\else
    \ClassWarning{omnilatex}{Unknown doctype '\omnilatex@doctype'.%
        Falling back to 'book'. Valid options: book, thesis, dissertation,%
        manual, guide, handbook, report, technicalreport, standard, patent,%
        article, inlinepaper, journal, dictionary, cv, cover-letter, poster,%
        presentation, letter, homework, exam, research-proposal, recipe,%
        lecture-notes, syllabus, handout, memo, white-paper, invoice, beamer,%
        grant-proposal, ieee, book-chapter, lab-report, literature-review,%
        thesis-proposal, annotated-bibliography, proceedings, preprint,%
        working-paper, business-letter, meeting-minutes, quarterly-report,%
        strategic-plan, product-spec, course-material, course-notes,%
        textbook, quiz, lesson-plan, software-documentation, api-reference,%
        changelog, technical-spec, blog-post, newsletter, brochure,%
        invitation, program, legislation, regulation, annual-report,%
        case-study, conference-paper, meta-analysis, research-notebook,%
        clinical-report, data-sheet, experiment-log, survey-report,%
        review-article, dissertation-proposal, postdoc-report,%
        business-plan, market-analysis, financial-report,%
        employee-handbook, onboarding-guide, performance-review,%
        project-charter, risk-assessment, stakeholder-report,%
        pitch-deck, press-release, media-kit, user-guide,%
        developer-guide, operations-manual, architecture-document,%
        design-document, test-plan, deployment-guide,%
        troubleshooting-guide, coding-standards, data-dictionary,%
        system-design, contract, terms-of-service, privacy-policy,%
        legal-brief, court-filing, affidavit, compliance-document,%
        policy-document, public-comment, impact-report, audit-report,%
        feasibility-study, novel, short-story, poetry-collection,%
        screenplay, comic-book, zine, art-catalogue, photo-book,%
        travel-guide, greeting-card, wedding-invitation, flashcards,%
        study-guide, curriculum, activity-book, workbook, journal,%
        recipe-book, personal-portfolio, family-tree, podcast-script,%
        video-script, advertising-copy, sermon, liturgy}%
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
    \ClassWarning{omnilatex}{Unknown~titlestyle~'\omnilatex@titlestyle'.~
        Using~default~title~page~layout.}
}
\ExplSyntaxOff

\ifomnilatex@beamer
    \ifx\omnilatexuserclassoptions\@empty\else
        \PassOptionsToClass{\omnilatexuserclassoptions}{\@baseclass}
    \fi
    \PassOptionsToClass{aspectratio=\omnilatex@beameraspectratio}{\@baseclass}
\else
    \ifx\omnilatexuserclassoptions\@empty
        \PassOptionsToClass{\omnilatexclassoptions}{\@baseclass}
    \else
        \PassOptionsToClass{\omnilatexclassoptions,\omnilatexuserclassoptions}{\@baseclass}
    \fi
\fi

\LoadClass{\@baseclass}

% Warn if user loads packages known to conflict with KOMA-Script.
\AddToHook{package/geometry/after}{%
  \ClassWarning{omnilatex}{geometry loaded — KOMA's typearea is in use.
    Use \string\KOMAoptions{DIV=calc,BCOR=...} instead of geometry}%
}
\AddToHook{package/fancyhdr/after}{%
  \ClassWarning{omnilatex}{fancyhdr loaded — KOMA's scrlayer-scrpage is in use.
    Use \string\setkomafont{pagehead} and \string\setkomafont{pagefoot}}%
}
\AddToHook{package/tocloft/after}{%
  \ClassWarning{omnilatex}{tocloft loaded — KOMA's tocbasic is in use.
    Use \string\setuptoc{toc}{...} and \string\DeclareTOCStyleEntries}%
}
\AddToHook{package/titlesec/after}{%
  \ClassWarning{omnilatex}{titlesec loaded — KOMA-Script disables its
    sectioning when titlesec is detected. Use \string\addtokomafont{section}
    and \string\RedeclareSectionCommand instead}%
}

% silence + etex packages removed: callback.register() deprecated in TL2026
% LuaTeX includes etex functionality natively; explicit loading causes errors
% LuaTeX: suppress non-fatal "Counter too large" errors.
% These come from bib2gls .glstex files in large documents
% (254+ pages).  PDF output is correct — errors are cosmetic.
% Use luatexbase.add_to_callback (modern API) instead of callback.register (deprecated).
\ifluatex
  \directlua{
    local ok, luatexbase = pcall(require, "luatexbase")
    if ok then
      luatexbase.add_to_callback("show_error_hook", function()
        local e = status.lasterrorstring or ""
        if string.find(e, "Counter too large") then
          texio.write("log", "(OmniLaTeX: counter too large suppressed)")
          return true
        end
        return false
      end, "omnilatex: suppress counter too large")
    else
      -- Fallback: use raw callback.register if luatexbase not available
      callback.register("show_error_hook", function()
        local e = status.lasterrorstring or ""
        if string.find(e, "Counter too large") then
          texio.write("log", "(OmniLaTeX: counter too large suppressed)")
          return true
        end
        return false
      end)
    end
  }
\fi

% Load Beamer integration module when doctype=beamer
\ifomnilatex@beamer
    \RequirePackage{lib/graphics/omnilatex-beamer}
\fi

\RequirePackage[\omnilatex@language]{tracklang}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Load Core Modules (Always)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Core modules (always loaded)
\RequirePackage{lib/core/omnilatex-base}
\RequirePackage{lib/utils/omnilatex-colors}
\RequirePackage{lib/utils/omnilatex-utils}
\RequirePackage{lib/typography/omnilatex-fonts}
% omnilatex-lists uses enumitem which conflicts with beamer's list handling
\ifomnilatex@beamer\else
    \ifomnilatex@enablelayout
        \RequirePackage{lib/typography/omnilatex-lists}
    \fi
\fi
\RequirePackage{lib/typography/omnilatex-typesetting}
% KOMA-Script layout modules are incompatible with beamer base class
\ifomnilatex@beamer\else
    \ifomnilatex@enablelayout
        \RequirePackage{lib/layout/omnilatex-page}
        \RequirePackage{lib/layout/omnilatex-koma}
        \RequirePackage{lib/layout/omnilatex-floats}
        \RequirePackage{lib/layout/omnilatex-boxes}
        \RequirePackage{lib/layout/omnilatex-document}
    \fi
\fi
% Doctype-specific modules are loaded conditionally after core layouts.
\IfStrEq{\omnilatex@doctype}{presentation}{%
  \RequirePackage{lib/layout/omnilatex-presentation}%
}{}%
\IfStrEq{\omnilatex@doctype}{poster}{%
  \RequirePackage{lib/layout/omnilatex-presentation}%
}{}%
% Beamer loads its own hyperref; skip our hyperref module to avoid option clash
\ifomnilatex@beamer\else
    \ifomnilatex@enablehyperref
        \RequirePackage{lib/references/omnilatex-hyperref}
    \fi
\fi
% Workaround: luaotfload-multiscript.lua calls kpse.find_file('ScriptExtensions.txt')
% which returns nil in Nix/TL2025, then calls os.exit(-1). Patch kpse.find_file
% to return a dummy temp file when the real file is missing.
\directlua{dofile(kpse.find_file("lib/utils/omnilatex-luaotfload-workaround.lua") or "lib/utils/omnilatex-luaotfload-workaround.lua")}%

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
  \omnilatex@check@cjk@lang{simplifiedchinese}%
  \omnilatex@check@cjk@lang{traditionalchinese}%
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
  \omnilatex@check@cjk@sf@lang{simplifiedchinese}%
  \omnilatex@check@cjk@sf@lang{traditionalchinese}%
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
    \IfFontExistsTF{Amiri}{%
      \newfontfamily\arabicfont[Script=Arabic,BoldFont=Amiri,BoldFeatures={FakeBold=2}]{Amiri}%
      \newfontfamily\arabicfontfamily[Script=Arabic,BoldFont=Amiri,BoldFeatures={FakeBold=2}]{Amiri}%
      \newfontfamily\arabicfontsf[Script=Arabic,BoldFont=Amiri,BoldFeatures={FakeBold=2}]{Amiri}%
    }{%
      \IfFontExistsTF{Noto Naskh Arabic}{%
        \newfontfamily\arabicfont[Script=Arabic,BoldFont=Noto Naskh Arabic,BoldFeatures={FakeBold=2}]{Noto Naskh Arabic}%
        \newfontfamily\arabicfontfamily[Script=Arabic,BoldFont=Noto Naskh Arabic,BoldFeatures={FakeBold=2}]{Noto Naskh Arabic}%
        \newfontfamily\arabicfontsf[Script=Arabic,BoldFont=Noto Naskh Arabic,BoldFeatures={FakeBold=2}]{Noto Naskh Arabic}%
      }{}%
    }%
  }{}%
}{}%
\@ifundefined{persianfont}{%
  \IfStrEq{\omnilatex@language}{persian}{%
    \IfFontExistsTF{Amiri}{%
      \newfontfamily\persianfont[Script=Arabic,BoldFont=Amiri,BoldFeatures={FakeBold=2}]{Amiri}%
      \newfontfamily\persianfontfamily[Script=Arabic,BoldFont=Amiri,BoldFeatures={FakeBold=2}]{Amiri}%
      \newfontfamily\persianfontsf[Script=Arabic,BoldFont=Amiri,BoldFeatures={FakeBold=2}]{Amiri}%
    }{%
      \IfFontExistsTF{Noto Naskh Arabic}{%
        \newfontfamily\persianfont[Script=Arabic,BoldFont=Noto Naskh Arabic,BoldFeatures={FakeBold=2}]{Noto Naskh Arabic}%
        \newfontfamily\persianfontfamily[Script=Arabic,BoldFont=Noto Naskh Arabic,BoldFeatures={FakeBold=2}]{Noto Naskh Arabic}%
        \newfontfamily\persianfontsf[Script=Arabic,BoldFont=Noto Naskh Arabic,BoldFeatures={FakeBold=2}]{Noto Naskh Arabic}%
      }{}%
    }%
  }{}%
}{}%
\@ifundefined{hebrewfont}{%
  \IfStrEq{\omnilatex@language}{hebrew}{%
    \IfFontExistsTF{David CLM}{%
      \newfontfamily\hebrewfont[Script=Hebrew,BoldFont=David CLM,BoldFeatures={FakeBold=2}]{David CLM}%
      \newfontfamily\hebrewfontfamily[Script=Hebrew,BoldFont=David CLM,BoldFeatures={FakeBold=2}]{David CLM}%
      \newfontfamily\hebrewfontsf[Script=Hebrew,BoldFont=David CLM,BoldFeatures={FakeBold=2}]{David CLM}%
      \setsansfont[Script=Hebrew,BoldFont=David CLM,BoldFeatures={FakeBold=2}]{David CLM}%
    }{%
      \IfFontExistsTF{Frank Ruehl CLM}{%
        \newfontfamily\hebrewfont[Script=Hebrew,BoldFont=Frank Ruehl CLM,BoldFeatures={FakeBold=2}]{Frank Ruehl CLM}%
        \newfontfamily\hebrewfontfamily[Script=Hebrew,BoldFont=Frank Ruehl CLM,BoldFeatures={FakeBold=2}]{Frank Ruehl CLM}%
        \newfontfamily\hebrewfontsf[Script=Hebrew,BoldFont=Frank Ruehl CLM,BoldFeatures={FakeBold=2}]{Frank Ruehl CLM}%
        \setsansfont[Script=Hebrew,BoldFont=Frank Ruehl CLM,BoldFeatures={FakeBold=2}]{Frank Ruehl CLM}%
      }{%
        \IfFontExistsTF{Noto Sans Hebrew}{%
          \newfontfamily\hebrewfont[Script=Hebrew,BoldFont=Noto Sans Hebrew,BoldFeatures={FakeBold=2}]{Noto Sans Hebrew}%
          \newfontfamily\hebrewfontfamily[Script=Hebrew,BoldFont=Noto Sans Hebrew,BoldFeatures={FakeBold=2}]{Noto Sans Hebrew}%
          \newfontfamily\hebrewfontsf[Script=Hebrew,BoldFont=Noto Sans Hebrew,BoldFeatures={FakeBold=2}]{Noto Sans Hebrew}%
          \setsansfont[Script=Hebrew,BoldFont=Noto Sans Hebrew,BoldFeatures={FakeBold=2}]{Noto Sans Hebrew}%
        }{}%
      }{}%
    }%
  }{}%
}{}%

\RequirePackage{lib/language/omnilatex-i18n}

% Auto-load CJK support for Chinese, Japanese, Korean
\def\omnilatex@cjk@check@lang#1{%
  \IfStrEq{\omnilatex@language}{#1}{\RequirePackage{lib/language/omnilatex-cjk}}{}%
}
\omnilatex@cjk@check@lang{chinese}%
\omnilatex@cjk@check@lang{simplifiedchinese}%
\omnilatex@cjk@check@lang{traditionalchinese}%
\omnilatex@cjk@check@lang{japanese}%
\omnilatex@cjk@check@lang{korean}%

% Auto-load RTL support for Arabic, Persian, Hebrew
\def\omnilatex@rtl@check@lang#1{%
  \IfStrEq{\omnilatex@language}{#1}{\RequirePackage{lib/language/omnilatex-rtl}}{}%
}
\omnilatex@rtl@check@lang{arabic}%
\omnilatex@rtl@check@lang{persian}%
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
% Ensure csquotes is loaded after fvextra (loaded by omnilatex-tables).
% omnilatex-typesetting loads csquotes early; re-require here to
% satisfy the load-order warning ("csquotes should be loaded after fvextra").
\RequirePackage{csquotes}
\ifomnilatex@loadGlossaries
    \RequirePackage{lib/references/omnilatex-glossary}
\fi
% Bibliography module uses KOMA-specific features; skip for beamer
\ifomnilatex@beamer\else
    \ifomnilatex@enablebibliography
        \RequirePackage{lib/references/omnilatex-biblio}
        \RequirePackage{lib/references/omnilatex-citations}
    \fi
\fi

% Plugin system (always available)
\RequirePackage{lib/utils/omnilatex-plugin}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Graceful degradation stubs for disabled modules
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% When a module group is disabled, provide no-op stubs for its most common
% commands so that downstream code (e.g. doctype profiles, user documents)
% does not produce hard errors.  Each stub is only defined if the real
% command does not already exist (via \providecommand or \@ifundefined).

\ifomnilatex@enablehyperref\else
    % hyperref stubs
    \providecommand{\hypersetup}[1]{}
    \providecommand{\href}[2]{#2}
    \providecommand{\url}[1]{\texttt{#1}}
    \providecommand{\texorpdfstring}[2]{#2}
    % cleveref stubs (loaded by hyperref module)
    \providecommand{\cref}[1]{}
    \providecommand{\Cref}[1]{}
    \providecommand{\crefname}[3]{}
    \providecommand{\Crefname}[3]{}
    \providecommand{\crefrange}[2]{}
    \providecommand{\autoref}[1]{}
\fi

\ifomnilatex@enablebibliography\else
    % biblatex stubs
    \providecommand{\cite}[1]{}
    \providecommand{\parencite}[1]{}
    \providecommand{\footcite}[1]{}
    \providecommand{\textcite}[1]{}
    \providecommand{\autocite}[1]{}
    \providecommand{\fullcite}[1]{}
    \providecommand{\nocite}[1]{}
    \providecommand{\printbibliography}[1]{}
    \providecommand{\addbibresource}[1]{}
\fi

\ifomnilatex@enablelayout\else
    % KOMA/layout stubs used by doctype profiles
    \providecommand{\addtokomafont}[2]{}
    \providecommand{\setkomafont}[2]{}
    \providecommand{\usekomafont}[1]{}
    \providecommand{\KOMAoptions}[1]{}
    \providecommand{\addpart}[1]{}
\fi

\def\@doctypefile{}
\edef\@doctypecandidate{config/document-types/omnilatex-doctype-\omnilatex@doctypeprofile}
\IfFileExists{\@doctypecandidate.sty}{\edef\@doctypefile{\@doctypecandidate}}{%
    \IfFileExists{config/document-types/\omnilatex@doctypeprofile/omnilatex-doctype-\omnilatex@doctypeprofile.sty}{%
        \edef\@doctypefile{config/document-types/\omnilatex@doctypeprofile/omnilatex-doctype-\omnilatex@doctypeprofile}%
    }{}
}
\ifx\@doctypefile\@empty\else\RequirePackage{\@doctypefile}\fi

% Load todo-tracker if todonotes option is enabled
\ifomnilatex@todonotes
    \RequirePackage{lib/utils/omnilatex-todo}
\fi

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
