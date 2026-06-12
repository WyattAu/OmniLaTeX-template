# Part II: Document Types — Detailed Chapter Plans

---

## Chapter 20: Articles & Short Documents

**Purpose:** Cover all scrartcl-based short document types.

### 20.0 KOMA scrartcl Foundation

All article-type documents in OmniLaTeX use KOMA-Script's `scrartcl` class as their base. The class is loaded with these default options (defined in `omnilatex.cls`):

```latex
\omnilatex@articleoptions = bibliography=totoc, numbers=noenddot, parskip=half
```

Key scrartcl-specific features inherited by all article doctypes:

- No `\chapter` command (sections are the top-level division)
- `\tableofcontents` is section-level (no chapter prefix)
- `parskip=half` by default (paragraph spacing instead of indentation)
- `titlepage=true` for most article variants

### 20.1 Article Structure Guide

The standard article doctype (`doctype=article`) provides this structure:

```latex
\documentclass[doctype=article]{omnilatex}

\title{Article Title}
\author{Author Name}
\date{\today}
\subtitle{Abstract text goes here (reused as abstract on title page)}
\keywords{keyword1, keyword2}
\doi{10.1234/example}
\contact{author@example.com}
\affiliation{Department of Example, University of Examples}

\begin{document}
\maketitle

\section{Introduction}
Article content here.

\section{Methods}
\subsection{Experimental Setup}
Details of the methodology.

\section{Results}
Results with a TikZ figure:

\begin{figure}[htbp]
    \centering
    \begin{tikzpicture}
        \draw[thick] (0,0) -- (4,3);
    \end{tikzpicture}
    \caption{Example figure.}
    \label{fig:example}
\end{figure}

As shown in \cref{fig:example}, the results demonstrate...

\section{Conclusion}
Summary of findings.

\printbibliography
\end{document}
```

**Article-specific commands:**

| Command | Default | Description |
|---|---|---|
| `\subtitle{text}` | (empty) | Also used as abstract on the title page |
| `\keywords{text}` | `n/a` | Keyword list for the title page |
| `\doi{text}` | `pending` | Digital object identifier |
| `\contact{text}` | (empty) | Contact email |
| `\affiliation{text}` | `Independent Researcher` | Author affiliation block |

**Article profile settings** (from `article.sty`):

- Font size: `11pt`
- Layout: `DIV=12, headinclude=false, footinclude=false`
- Line spacing: `onehalf`
- Section numbering depth: `secnumdepth=3`, `tocdepth=2`
- Citation style: `ieee`

### 20.2 Journal

- Custom commands: `\journalname`, `\journalvolume`, `\journalissue`, `\journalpages`, `\doi`, `\articletype`, `\highlights`, `\receiveddate`, `\accepteddate`, `\publisheddate`
- Best for: academic journal submissions
- Example: journal article with wave function plots

### 20.3 Inline Paper

- Custom commands: `\affiliation`, `\contact`, `\supplementary`, `\keywords`
- Two-column layout (arXiv-style)
- KOMA options: `titlepage=false` (no separate title page)
- Best for: conference papers, arXiv preprints
- Example: compact two-column paper

### 20.4 White Paper

- Custom commands: `\wptitle`, `\wporganization`, `\wpdate`, `\wpversion`, `\wpconfidential`, `\wpcontact`
- Environments: `whitepaperabstract`, `\callout{title}{text}`, `keytakeaways`
- Best for: industry white papers, policy documents
- Example: technology white paper with callouts

### 20.5 Letter

- Custom commands: `\letterrecipient`, `\lettersubject`, `\letterdate`, `\letteropening`, `\lettersender`, `\letterclosing`
- `\letterclosingblock` env
- Best for: formal correspondence, cover letters
- Example: formal letter with closing block

### 20.6 Cover Letter

- Custom commands: `\clrecipient`, `\clposition`, `\clcompany`, `\cldate`
- Best for: job applications
- Also see: `examples/cover-letter-formal/` variant

**Cross-refs:** Chapter 14 (doctype system), Chapter 30 (fonts), Chapter 70 (bibliography)

---

## Chapter 21: Reports & Long Documents

**Purpose:** Cover all scrreprt-based report types.

### 21.0 scrreprt vs scrbook vs scrartcl

OmniLaTeX's three KOMA base classes serve different document lengths:

