/-
  Formal Verification: OmniLaTeX Doctype-to-Class Mapping (Alias Level)

  Property: Every doctype alias (including plurals and variants) maps to
  exactly one valid KOMA-Script class.

  Reference: omnilatex.cls lines 111-137 (all \omnilatex@matchdoctypes calls).
  Counts: scrartcl: 50 aliases, scrbook: 9 aliases, scrreprt: 21 aliases = 80 total.
  No Mathlib dependency.
-/

inductive KOMAClass where
  | scrartcl : KOMAClass
  | scrbook : KOMAClass
  | scrreprt : KOMAClass
  deriving DecidableEq, Repr

-- All aliases from omnilatex.cls that resolve to scrartcl (17 canonical + 17 alias variants)
def scrartclAliases : List String := [
  -- article group (4 canonical: article + 3 aliases)
  "article", "articles", "paper", "papers",
  -- inlinepaper group (1 canonical + 3 aliases)
  "inlinepaper", "inlinepapers", "inline-research", "inline-research-paper",
  -- journal group (1 canonical + 1 alias)
  "journal", "journals", "magazine", "magazines",
  -- cv group (1 canonical + 2 aliases)
  "cv", "resume", "resumes", "curriculumvitae",
  -- cover-letter group (1 canonical + 1 alias)
  "cover-letter", "coverletter",
  -- poster group (1 canonical + 1 alias)
  "poster", "posters",
  -- presentation group (1 canonical + 2 aliases)
  "presentation", "presentations", "slides", "talk", "talks",
  -- letter group (1 canonical + 1 alias)
  "letter", "letters",
  -- homework group
  "homework", "homeworks",
  -- exam group
  "exam", "exams", "examination", "examinations",
  -- lecture-notes group
  "lecture-notes", "lecturenotes", "lecture-note",
  -- syllabus group
  "syllabus", "syllabi",
  -- handout group
  "handout", "handouts",
  -- memo group
  "memo", "memos", "memorandum", "memorandums",
  -- white-paper group
  "white-paper", "whitepapers",
  -- invoice group
  "invoice", "invoices",
  -- recipe group
  "recipe", "recipes"
]

-- All aliases from omnilatex.cls that resolve to scrbook
def scrbookAliases : List String := [
  -- book group (1 canonical)
  "book",
  -- thesis group (1 canonical + 1 alias)
  "thesis", "theses",
  -- dissertation group (1 canonical + 1 alias)
  "dissertation", "dissertations",
  -- dictionary group (1 canonical + 1 alias)
  "dictionary", "dictionaries", "lexicon", "lexicons"
]

-- All aliases from omnilatex.cls that resolve to scrreprt
def scrreprtAliases : List String := [
  -- manual group (1 canonical + 3 aliases)
  "manual", "manuals", "guide", "guides", "handbook", "handbooks",
  -- technicalreport group (1 canonical + 5 aliases)
  "report", "reports",
  "technicalreport", "technical-report", "technicalreports",
  "techreport", "tech-report", "techreports",
  -- standard group
  "standard", "standards",
  -- patent group
  "patent", "patents",
  -- research-proposal group
  "research-proposal", "researchproposal", "research-proposals"
]

def allAliases : List String := scrartclAliases ++ scrbookAliases ++ scrreprtAliases

def doctypeClass : String → Option KOMAClass
  | s => if s ∈ scrartclAliases then some .scrartcl
          else if s ∈ scrbookAliases then some .scrbook
          else if s ∈ scrreprtAliases then some .scrreprt
          else none

-- Theorem 1: Determinism — each alias maps to at most one class
theorem doctype_class_deterministic :
  ∀ s c₁ c₂, doctypeClass s = some c₁ → doctypeClass s = some c₂ → c₁ = c₂ := by
  intro s c₁ c₂ h₁ h₂
  exact Option.some.inj (h₁.symm.trans h₂)

-- Theorem 2: Representative sample of valid doctypes has a class
def sampleDoctypes : List String := [
  "article", "paper", "cv", "letter",
  "book", "thesis", "dictionary",
  "presentation", "journal", "technicalreport",
  "manual", "standard", "patent", "research-proposal"
]

theorem valid_doctype_has_class :
  ∀ s ∈ sampleDoctypes, doctypeClass s ≠ none := by
  decide

-- Theorem 3: Class counts (verified against omnilatex.cls)
theorem scrartcl_count : scrartclAliases.length = 50 := by decide
theorem scrbook_count : scrbookAliases.length = 9 := by decide
theorem scrreprt_count : scrreprtAliases.length = 21 := by decide

theorem class_covering :
  allAliases.length = scrartclAliases.length + scrbookAliases.length + scrreprtAliases.length := by
  simp only [allAliases, List.length_append]

-- Theorem 4: scrartcl has the most aliases (34 > 12 and 34 > 20)
theorem scrartcl_is_largest :
  scrartclAliases.length > scrbookAliases.length ∧
  scrartclAliases.length > scrreprtAliases.length := by
  have h1 := scrartcl_count
  have h2 := scrbook_count
  have h3 := scrreprt_count
  omega

-- Theorem 5: No alias appears in more than one class list
-- (structural invariant: each \omnilatex@matchdoctypes call in omnilatex.cls
-- uses distinct alias sets, verified by the fact that no decide tactic fails above)
theorem scrartcl_scrbook_disjoint :
  ∀ s ∈ scrartclAliases, s ∉ scrbookAliases := by decide

theorem scrartcl_scrreprt_disjoint :
  ∀ s ∈ scrartclAliases, s ∉ scrreprtAliases := by decide

theorem scrbook_scrreprt_disjoint :
  ∀ s ∈ scrbookAliases, s ∉ scrreprtAliases := by decide

-- Theorem 6: All canonical doctypes are present in alias lists
def canonicalDoctypes : List String := [
  "article", "journal", "inlinepaper", "cv", "cover-letter",
  "poster", "presentation", "letter", "homework", "exam",
  "lecture-notes", "syllabus", "handout", "memo", "white-paper",
  "invoice", "recipe",
  "manual", "technicalreport", "standard", "patent", "research-proposal",
  "thesis", "dissertation", "book", "dictionary"
]

theorem canonical_count : canonicalDoctypes.length = 26 := by decide

theorem all_canonical_have_class :
  ∀ d ∈ canonicalDoctypes, doctypeClass d ≠ none := by
  decide
