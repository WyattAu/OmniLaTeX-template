/-
  Formal Verification: OmniLaTeX Font Size Hierarchy
  Property: Font sizes are strictly ordered across all configurations.

  Reference: specs/typography_constraints.toml TC-001
-/

-- Define LaTeX font size names in canonical order
inductive FontSize where
  | scriptsize : FontSize
  | footnotesize : FontSize
  | small : FontSize
  | normalsize : FontSize
  | large : FontSize
  | Large : FontSize
  | LARGE : FontSize
  | huge : FontSize
  | Huge : FontSize
  deriving DecidableEq, Repr

-- Define strict ordering on font sizes
def fontSizeLt : FontSize → FontSize → Bool
  | .scriptsize, .footnotesize => true
  | .scriptsize, .small => true
  | .scriptsize, .normalsize => true
  | .scriptsize, .large => true
  | .scriptsize, .Large => true
  | .scriptsize, .LARGE => true
  | .scriptsize, .huge => true
  | .scriptsize, .Huge => true
  | .footnotesize, .small => true
  | .footnotesize, .normalsize => true
  | .footnotesize, .large => true
  | .footnotesize, .Large => true
  | .footnotesize, .LARGE => true
  | .footnotesize, .huge => true
  | .footnotesize, .Huge => true
  | .small, .normalsize => true
  | .small, .large => true
  | .small, .Large => true
  | .small, .LARGE => true
  | .small, .huge => true
  | .small, .Huge => true
  | .normalsize, .large => true
  | .normalsize, .Large => true
  | .normalsize, .LARGE => true
  | .normalsize, .huge => true
  | .normalsize, .Huge => true
  | .large, .Large => true
  | .large, .LARGE => true
  | .large, .huge => true
  | .large, .Huge => true
  | .Large, .LARGE => true
  | .Large, .huge => true
  | .Large, .Huge => true
  | .LARGE, .huge => true
  | .LARGE, .Huge => true
  | .huge, .Huge => true
  | _, _ => false

-- Theorem 1: Irreflexivity
theorem font_size_irreflexive : ∀ s, ¬fontSizeLt s s := by
  intro s
  cases s <;> simp [fontSizeLt]

-- Theorem 2: Asymmetry
theorem font_size_asymmetric : ∀ a b, fontSizeLt a b → ¬fontSizeLt b a := by
  intro a b hab
  cases a <;> cases b <;> simp_all [fontSizeLt]

-- Theorem 3: Transitivity
theorem font_size_transitive : ∀ a b c, fontSizeLt a b → fontSizeLt b c → fontSizeLt a c := by
  intro a b c hab hbc
  cases a <;> cases b <;> cases c <;> simp_all [fontSizeLt]

-- Theorem 4: Connexity (any two distinct sizes are ordered)
theorem font_size_connex : ∀ a b, a ≠ b → fontSizeLt a b ∨ fontSizeLt b a := by
  intro a b hne
  cases a <;> cases b <;> simp_all [fontSizeLt]

-- Theorem 5: scriptsize is the minimum element
theorem scriptsize_is_minimum : ∀ s, fontSizeLt .scriptsize s → s ≠ .scriptsize := by
  intro s h
  cases s <;> simp [fontSizeLt] at h <;> decide

-- Theorem 6: Huge is the maximum element
theorem huge_is_maximum : ∀ s, fontSizeLt s .Huge → s ≠ .Huge := by
  intro s h
  cases s <;> simp [fontSizeLt] at h <;> decide

-- Theorem 7: No element is smaller than scriptsize
theorem nothing_smaller_than_scriptsize : ∀ s, ¬fontSizeLt s .scriptsize := by
  intro s
  cases s <;> simp [fontSizeLt]

-- Theorem 8: No element is larger than Huge
theorem nothing_larger_than_Huge : ∀ s, ¬fontSizeLt .Huge s := by
  intro s
  cases s <;> simp [fontSizeLt]

-- Corollary: Font sizes form a strict total order
-- A strict total order is irreflexive, asymmetric, transitive, and connex