| Feature | scrartcl (Articles) | scrreprt (Reports) | scrbook (Books) |
|---|---|---|---|
| Top-level division | `\section` | `\chapter` | `\chapter` |
| Two-sided default | No | No (open=any) | Yes (open=right) |
| Chapter prefix | N/A | No (`chapterprefix=false`) | Yes (`chapterprefix=true`) |
| Bibliography in TOC | Yes | Yes | Yes |
| Best for | < 20 pages | 20-100 pages | > 100 pages |

Report doctypes use these default KOMA options:

```latex
\omnilatex@reportoptions = listof=totoc, bibliography=totoc,
    chapterprefix=false, open=any, numbers=noenddot
```

### 21.1 Technical Report Structure Guide

The `doctype=technicalreport` (also aliased as `report`, `technical-report`, `techreport`, `tech-report`) uses `scrreprt` and provides:

```latex
\documentclass[doctype=technicalreport]{omnilatex}

\title{Thermal Analysis of Heat Exchanger Network}
\reportnumber{TR-2026-042}
\revision{B}
\preparedby{Jane Doe, John Smith}
\client{Acme Industrial}
\projectname{HEX Optimization Phase II}
\confidentiality{Internal Use Only}
\sponsor{Dr. Alice Johnson}
\leadengineer{Bob Williams}
\doccontrol{Carol Davis}
\distribution{Distribution authorized to project stakeholders.}
\date{May 2026}

\begin{document}
\maketitle

\tableofcontents

\chapter{Introduction}
\section{Background}
\section{Objectives}

\chapter{Methodology}
\section{System Description}
\section{Simulation Setup}

\chapter{Results}
\section{Performance Metrics}
\section{Sensitivity Analysis}

\chapter{Conclusions and Recommendations}

\appendix
\chapter{Raw Data}

\printbibliography
\end{document}
```

**Technical report commands:**

| Command | Default | Description |
|---|---|---|
| `\reportnumber{text}` | `TR-000` | Report identification number |
| `\revision{text}` | `A` | Document revision letter |
| `\preparedby{text}` | `Analysis Group` | Author(s) |
| `\client{text}` | `Client Organization` | Client name |
| `\projectname{text}` | `Project Name` | Project identifier |
| `\confidentiality{text}` | `Internal Use Only` | Classification level |
| `\sponsor{text}` | `Name` | Executive sponsor |
| `\leadengineer{text}` | `Name` | Lead engineer |
| `\doccontrol{text}` | `Name` | Document control contact |
| `\distribution{text}` | `Distribution authorized...` | Distribution statement |

**Technical report profile settings:**

- KOMA options: `titlepage=true, twoside=false`
- Section depth: `secnumdepth=3`, `tocdepth=2`
- Citation style: `ieee`

### 21.2 Research Proposal Structure Guide

The `doctype=research-proposal` (also aliased as `researchproposal`, `research-proposals`) uses `scrreprt` with `chapterprefix=false, open=any`:

```latex
\documentclass[doctype=research-proposal]{omnilatex}

\title{Deep Learning for Thermal System Optimization}
\propprogram{Horizon Europe}
\propcall{HORIZON-CL4-2026-ENERGY}
\propduration{36 months}
\propbudget{EUR 2,400,000}
\propstartdate{2027-01-01}
\propenddate{2029-12-31}
\propinvestigator{Prof. Jane Doe}
\propcoinvestigators{Dr. Alice Johnson, Dr. Bob Williams}
\proporganization{Technical University}

\begin{document}
\maketitle

\tableofcontents

\chapter{Abstract}
\propabstract{This proposal outlines a novel approach...}

\chapter{State of the Art}
\chapter{Objectives}
\chapter{Methodology}
\chapter{Work Plan and Timeline}
\chapter{Budget Justification}
\chapter{Impact}
\chapter{Team and Consortium}

\printbibliography
\end{document}
```

**Research proposal commands:**

| Command | Default | Description |
|---|---|---|
| `\propabstract{text}` | (empty) | Project abstract |
| `\propprogram{text}` | `Funding Program` | Funding program name |
| `\propcall{text}` | (empty) | Call identifier |
| `\propduration{text}` | `24 months` | Project duration |
| `\propbudget{text}` | (empty) | Total budget |
| `\propstartdate{text}` | `TBD` | Start date |
| `\propenddate{text}` | `TBD` | End date |
| `\propinvestigator{text}` | `PI Name` | Principal investigator |
| `\propcoinvestigators{text}` | `None` | Co-investigators |
| `\proporganization{text}` | `Institution` | Host organization |

