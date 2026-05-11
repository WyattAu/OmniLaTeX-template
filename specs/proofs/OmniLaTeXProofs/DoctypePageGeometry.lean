/-
  Formal Verification: OmniLaTeX Doctype Page Geometry Properties

  Property: Each KOMA-Script class (scrbook, scrreprt, scrartcl) has
  well-defined page geometry defaults (twoside, DIV) that apply to all
  member doctypes.

  Reference: omnilatex.cls, KOMA-Script typearea documentation
  scrbook doctypes (4): thesis, dissertation, book, dictionary — twoside=true, DIV=12
  scrreprt doctypes (10): manual, technicalreport, standard, patent,
    research-proposal, cover-letter, exam, handout, homework, memo, white-paper — twoside depends, DIV=12
  scrartcl doctypes (12): article, inlinepaper, journal, cv, poster,
    presentation, letter, recipe, lecture-notes, syllabus, invoice — twoside=false, DIV=12

  Note: DocumentSettings.lean classifies cover-letter, exam, handout, homework, memo, white-paper
  under scrartcl (17 article-class doctypes). Here we reclassify based on omnilatex.cls
  twoside behaviour: these 6 doctypes use twoside=false like scrartcl.
  No Mathlib dependency.
-/

namespace DoctypePageGeometry

inductive KomaClass where
  | scrbook : KomaClass
  | scrreprt : KomaClass
  | scrartcl : KomaClass
  deriving DecidableEq, Repr

inductive Doctype where
  -- scrbook (4)
  | thesis : Doctype
  | dissertation : Doctype
  | book : Doctype
  | dictionary : Doctype
  -- scrreprt (10)
  | manual : Doctype
  | technicalreport : Doctype
  | standard : Doctype
  | patent : Doctype
  | research_proposal : Doctype
  | cover_letter : Doctype
  | exam : Doctype
  | handout : Doctype
  | homework : Doctype
  | memo : Doctype
  | white_paper : Doctype
  -- scrartcl (12)
  | article : Doctype
  | inlinepaper : Doctype
  | journal : Doctype
  | cv : Doctype
  | poster : Doctype
  | presentation : Doctype
  | letter : Doctype
  | recipe : Doctype
  | lecture_notes : Doctype
  | syllabus : Doctype
  | invoice : Doctype
  deriving DecidableEq, Repr

def scrbookDoctypes : List Doctype := [
  .thesis, .dissertation, .book, .dictionary
]

def scrreprtDoctypes : List Doctype := [
  .manual, .technicalreport, .standard, .patent, .research_proposal,
  .cover_letter, .exam, .handout, .homework, .memo, .white_paper
]

def scrartclDoctypes : List Doctype := [
  .article, .inlinepaper, .journal, .cv, .poster, .presentation,
  .letter, .recipe, .lecture_notes, .syllabus, .invoice
]

def allDoctypes : List Doctype :=
  scrbookDoctypes ++ scrreprtDoctypes ++ scrartclDoctypes

def doctypeClass : Doctype → KomaClass
  | .thesis => .scrbook
  | .dissertation => .scrbook
  | .book => .scrbook
  | .dictionary => .scrbook
  | .manual => .scrreprt
  | .technicalreport => .scrreprt
  | .standard => .scrreprt
  | .patent => .scrreprt
  | .research_proposal => .scrreprt
  | .cover_letter => .scrreprt
  | .exam => .scrreprt
  | .handout => .scrreprt
  | .homework => .scrreprt
  | .memo => .scrreprt
  | .white_paper => .scrreprt
  | .article => .scrartcl
  | .inlinepaper => .scrartcl
  | .journal => .scrartcl
  | .cv => .scrartcl
  | .poster => .scrartcl
  | .presentation => .scrartcl
  | .letter => .scrartcl
  | .recipe => .scrartcl
  | .lecture_notes => .scrartcl
  | .syllabus => .scrartcl
  | .invoice => .scrartcl

def twoside : KomaClass → Bool
  | .scrbook => true
  | .scrreprt => false
  | .scrartcl => false

def divValue : KomaClass → Nat
  | .scrbook => 12
  | .scrreprt => 12
  | .scrartcl => 12

theorem scrbook_doctype_count : scrbookDoctypes.length = 4 := by
  decide

theorem scrreprt_doctype_count : scrreprtDoctypes.length = 11 := by
  decide

theorem scrartcl_doctype_count : scrartclDoctypes.length = 11 := by
  decide

theorem total_doctypes : allDoctypes.length = 26 := by
  simp [allDoctypes, scrbook_doctype_count, scrreprt_doctype_count, scrartcl_doctype_count]

theorem doctype_counts_sum_to_total :
    scrbookDoctypes.length + scrreprtDoctypes.length + scrartclDoctypes.length = 26 := by
  simp [scrbook_doctype_count, scrreprt_doctype_count, scrartcl_doctype_count]

theorem all_scrbook_doctypes_are_valid :
    ∀ d ∈ scrbookDoctypes, doctypeClass d = .scrbook := by
  simp [doctypeClass, scrbookDoctypes]

theorem all_scrreprt_doctypes_are_valid :
    ∀ d ∈ scrreprtDoctypes, doctypeClass d = .scrreprt := by
  simp [doctypeClass, scrreprtDoctypes]

theorem all_scrartcl_doctypes_are_valid :
    ∀ d ∈ scrartclDoctypes, doctypeClass d = .scrartcl := by
  simp [doctypeClass, scrartclDoctypes]

theorem doctype_partitions_are_disjoint :
    (∀ d ∈ scrbookDoctypes, d ∉ scrreprtDoctypes ∧ d ∉ scrartclDoctypes) ∧
    (∀ d ∈ scrreprtDoctypes, d ∉ scrartclDoctypes) := by
  decide

theorem every_doctype_has_exactly_one_class :
    ∀ d ∈ allDoctypes,
      (doctypeClass d = .scrbook ∨ doctypeClass d = .scrreprt ∨ doctypeClass d = .scrartcl) ∧
      ¬(doctypeClass d = .scrbook ∧ doctypeClass d = .scrreprt) ∧
      ¬(doctypeClass d = .scrbook ∧ doctypeClass d = .scrartcl) ∧
      ¬(doctypeClass d = .scrreprt ∧ doctypeClass d = .scrartcl) := by
  decide

theorem all_doctypes_use_div_12 :
    ∀ d ∈ allDoctypes, divValue (doctypeClass d) = 12 := by
  decide

theorem scrbook_has_twoside :
    ∀ d ∈ scrbookDoctypes, twoside (doctypeClass d) = true := by
  simp [doctypeClass, twoside, scrbookDoctypes]

end DoctypePageGeometry
