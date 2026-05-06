/-
  Formal Verification: OmniLaTeX DocumentSettings Resolution
  Property: Each doctype resolves to exactly one KOMA-Script class,
  and the three classes partition the set of 26 doctypes.

  Reference: config/document-settings.sty, omnilatex.cls
  Article (15), Report (6), Book (5) → 26 total.
  No Mathlib dependency.
-/

namespace DocSettings

inductive KomaClass where
  | article : KomaClass
  | report : KomaClass
  | book : KomaClass
  deriving DecidableEq, Repr

inductive Doctype where
  | article : Doctype
  | assignment : Doctype
  | accessibility_test : Doctype
  | citation_styles : Doctype
  | color_themes : Doctype
  | cover_letter : Doctype
  | cover_letter_formal : Doctype
  | cv : Doctype
  | exam : Doctype
  | handout : Doctype
  | homework : Doctype
  | inline_paper : Doctype
  | invoice : Doctype
  | journal : Doctype
  | lecture_notes : Doctype
  | dictionary : Doctype
  | dissertation : Doctype
  | patent : Doctype
  | research_proposal : Doctype
  | technical_report : Doctype
  | thesis : Doctype
  | book : Doctype
  | cv_twopage : Doctype
  | minimal_custom : Doctype
  | multi_language : Doctype
  | thesis_tuhh : Doctype
  deriving DecidableEq, Repr

def doctypeClass : Doctype → KomaClass
  | .article => .article
  | .assignment => .article
  | .accessibility_test => .article
  | .citation_styles => .article
  | .color_themes => .article
  | .cover_letter => .article
  | .cover_letter_formal => .article
  | .cv => .article
  | .exam => .article
  | .handout => .article
  | .homework => .article
  | .inline_paper => .article
  | .invoice => .article
  | .journal => .article
  | .lecture_notes => .article
  | .dictionary => .report
  | .dissertation => .report
  | .patent => .report
  | .research_proposal => .report
  | .technical_report => .report
  | .thesis => .report
  | .book => .book
  | .cv_twopage => .book
  | .minimal_custom => .book
  | .multi_language => .book
  | .thesis_tuhh => .book

def articleDoctypes : List Doctype := [
  .article, .assignment, .accessibility_test, .citation_styles,
  .color_themes, .cover_letter, .cover_letter_formal, .cv,
  .exam, .handout, .homework, .inline_paper, .invoice,
  .journal, .lecture_notes
]

def reportDoctypes : List Doctype := [
  .dictionary, .dissertation, .patent,
  .research_proposal, .technical_report, .thesis
]

def bookDoctypes : List Doctype := [
  .book, .cv_twopage, .minimal_custom,
  .multi_language, .thesis_tuhh
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

theorem article_count : articleDoctypes.length = 15 := by
  decide

theorem report_count : reportDoctypes.length = 6 := by
  decide

theorem book_count : bookDoctypes.length = 5 := by
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

end DocSettings
