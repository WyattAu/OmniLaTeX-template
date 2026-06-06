/-
  Formal Verification: OmniLaTeX Build Mode Configuration
  Property: Build mode system (dev/prod/ultra) produces consistent configurations.

  Reference: .latexmkrc, lib/core/omnilatex-base.sty
-/

namespace BuildModes

inductive BuildMode where
  | dev : BuildMode
  | prod : BuildMode
  | ultra : BuildMode
  deriving DecidableEq, Repr

structure BuildConfig where
  mode : BuildMode
  maxPasses : Nat
  runBiber : Bool
  runBib2gls : Bool
  validateDatamodel : Bool
  shellEscape : Bool
  strictWarnings : Bool
  deriving Repr

def buildConfigFor : BuildMode → BuildConfig
  | .dev => ⟨.dev, 10, true, true, false, true, false⟩
  | .prod => ⟨.prod, 5, true, true, true, true, true⟩
  | .ultra => ⟨.ultra, 1, false, false, false, true, false⟩


-- Theorem 1: Ultra mode never runs bibliography tools
theorem ultra_no_bib :
  (buildConfigFor .ultra).runBiber = false ∧
  (buildConfigFor .ultra).runBib2gls = false := by
  simp [buildConfigFor]

-- Theorem 2: Prod mode always validates datamodel
theorem prod_validates :
  (buildConfigFor .prod).validateDatamodel = true ∧
  (buildConfigFor .prod).runBiber = true := by
  simp [buildConfigFor]

-- Theorem 3: Dev mode has enough passes for reference resolution
theorem dev_enough_passes :
  (buildConfigFor .dev).maxPasses ≥ 3 := by
  simp [buildConfigFor]

-- Theorem 4: All modes enable shell-escape (for minted/Inkscape)
theorem all_modes_shell_escape :
  ∀ m, (buildConfigFor m).shellEscape = true := by
  intro m
  cases m <;> simp [buildConfigFor]

-- Theorem 5: Mode ordering by strictness
theorem mode_strictness_order :
  ∀ m, (buildConfigFor m).strictWarnings = true ↔ m = .prod := by
  intro m
  cases m <;> simp [buildConfigFor]

-- Theorem 6: All three modes are distinct
theorem modes_distinct :
  BuildMode.dev ≠ BuildMode.prod ∧ BuildMode.prod ≠ BuildMode.ultra ∧ BuildMode.dev ≠ BuildMode.ultra := by
  constructor
  · decide
  constructor
  · decide
  · decide

-- Theorem 7: Exactly three modes exist
theorem mode_count_three :
  [BuildMode.dev, BuildMode.prod, BuildMode.ultra].length = 3 := by
  rfl

-- Theorem 8: Dev mode does not validate datamodel
theorem dev_no_validate :
  (buildConfigFor .dev).validateDatamodel = false := by
  simp [buildConfigFor]

-- Theorem 9: Ultra mode does not validate datamodel
theorem ultra_no_validate :
  (buildConfigFor .ultra).validateDatamodel = false := by
  simp [buildConfigFor]

-- Theorem 10: Dev mode runs bib2gls
theorem dev_runs_bib2gls :
  (buildConfigFor .dev).runBib2gls = true := by
  simp [buildConfigFor]

end BuildModes
