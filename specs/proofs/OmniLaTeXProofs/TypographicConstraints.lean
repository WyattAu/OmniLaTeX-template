/-
  Formal Verification: OmniLaTeX Typographic Constraints
  Property: Line spacing, paragraph indent, word spacing, hyphen penalty, and
  related typographic parameters satisfy design invariants.

  Reference: specs/typography_constraints.toml, lib/typography/omnilatex-typesetting.sty
-/

namespace TypographicConstraints

-- Typographic parameter model
structure TypoParam where
  lineSpacing : Nat       -- in 1/1000 of baselineskip
  paragraphIndent : Nat   -- in pt
  wordSpacing : Nat       -- percent of normal (100 = normal)
  hyphenPenalty : Nat     -- integer penalty
  orphanLines : Nat       -- min lines at top of page
  widowLines : Nat        -- min lines at bottom of page
  deriving Repr

-- Ground-truth configuration
def defaultTypoParam : TypoParam := {
  lineSpacing := 1200       -- 1.2× baselineskip
  paragraphIndent := 20     -- 20pt ≈ 1.5em at 10pt
  wordSpacing := 100        -- 100% = normal
  hyphenPenalty := 50       -- moderate penalty
  orphanLines := 2
  widowLines := 2
}

-- Parameter bounds
def minLineSpacing : Nat := 1000   -- at least 1.0×
def maxLineSpacing : Nat := 2000   -- at most 2.0×
def minParagraphIndent : Nat := 0
def maxParagraphIndent : Nat := 50
def minWordSpacing : Nat := 50
def maxWordSpacing : Nat := 200

-- Theorem 1: Line spacing is at least single spacing
theorem line_spacing_at_least_single :
    defaultTypoParam.lineSpacing ≥ minLineSpacing := by
  simp [defaultTypoParam, minLineSpacing]

-- Theorem 2: Line spacing is at most double spacing
theorem line_spacing_at_most_double :
    defaultTypoParam.lineSpacing ≤ maxLineSpacing := by
  simp [defaultTypoParam, maxLineSpacing]

-- Theorem 3: Paragraph indent is non-negative
theorem paragraph_indent_nonneg :
    defaultTypoParam.paragraphIndent ≥ minParagraphIndent := by
  simp [defaultTypoParam, minParagraphIndent]

-- Theorem 4: Paragraph indent is bounded above
theorem paragraph_indent_bounded :
    defaultTypoParam.paragraphIndent ≤ maxParagraphIndent := by
  simp [defaultTypoParam, maxParagraphIndent]

-- Theorem 5: Word spacing is at least 50% (readable)
theorem word_spacing_minimal :
    defaultTypoParam.wordSpacing ≥ minWordSpacing := by
  simp [defaultTypoParam, minWordSpacing]

-- Theorem 6: Word spacing is at most 200% (not too loose)
theorem word_spacing_maximal :
    defaultTypoParam.wordSpacing ≤ maxWordSpacing := by
  simp [defaultTypoParam, maxWordSpacing]

-- Theorem 7: Hyphen penalty is positive (discourages bad breaks)
theorem hyphen_penalty_positive :
    defaultTypoParam.hyphenPenalty > 0 := by
  simp [defaultTypoParam]

-- Theorem 8: Orphan control — at least 2 lines
theorem orphan_lines_minimal :
    defaultTypoParam.orphanLines ≥ 2 := by
  simp [defaultTypoParam]

-- Theorem 9: Widow control — at least 2 lines
theorem widow_lines_minimal :
    defaultTypoParam.widowLines ≥ 2 := by
  simp [defaultTypoParam]

-- Theorem 10: Line spacing forms a valid range
theorem line_spacing_in_range :
    defaultTypoParam.lineSpacing ≥ minLineSpacing ∧
    defaultTypoParam.lineSpacing ≤ maxLineSpacing := by
  constructor
  · simp [defaultTypoParam, minLineSpacing]
  · simp [defaultTypoParam, maxLineSpacing]

-- Theorem 11: Word spacing equals 100% (normal)
theorem word_spacing_normal :
    defaultTypoParam.wordSpacing = 100 := by
  simp [defaultTypoParam]

-- Theorem 12: All parameter counts are positive (non-degenerate config)
theorem all_params_positive :
    defaultTypoParam.lineSpacing > 0 ∧
    defaultTypoParam.hyphenPenalty > 0 ∧
    defaultTypoParam.orphanLines > 0 ∧
    defaultTypoParam.widowLines > 0 := by
  constructor
  · simp [defaultTypoParam]
  constructor
  · simp [defaultTypoParam]
  constructor
  · simp [defaultTypoParam]
  · simp [defaultTypoParam]

-- Theorem 13: Orphan and widow lines are equal (symmetric policy)
theorem orphan_widow_equal :
    defaultTypoParam.orphanLines = defaultTypoParam.widowLines := by
  simp [defaultTypoParam]

-- Theorem 14: Paragraph indent is nonzero (first-line indent active)
theorem paragraph_indent_active :
    defaultTypoParam.paragraphIndent > 0 := by
  simp [defaultTypoParam]

-- Theorem 15: Parameter range is well-formed (min ≤ max for each)
theorem range_wellformed :
    minLineSpacing ≤ maxLineSpacing ∧
    minParagraphIndent ≤ maxParagraphIndent ∧
    minWordSpacing ≤ maxWordSpacing := by
  constructor
  · simp [minLineSpacing, maxLineSpacing]
  constructor
  · simp [minParagraphIndent, maxParagraphIndent]
  · simp [minWordSpacing, maxWordSpacing]

end TypographicConstraints
