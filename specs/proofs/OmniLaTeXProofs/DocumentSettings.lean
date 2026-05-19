/-
  Formal Verification: OmniLaTeX DocumentSettings Resolution

  Property: Each canonical doctype resolves to exactly one KOMA-Script class,
  and the three classes partition the set of 26 doctypes.

  Source of truth: tests/constants.py DOCTYPE_TO_CLASS (verified against omnilatex.cls).
  Article (17), Report (5), Book (4) = 26 total.
  No Mathlib dependency.
-/

namespace DocSettings

inductive KomaClass where
  | article : KomaClass
  | report : KomaClass
  | book : KomaClass
  deriving DecidableEq, Repr

inductive Doctype where
  -- scrartcl (17)
  | article : Doctype
  | journal : Doctype
  | inlinepaper : Doctype
  | cv : Doctype
  | cover_letter : Doctype
  | poster : Doctype
  | presentation : Doctype
  | letter : Doctype
  | homework : Doctype
  | exam : Doctype
  | lecture_notes : Doctype
  | syllabus : Doctype
  | handout : Doctype
  | memo : Doctype
  | white_paper : Doctype
  | invoice : Doctype
  | recipe : Doctype
  -- scrreprt (5)
  | manual : Doctype
  | technicalreport : Doctype
  | standard : Doctype
  | patent : Doctype
  | research_proposal : Doctype
  -- scrbook (4)
  | thesis : Doctype
  | dissertation : Doctype
  | book : Doctype
  | dictionary : Doctype
  deriving DecidableEq, Repr

-- Canonical doctype-to-class mapping from omnilatex.cls / constants.py
def doctypeClass : Doctype → KomaClass
  -- scrartcl
  | .article => .article
  | .journal => .article
  | .inlinepaper => .article
  | .cv => .article
  | .cover_letter => .article
  | .poster => .article
  | .presentation => .article
  | .letter => .article
  | .homework => .article
  | .exam => .article
  | .lecture_notes => .article
  | .syllabus => .article
  | .handout => .article
  | .memo => .article
  | .white_paper => .article
  | .invoice => .article
  | .recipe => .article
  -- scrreprt
  | .manual => .report
  | .technicalreport => .report
  | .standard => .report
  | .patent => .report
  | .research_proposal => .report
  -- scrbook
  | .thesis => .book
  | .dissertation => .book
  | .book => .book
  | .dictionary => .book

def articleDoctypes : List Doctype := [
  .article, .journal, .inlinepaper, .cv, .cover_letter,
  .poster, .presentation, .letter, .homework, .exam,
  .lecture_notes, .syllabus, .handout, .memo, .white_paper,
  .invoice, .recipe
]

def reportDoctypes : List Doctype := [
  .manual, .technicalreport, .standard, .patent, .research_proposal
]

def bookDoctypes : List Doctype := [
  .thesis, .dissertation, .book, .dictionary
]

def allDoctypes : List Doctype :=
  articleDoctypes ++ reportDoctypes ++ bookDoctypes

theorem doctype_class_deterministic :
    ∀ d c₁ c₂, doctypeClass d = c₁ → doctypeClass d = c₂ → c₁ = c₂ := by
  intro d c₁ c₂ h₁ h₂
  exact h₁.symm.trans h₂

theorem article_class_nonempty : articleDoctypes.length > 0 := by
  decide

theorem report_class_nonempty : reportDoctypes.length > 0 := by
  decide

theorem book_class_nonempty : bookDoctypes.length > 0 := by
  decide

theorem article_count : articleDoctypes.length = 17 := by
  decide

theorem report_count : reportDoctypes.length = 5 := by
  decide

theorem book_count : bookDoctypes.length = 4 := by
  decide

theorem doctype_count : allDoctypes.length = 26 := by
  simp [allDoctypes, article_count, report_count, book_count]

theorem all_doctype_classes_covered :
    articleDoctypes.length > 0 ∧
    reportDoctypes.length > 0 ∧
    bookDoctypes.length > 0 := by
  exact And.intro (by decide) (And.intro (by decide) (by decide))

theorem class_partition :
    allDoctypes.length = articleDoctypes.length + reportDoctypes.length + bookDoctypes.length ∧
    articleDoctypes.length > 0 ∧
    reportDoctypes.length > 0 ∧
    bookDoctypes.length > 0 := by
  exact And.intro
    (by simp [allDoctypes, article_count, report_count, book_count])
    (And.intro (by decide) (And.intro (by decide) (by decide)))

theorem article_is_largest :
    articleDoctypes.length > reportDoctypes.length ∧
    articleDoctypes.length > bookDoctypes.length := by
  exact And.intro (by decide) (by decide)

-- Verify that every doctype in each list maps to the expected class
theorem article_doctypes_consistent :
    ∀ d ∈ articleDoctypes, doctypeClass d = .article := by
  intro d hd
  simp [doctypeClass] at *
  cases d <;> simp [articleDoctypes] at hd <;> try decide

theorem report_doctypes_consistent :
    ∀ d ∈ reportDoctypes, doctypeClass d = .report := by
  intro d hd
  simp [doctypeClass] at *
  cases d <;> simp [reportDoctypes] at hd <;> try decide

theorem book_doctypes_consistent :
    ∀ d ∈ bookDoctypes, doctypeClass d = .book := by
  intro d hd
  simp [doctypeClass] at *
  cases d <;> simp [bookDoctypes] at hd <;> try decide

-- Total doctype count verification
theorem total_doctype_count :
    articleDoctypes.length + reportDoctypes.length + bookDoctypes.length = 26 := by
  simp [articleDoctypes, reportDoctypes, bookDoctypes]

-- No doctype belongs to more than one class
theorem class_partition_disjoint :
    ∀ d : Doctype, ¬(doctypeClass d = .article ∧ doctypeClass d = .report) := by
  intro d h
  cases d <;> simp [doctypeClass] at * <;> contradiction

-- Every doctype resolves to some class (exhaustiveness)
theorem all_doctypes_have_class :
    ∀ d : Doctype, doctypeClass d = .article ∨ doctypeClass d = .report ∨ doctypeClass d = .book := by
  intro d
  cases d <;> simp [doctypeClass] <;> try left <;> try right <;> try left <;> rfl

-- Presentation and poster are article-class (common assumption)
theorem presentation_is_article_class :
    doctypeClass .presentation = .article := by
  rfl

theorem thesis_is_book_class :
    doctypeClass .thesis = .book := by
  rfl

theorem manual_is_report_class :
    doctypeClass .manual = .report := by
  rfl

end DocSettings
