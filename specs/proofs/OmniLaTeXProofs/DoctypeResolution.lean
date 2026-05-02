/-
  Formal Verification: OmniLaTeX Doctype Resolution
  Property: The doctype resolution function is deterministic and total over the specified alias set.

  Reference: omnilatex.cls v1.3.0-dev, lines 111-127
  State Machine: specs/document_model_state_machine.md
-/

-- Define the three KOMA-Script base classes
inductive BaseClass where
  | scrbook : BaseClass
  | scrreprt : BaseClass
  | scrartcl : BaseClass
  deriving DecidableEq, Repr

-- Define the 16 document type profiles
inductive DocProfile where
  | book : DocProfile
  | thesis : DocProfile
  | dissertation : DocProfile
  | manual : DocProfile
  | technicalreport : DocProfile
  | standard : DocProfile
  | patent : DocProfile
  | article : DocProfile
  | inlinepaper : DocProfile
  | journal : DocProfile
  | dictionary : DocProfile
  | cv : DocProfile
  | cover_letter : DocProfile
  | poster : DocProfile
  | presentation : DocProfile
  | letter : DocProfile
  deriving DecidableEq, Repr

-- Profile to base class mapping
def profileToClass : DocProfile → BaseClass
  | .book => .scrbook
  | .thesis => .scrbook
  | .dissertation => .scrbook
  | .dictionary => .scrbook
  | .manual => .scrreprt
  | .technicalreport => .scrreprt
  | .standard => .scrreprt
  | .patent => .scrreprt
  | .article => .scrartcl
  | .inlinepaper => .scrartcl
  | .journal => .scrartcl
  | .cv => .scrartcl
  | .cover_letter => .scrartcl
  | .poster => .scrartcl
  | .presentation => .scrartcl
  | .letter => .scrartcl

-- Doctype alias to profile resolution (partial function)
def doctypeResolve : String → Option DocProfile
  | "book" => .some .book
  | "thesis" | "theses" => .some .thesis
  | "dissertation" | "dissertations" => .some .dissertation
  | "manual" | "manuals" | "guide" | "guides" | "handbook" | "handbooks" => .some .manual
  | "report" | "reports" | "technicalreport" | "technical-report"
  | "technicalreports" | "technical-reports" | "techreport" | "tech-report"
  | "techreports" => .some .technicalreport
  | "standard" | "standards" => .some .standard
  | "patent" | "patents" => .some .patent
  | "article" | "articles" | "paper" | "papers" => .some .article
  | "inlinepaper" | "inlinepapers" | "inline-research" | "inline-research-paper" => .some .inlinepaper
  | "journal" | "journals" | "magazine" | "magazines" => .some .journal
  | "dictionary" | "dictionaries" | "lexicon" | "lexicons" => .some .dictionary
  | "cv" | "resume" | "resumes" | "curriculumvitae" => .some .cv
  | "cover-letter" | "coverletter" => .some .cover_letter
  | "poster" | "posters" => .some .poster
  | "presentation" | "presentations" | "slides" | "talk" | "talks" => .some .presentation
  | "letter" | "letters" => .some .letter
  | _ => .none

-- The set of all known aliases
def knownAliases : List String := [
  "book",
  "thesis", "theses",
  "dissertation", "dissertations",
  "manual", "manuals", "guide", "guides", "handbook", "handbooks",
  "report", "reports", "technicalreport", "technical-report",
  "technicalreports", "technical-reports", "techreport", "tech-report", "techreports",
  "standard", "standards",
  "patent", "patents",
  "article", "articles", "paper", "papers",
  "inlinepaper", "inlinepapers", "inline-research", "inline-research-paper",
  "journal", "journals", "magazine", "magazines",
  "dictionary", "dictionaries", "lexicon", "lexicons",
  "cv", "resume", "resumes", "curriculumvitae",
  "cover-letter", "coverletter",
  "poster", "posters",
  "presentation", "presentations", "slides", "talk", "talks",
  "letter", "letters"
]

-- Theorem 1: Determinism — each input maps to at most one output
theorem doctypeResolve_deterministic :
  ∀ s bc₁ bc₂, doctypeResolve s = some bc₁ → doctypeResolve s = some bc₂ → bc₁ = bc₂ := by
  intro s bc₁ bc₂ h₁ h₂
  exact Option.some.inj (h₁.symm.trans h₂)

-- Theorem 2: Totality — every known alias resolves successfully
theorem doctypeResolve_total_on_aliases :
  ∀ s, s ∈ knownAliases → doctypeResolve s ≠ none := by
  decide

-- Theorem 3: Profile-to-class consistency — no profile maps to the wrong class
theorem profile_class_consistency :
  ∀ p, profileToClass p = .scrbook ↔
    (p = .book ∨ p = .thesis ∨ p = .dissertation ∨ p = .dictionary) := by
  intro p
  cases p <;> simp [profileToClass] <;> try simp

-- Theorem 4: Known alias count
-- Count: 1 + 2 + 2 + 6 + 9 + 2 + 2 + 4 + 4 + 4 + 4 + 4 + 2 + 2 + 5 + 2 = 55
theorem known_alias_count : knownAliases.length = 55 := by
  simp [knownAliases]