### 21.3 Standard

- Custom commands: `\standardseries`, `\standarddesignation`, `\standardstatus`, `\standardscope`, `\standardcommittee`, `\standardsupersedes`, `\standardics`, `\standardkeywords`, `\standarddisclaimer`
- Custom section numbering (no chapter prefix, pure arabic)
- KOMA options: `titlepage=true, twoside=false, parskip=half`
- Best for: ISO/IEC standards documents
- Profile overrides `\thesection`, `\thesubsection`, `\thesubsubsection` to pure arabic numbering (e.g., "1.2.3" instead of "Chapter 1 / Section 2 / Subsection 3")

### 21.4 Patent

- KOMA scrreprt base with `titlepage=true, twoside=false`
- Best for: patent specifications, IP documentation

### 21.5 Manual

- Custom commands: `\manualbrand`, `\manualversion`, `\manualreleasedate`, `\manualsupport`, `\manualsummary`
- Font mode: sans-serif (`documentfontmode=sans`)
- Color mode: black-and-white (`documentcolormode=bw`)
- Link style: black (`documentlinkstyle=black`)
- Citation style: `chicago`
- Best for: software documentation, user guides
- Example: this very manual uses `doctype=manual`

**Cross-refs:** Chapter 14, Chapter 50 (page layout), Chapter 62 (tables)

---

## Chapter 22: Theses & Dissertations

**Purpose:** Cover all scrbook-based long document types.

### 22.0 Thesis vs Dissertation Distinction

In OmniLaTeX, "thesis" and "dissertation" are distinct doctypes with different metadata fields and title page layouts:

| Aspect | Thesis | Dissertation |
|---|---|---|
| Degree level | BSc, MSc, MEng | PhD, DSc, Dr.-Ing. |
| Supervisor field | `\thesisadvisor` (single) | `\firstsupervisor` + `\secondsupervisor` |
| Committee | `\thesiscommittee` | `\dissertationcommittee` |
| Defense date | `\defensedate` | N/A |
| Submission date | N/A | `\submissiondate` |
| Location | `\thesislocation` | N/A |
| Section depth | `secnumdepth=2` | `secnumdepth=3` |
| Font size | `12pt` | (class default) |
| Layout | `DIV=12, twoside` | `twoside` |
| KOMA options | `chapterprefix=true, open=right` | `chapterprefix=true, open=right` |

Both use `scrbook` as their base class with:

```latex
\omnilatex@bookoptions = listof=totoc, bibliography=totoc,
    chapterprefix=true, open=right, numbers=noenddot
```

### 22.1 Thesis Structure Template

```latex
\documentclass[doctype=thesis]{omnilatex}

\title{Optimization of Heat Exchanger Networks Using Machine Learning}
\author{Jane Doe}
\date{May 2026}

\thesisinstitution{Technical University of Hamburg}
\thesisdepartment{Institute of Thermodynamics}
\thesisdegree{Master of Science}
\thesisadvisor{Prof. Dr. John Smith}
\thesiscommittee{Dr. Alice Johnson, Dr. Bob Williams}
\defensedate{2026-06-15}
\thesislocation{Hamburg, Germany}

\begin{document}

\frontmatter
\maketitle

\tableofcontents
\listoffigures
\listoftables
\listoflistings

\chapter{Declaration of Authorship}
I hereby declare that this thesis...

\chapter{Abstract}
This thesis presents...

\mainmatter

\chapter{Introduction}
\section{Motivation}
\section{Objectives}
\section{Outline}

\chapter{Theoretical Background}
\section{Heat Exchanger Theory}
\section{Machine Learning Fundamentals}

\chapter{Methodology}
\section{Data Collection}
\section{Model Development}

\chapter{Results and Discussion}
\section{Model Performance}
\section{Comparison with Literature}

\chapter{Conclusions and Outlook}

\appendix
\chapter{Supplementary Data}
\chapter{Source Code}

\printbibliography

\end{document}
```

**Thesis commands:**

| Command | Default | Description |
|---|---|---|
| `\thesisinstitution{text}` | `University` | University name |
| `\thesisdepartment{text}` | `Department` | Department name |
| `\thesisdegree{text}` | `Master of Science` | Degree being awarded |
| `\thesisadvisor{text}` | `Advisor Name` | Primary advisor |
| `\thesiscommittee{text}` | `Committee Member A, ...` | Committee members |
| `\defensedate{text}` | `\today` | Oral defense date |
| `\thesislocation{text}` | `City, Country` | Institution location |

