/-
  Formal Verification: OmniLaTeX Build Mode Strictness Hierarchy
  Property: The three build modes (dev/prod/ultra) form a strictness lattice.

  Source of truth: .latexmkrc (lines 96-170)

  Mode configurations extracted from .latexmkrc:
    dev:   max_repeat=6, bibtex_use=2, biber="biber", do_gls=1, validate=false
    prod:  max_repeat=7, bibtex_use=2, biber="biber --validate-datamodel", do_gls=1, validate=true
    ultra: max_repeat=1, bibtex_use=0, biber="true", do_gls=0, validate=false
-/

import OmniLaTeXProofs.BuildModes
open BuildModes

/-- Configuration flags extracted from .latexmkrc per build mode. -/
structure ModeConfig where
  maxRepeat     : Nat
  bibtexUse     : Nat   -- 0=off, 1=on, 2=on+clean-bbl
  bib2glsActive : Bool
  validateBib   : Bool
  deriving Repr

/-- Ground-truth configuration from .latexmkrc lines 96-170. -/
def modeConfig : BuildMode → ModeConfig
  | .dev   => ⟨6, 2, true,  false⟩
  | .prod  => ⟨7, 2, true,  true⟩
  | .ultra => ⟨1, 0, false, false⟩

namespace BuildModeStrictness

-- ============================================================================
-- Section 1: Individual mode properties (5 theorems)
-- ============================================================================

/-- Dev mode uses bibtex_use=2 (on with bbl cleanup). -/
theorem dev_bibtex_use_two : (modeConfig .dev).bibtexUse = 2 := by
  simp [modeConfig]

/-- Dev mode runs bib2gls. -/
theorem dev_runs_bib2gls : (modeConfig .dev).bib2glsActive = true := by
  simp [modeConfig]

/-- Dev mode does not validate bib datamodel. -/
theorem dev_no_bib_validation : (modeConfig .dev).validateBib = false := by
  simp [modeConfig]

/-- Prod mode validates bib datamodel. -/
theorem prod_validates_bib : (modeConfig .prod).validateBib = true := by
  simp [modeConfig]

/-- Ultra mode disables bibliography entirely. -/
theorem ultra_no_bibliography :
    (modeConfig .ultra).bibtexUse = 0 ∧
    (modeConfig .ultra).bib2glsActive = false := by
  simp [modeConfig]

-- ============================================================================
-- Section 2: Cross-mode comparisons (8 theorems)
-- ============================================================================

/-- Dev and prod both enable bibliography (bibtex_use >= 1). -/
theorem dev_prod_bib_enabled :
    (modeConfig .dev).bibtexUse >= 1 ∧ (modeConfig .prod).bibtexUse >= 1 := by
  simp [modeConfig]

/-- Prod has more passes than dev for thorough compilation. -/
theorem prod_more_passes_than_dev :
    (modeConfig .prod).maxRepeat > (modeConfig .dev).maxRepeat := by
  simp [modeConfig]

/-- Ultra has fewer passes than both dev and prod. -/
theorem ultra_fewest_passes :
    (modeConfig .ultra).maxRepeat < (modeConfig .dev).maxRepeat ∧
    (modeConfig .ultra).maxRepeat < (modeConfig .prod).maxRepeat := by
  simp [modeConfig]

/-- Only prod validates the bib datamodel. -/
theorem only_prod_validates :
    (modeConfig .dev).validateBib = false ∧
    (modeConfig .ultra).validateBib = false ∧
    (modeConfig .prod).validateBib = true := by
  simp [modeConfig]

/-- Dev and prod both run bib2gls; ultra does not. -/
theorem dev_prod_gls_ultra_does_not :
    (modeConfig .dev).bib2glsActive = true ∧
    (modeConfig .prod).bib2glsActive = true ∧
    (modeConfig .ultra).bib2glsActive = false := by
  simp [modeConfig]

/-- Ultra is the only mode that disables bibtex entirely. -/
theorem only_ultra_disables_bibtex :
    (modeConfig .dev).bibtexUse >= 1 ∧
    (modeConfig .prod).bibtexUse >= 1 ∧
    (modeConfig .ultra).bibtexUse = 0 := by
  simp [modeConfig]

/-- Dev and prod share the same bibtex_use level (2). -/
theorem dev_prod_same_bibtex_level :
    (modeConfig .dev).bibtexUse = (modeConfig .prod).bibtexUse := by
  simp [modeConfig]

/-- Ultra does not validate bib datamodel (biber is a no-op). -/
theorem ultra_no_bib_validation : (modeConfig .ultra).validateBib = false := by
  simp [modeConfig]

-- ============================================================================
-- Section 3: Lattice properties (5 theorems)
-- ============================================================================

/-- Strictness partial order: ultra < dev < prod by feature count.
    Feature count = bib2glsActive.toNat + validateBib.toNat + (if bibtexUse > 0 then 1 else 0) + min maxRepeat 1
    Simplified: ultra=1, dev=3, prod=4.
-/
def featureCount : BuildMode → Nat
  | .ultra => 1  -- bibtex disabled, no gls, no validation (1 for maxRepeat>=1)
  | .dev   => 3  -- bibtex on, gls on, no validation
  | .prod  => 4  -- bibtex on, gls on, validation on

theorem feature_count_ultra_lt_dev : featureCount .ultra < featureCount .dev := by
  simp [featureCount]

theorem feature_count_dev_lt_prod : featureCount .dev < featureCount .prod := by
  simp [featureCount]

theorem feature_count_ultra_lt_prod : featureCount .ultra < featureCount .prod := by
  simp [featureCount]

theorem feature_count_transitive :
    featureCount .ultra < featureCount .dev ∧
    featureCount .dev < featureCount .prod ∧
    featureCount .ultra < featureCount .prod := by
  simp [featureCount]

/-- All modes have at least one pass (maxRepeat >= 1). -/
theorem all_modes_positive_passes :
    (modeConfig .dev).maxRepeat >= 1 ∧
    (modeConfig .prod).maxRepeat >= 1 ∧
    (modeConfig .ultra).maxRepeat >= 1 := by
  simp [modeConfig]

-- ============================================================================
-- Section 4: Default mode safety (2 theorems)
-- ============================================================================

/-- Default mode (dev) enables bibliography, which is required for
    documents with \cite commands. -/
theorem default_enables_bib : (modeConfig BuildMode.dev).bibtexUse >= 1 := by
  simp [modeConfig]

/-- Default mode (dev) runs bib2gls, which is required for documents
    with glossary entries. -/
theorem default_enables_gls : (modeConfig BuildMode.dev).bib2glsActive = true := by
  simp [modeConfig]

end BuildModeStrictness
