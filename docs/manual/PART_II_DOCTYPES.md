# Part II: Document Types — Detailed Chapter Plans

---

## Chapter 20: Articles & Short Documents

**Purpose:** Cover all scrartcl-based short document types.

**Sections per doctype (6 doctypes):**

### 20.1 Article
- `\documentclass[doctype=article]{omnilatex}`
- Standard KOMA scrartcl, `11pt`, `a4paper`
- Best for: journal submissions, short reports, blog posts
- Example: complete article with TikZ figure (loss curves)

### 20.2 Journal
- Custom commands: `\journalname`, `\journalvolume`, `\journalissue`, `\journalpages`, `\doi`, `\articletype`, `\highlights`, `\receiveddate`, `\accepteddate`, `\publisheddate`
- Best for: academic journal submissions
- Example: journal article with wave function plots

### 20.3 Inline Paper
- Custom commands: `\affiliation`, `\contact`, `\supplementary`, `\keywords`
- Two-column layout (arXiv-style)
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

**Sections per doctype (5 doctypes):**

### 21.1 Report / Technical Report
- Custom commands: `\reportnumber`, `\revision`, `\preparedby`, `\client`, `\projectname`, `\confidentiality`, `\sponsor`, `\leadengineer`, `\doccontrol`, `\distribution`
- Best for: engineering reports, project documentation
- Example: technical report with IOPS demand chart

### 21.2 Research Proposal
- Custom commands: `\propabstract`, `\propprogram`, `\propcall`, `\propduration`, `\propbudget`, `\propstartdate`, `\propenddate`, `\propinvestigator`, `\propcoinvestigators`, `\proporganization`
- Best for: grant applications, funding proposals
- Example: research proposal with CNN architecture diagram

### 21.3 Standard
- Custom commands: `\standardseries`, `\standarddesignation`, `\standardstatus`, `\standardscope`, `\standardcommittee`, `\standardsupersedes`, `\standardics`, `\standardkeywords`, `\standarddisclaimer`
- Custom section numbering
- Best for: ISO/IEC standards documents

### 21.4 Patent
- KOMA scrreprt base
- Best for: patent specifications, IP documentation

### 21.5 Manual
- Custom commands: `\manualbrand`, `\manualversion`, `\manualreleasedate`, `\manualsupport`, `\manualsummary`
- Sans font mode
- Best for: software documentation, user guides
- Example: this very manual uses doctype=manual

**Cross-refs:** Chapter 14, Chapter 50 (page layout), Chapter 62 (tables)

---

## Chapter 22: Theses & Dissertations

**Purpose:** Cover all scrbook-based long document types.

**Sections per doctype (5 doctypes):**

### 22.1 Thesis
- Custom commands: `\thesisinstitution`, `\thesisdepartment`, `\thesisdegree`, `\thesisadvisor`, `\thesiscommittee`, `\defensedate`, `\thesislocation`
- Custom `\maketitle` with examiners table
- Best for: BSc/MSc theses

### 22.2 Dissertation
- Custom commands: `\dissertationdegree`, `\dissertationdepartment`, `\dissertationinstitution`, `\firstsupervisor`, `\secondsupervisor`, `\dissertationcommittee`, `\submissiondate`, `\keywords`
- Best for: PhD dissertations

### 22.3 Thesis TUHH
- Institution config: `institution=tuhh`, `titlestyle=TUHH`
- TUHH-specific branded title page, bilingual logos
- Best for: TUHH ITT theses
- Full walkthrough: colophon, task page, authorship declaration, abstract

### 22.4 Manual
- (See 21.5 — same doctype, different context)

### 22.5 Dictionary
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
- Custom commands: `\recipeprep`, `\recipecook`, `\recipeservings`, `\recipedifficulty`, `\recipecuisine`, `\recipecategory`, `\recipecalories`
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
- 16:10 aspect ratio (254mm × 190.5mm)
- Environments: `presentationframe`, `slideframe`
- Custom commands: `\presentationSection{title}`, `\slidetitle{}`, `\presentationcolumns`, `\presentationcolumn{width}`
- Block environments: `presentationblock`, `alertblock`, `exampleblock`, `noteblock`, `definitionblock`
- Features: progress bar, section dividers, navigation symbols, frame counter
- `\presentationnavsymbolson/off`, `\presentationprogresson/off`
- Best for: conference talks, lectures, project presentations

### 25.2 Poster
- A1 landscape (841mm × 594mm)
- `posterblock{title}`, `posterblocknotitle`
- `\posterwidth`
- Column breaks via `\columnbreak`
- Best for: academic conference posters
- Example: poster with TikZ accuracy chart + system architecture diagram