### 22.2 Dissertation Structure Template

```latex
\documentclass[doctype=dissertation]{omnilatex}

\title{Contributions to the Theory of Renewable Energy Systems}
\author{Jane Doe}

\dissertationdegree{Doctor of Philosophy}
\dissertationdepartment{Department of Electrical Engineering}
\dissertationinstitution{Technical University}
\firstsupervisor{Prof. Dr. John Smith}
\secondsupervisor{Prof. Dr. Alice Johnson}
\dissertationcommittee{Dr. Bob Williams, Dr. Carol Davis}
\submissiondate{2026-05-15}
\keywords{renewable energy, power systems, optimization}

\begin{document}

\frontmatter
\maketitle

\chapter{Declaration}
I hereby declare...

\chapter{Abstract}
This dissertation...

\chapter{Acknowledgments}
I would like to thank...

\chapter{Notation}
\begin{tabular}{@{}cl@{}}
    \toprule
    Symbol & Description \\
    \midrule
    $P$ & Power (W) \\
    $\eta$ & Efficiency (\%) \\
    \bottomrule
\end{tabular}

\tableofcontents
\listoffigures
\listoftables

\mainmatter

\part{Theory}

\chapter{Fundamentals of Power Systems}
\section{Grid Topology}
\section{Power Flow Analysis}

\chapter{Renewable Energy Integration}
\section{Solar Photovoltaics}
\section{Wind Energy Conversion}

\part{Applications}

\chapter{Case Study: Island Microgrid}
\section{System Description}
\section{Simulation Results}

\chapter{Case Study: Urban Distribution Network}

\part{Synthesis}

\chapter{General Discussion}
\chapter{Conclusions and Future Work}

\appendix
\chapter{Mathematical Derivations}
\chapter{Data Tables}

\printbibliography

\end{document}
```

**Dissertation commands:**

| Command | Default | Description |
|---|---|---|
| `\dissertationdegree{text}` | `Doctoral Dissertation` | Degree title |
| `\dissertationdepartment{text}` | `Department` | Department name |
| `\dissertationinstitution{text}` | `University` | University name |
| `\firstsupervisor{text}` | `Supervisor Name` | Primary supervisor |
| `\secondsupervisor{text}` | `Co-Supervisor Name` | Secondary supervisor |
| `\dissertationcommittee{text}` | `Committee Member A, ...` | Committee members |
| `\submissiondate{text}` | `\today` | Submission date |
| `\keywords{text}` | `n/a` | Keywords for the title page |

### 22.3 Front Matter Components

Both thesis and dissertation doctypes use `\frontmatter` / `\mainmatter` / `\backmatter` for document division:

**`\frontmatter`** (before `\mainmatter`):

- Page numbering: lowercase Roman (i, ii, iii...)
- Chapter numbering: unnumbered by default (use `\chapter*{}` or `\addchap{}`)
- Typical contents:
  - Title page (`\maketitle`)
  - Declaration of authorship
  - Abstract
  - Acknowledgments
  - Notation/symbol table
  - Table of contents, list of figures, list of tables

**`\mainmatter`** (after `\mainmatter`):

- Page numbering: Arabic (1, 2, 3...)
- Chapter numbering: sequential
- `\part` divisions for grouping chapters

**`\backmatter`** (after `\backmatter`):

- Bibliography (`\printbibliography`)
- Glossaries (`\printunsrtglossary`)
- Index (`\printunsrtindex`)
- Appendices should go before `\backmatter` (use `\appendix`)

### 22.4 Thesis TUHH

- Institution config: `institution=tuhh`, `titlestyle=TUHH`
- TUHH-specific branded title page, bilingual logos
- Best for: TUHH ITT theses
- Full walkthrough: colophon, task page, authorship declaration, abstract

### 22.5 Manual

- (See 21.5 -- same doctype, different context)

### 22.6 Dictionary

- Custom commands: `\dictionaryseries`, `\dictionarysubtitle`, `\dictionaryedition`, `\dictionarypublisher`, `\dictionaryisbn`, `\dictionarysubjects`, `\dictionarynote`
- Best for: lexicons, glossaries as standalone books

**Cross-refs:** Chapter 52 (title pages), Chapter 53 (institutions), Chapter 70 (bibliography)

---

## Chapter 23: Academic Documents

**Purpose:** Cover educational document types.

**Sections per doctype (5 doctypes):**

### 23.1 Homework

- Custom commands: `\hwtitle`, `\hwcourse`, `\hwauthor`, `\hwduedate`, `\hwinstructor`, `\hwnumber`, `\hwstudentname`, `\hwstudentid`, `\hwtotalpoints`
- Environments: `exercise`, `solution`
- `\showsolutions` / `\hidesolutions`
- Best for: problem sets, worksheets

### 23.2 Exam

- Custom commands: `\examtitle`, `\examcode`, `\examdate`, `\examduration`, `\totalmarks`, `\department`, `\examinstructions`
- Environments: `question`, `answer`
- Best for: midterm/final examinations

### 23.3 Lecture Notes

- Custom commands: `\lecturetitle`, `\lecturenumber`, `\coursename`, `\lecturedate`, `\lecturer`, `\semester`
- Environments: `theorem`, `lemma`, `corollary`, `definition`, `example`, `remark`, `proof`
- Wide left margin (3cm) for annotations
- Best for: course handouts, lecture material

### 23.4 Syllabus

- Custom commands: `\coursenumber`, `\coursetitle`, `\semester`, `\instructor`, `\instructoroffice`, `\instructoremail`, `\instructorhours`, `\meetingtime`, `\meetinglocation`, `\prerequisites`, `\coursewebsite`
- Environments: `objectives`, `gradingpolicy`
- `\gradingitem`, `\scheduleentry`
- Best for: course syllabi

### 23.5 Handout

- Custom commands: `\handouttitle`, `\handoutcourse`, `\handoutnumber`, `\handoutdate`, `\handoutauthor`
- `keyconceptbox` tcolorbox, `\keyconcept`, `\remember`
- Two-column mode
- Best for: class handouts, workshop materials

**Cross-refs:** Chapter 91 (boxes), Chapter 80 (code listings)

---

## Chapter 24: Business & Personal Documents

**Purpose:** Cover business and personal document types.

**Sections per doctype (5 doctypes):**

### 24.1 CV / Resume

- Custom commands: `\cvname`, `\cvtitle`, `\cvemail`, `\cvphone`, `\cvwebsite`, `\cvlinkedin`, `\cvsummary`, `\cvlocation`, `\cvlinks`, `\cvimage`, `\cvbulletspacing`
- Custom commands: `\cvexperience`, `\cveducation`, `\cvskill`, `\cvlanguages`
- Environment: `cventry`
- Also see: `cv-twopage` variant (scrbook-based two-page CV)
- Best for: academic and industry CVs

### 24.2 Cover Letter

- Custom commands: `\clrecipient`, `\clposition`, `\clcompany`, `\cldate`
- Best for: job applications

### 24.3 Invoice

- Custom commands: `\invnumber`, `\invdate`, `\invdue`, `\invfrom`, `\invto`, `\invfromaddr`, `\invtoaddr`, `\invcurrency`, `\invtaxrate`, `\invpaymentterms`, `\invnotes`
- `\invoiceitem{desc}{qty}{price}`
- Best for: freelance invoices, billing

### 24.4 Memo

- Custom commands: `\memoto`, `\memofrom`, `\memosubject`, `\memodate`, `\memocc`, `\memobcc`, `\memoref`
- Custom MEMORANDUM header
- Best for: internal communications

### 24.5 Recipe

- Custom commands: `\recipeprep`, `\recipecook`, `\recipeservings`, `\recipedifficulty`, `\recipecuisine`, `\recipecategory`, `\recipedifficulty`, `\recipecalories`
- `\recipeMeta`
- Environments: `ingredients`, `instructions`
- `\recipeNote`
- Best for: cookbooks, food blogs

**Cross-refs:** Chapter 50 (page layout), Chapter 62 (tables)

---

## Chapter 25: Visual Documents (Presentations & Posters)

**Purpose:** Cover visual/performance document types.

### 25.1 Presentation (Slides)

- Loads `omnilatex-presentation.sty`
- 16:10 aspect ratio (254mm x 190.5mm)
- Environments: `presentationframe`, `slideframe`
- Custom commands: `\presentationSection{title}`, `\slidetitle{}`, `\presentationcolumns`, `\presentationcolumn{width}`
- Block environments: `presentationblock`, `alertblock`, `exampleblock`, `noteblock`, `definitionblock`
- Features: progress bar, section dividers, navigation symbols, frame counter
- `\presentationnavsymbolson/off`, `\presentationprogresson/off`
- Best for: conference talks, lectures, project presentations

### 25.2 Poster

- A1 landscape (841mm x 594mm)
- `posterblock{title}`, `posterblocknotitle`
- `\posterwidth`
- Column breaks via `\columnbreak`
- Best for: academic conference posters
- Example: poster with TikZ accuracy chart + system architecture diagram

---

## Chapter 26: New Document Types (v3.1.0+)

### 26.1 Academic & Research

#### Lab Report (`doctype=lab-report`)
- Structured abstract (Objective, Methods, Results, Conclusion)
- Equipment tables, procedure steps
- Data analysis with pgfplots charts
- Error propagation calculations

#### Literature Review (`doctype=literature-review`)
- PRISMA-style methodology
- Thematic organization with comparison tables
- Synthesis matrix mapping papers to aspects
- Gap analysis tables

#### Thesis Proposal (`doctype=thesis-proposal`)
- Background, research questions, methodology
- Timeline (Gantt chart)
- Expected contributions

#### Annotated Bibliography (`doctype=annotated-bibliography`)
- Entries organized by theme
- Citation + annotation format

#### Proceedings (`doctype=proceedings`)
- Conference volume (scrbook base)
- Preface, table of contents, paper stubs

#### Preprint (`doctype=preprint`)
- arXiv-style formatting
- Abstract, sections, figures, bibliography

#### Working Paper (`doctype=working-paper`)
- Discussion paper format
- Policy implications section

### 26.2 Business & Professional

#### Business Letter (`doctype=business-letter`)
- Sender/recipient addresses
- Formal salutation/closing

#### Meeting Minutes (`doctype=meeting-minutes`)
- Attendees, agenda, decisions, action items

#### Quarterly Report (`doctype=quarterly-report`)
- Executive summary, KPI dashboard
- Financial charts (pgfplots)
- Department reviews

#### Strategic Plan (`doctype=strategic-plan`)
- Vision/mission, SWOT analysis
- Gantt roadmap, resource allocation

#### Product Spec (`doctype=product-spec`)
- Feature priority matrix
- Architecture diagrams (TikZ)
- API endpoints, testing strategy

### 26.3 Education

#### Course Material (`doctype=course-material`)
- Syllabus hybrid with schedule table
- Grading policy, learning outcomes

#### Course Notes (`doctype=course-notes`)
- Lecture notes with key concepts
- Examples, practice problems

#### Textbook (`doctype=textbook`)
- Learning objectives, exercises (3 difficulty levels)
- Theorem/definition environments
- Code listings

#### Quiz (`doctype=quiz`)
- Multiple choice, short answer, true/false
- Point values, time limits

#### Lesson Plan (`doctype=lesson-plan`)
- Objectives, materials, duration
- Warm-up, instruction, practice, assessment

### 26.4 Technical & Documentation

#### Software Documentation (`doctype=software-documentation`)
- Architecture diagrams (TikZ)
- API reference, CLI reference
- Code examples (Python, Rust, shell)

#### API Reference (`doctype=api-reference`)
- Authentication, rate limiting
- CRUD endpoints with examples
- Data models, webhooks, SDKs

#### Changelog (`doctype=changelog`)
- Version entries with categories
- Added, Changed, Deprecated, Removed, Fixed, Security

#### Technical Spec (`doctype=technical-spec`)
- Requirements table
- Architecture, interfaces, constraints

### 26.5 Creative & Lifestyle

#### Blog Post (`doctype=blog-post`)
- Title, date, author, tags
- Code blocks, conclusion

#### Newsletter (`doctype=newsletter`)
- Masthead, lead article, events

#### Brochure (`doctype=brochure`)
- Multi-column layout
- Features, testimonials, CTA

#### Invitation (`doctype=invitation`)
- Host/recipient, event details
- RSVP section

#### Program (`doctype=program`)
- Schedule table, speakers, sponsors

### 26.6 Government & Legal

#### Legislation (`doctype=legislation`)
- Preamble, sections, definitions
- Effective date, amendments

#### Regulation (`doctype=regulation`)
- Scope, requirements table
- Compliance matrix, enforcement

#### Annual Report (`doctype=annual-report`)
- Chair message, financial summary
- Achievements, governance

#### Case Study (`doctype=case-study`)
- Background, analysis, solution
- Results, lessons learned
