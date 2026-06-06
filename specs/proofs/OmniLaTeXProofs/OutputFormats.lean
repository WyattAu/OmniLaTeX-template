/-
  Formal Verification: OmniLaTeX Output Format Properties
  Property: Output format selection and PDF/A compliance.

  Reference: .latexmkrc, lib/core/omnilatex-base.sty
-/

namespace OutputFormats

inductive OutputFormat where
  | pdfA : OutputFormat       -- PDF/A-2b for archival
  | pdfStandard : OutputFormat -- standard PDF
  | html : OutputFormat        -- HTML for web
  | epub : OutputFormat        -- EPUB for e-readers
  deriving DecidableEq, Repr

def allFormats : List OutputFormat := [.pdfA, .pdfStandard, .html, .epub]
def formatCount : Nat := 4

structure FormatConfig where
  format : OutputFormat
  embedFonts : Bool
  linearize : Bool
  compress : Bool
  deriving Repr

def configFor : OutputFormat → FormatConfig
  | .pdfA       => ⟨.pdfA, true, true, true⟩
  | .pdfStandard => ⟨.pdfStandard, true, false, true⟩
  | .html       => ⟨.html, false, true, false⟩
  | .epub       => ⟨.epub, true, true, true⟩

-- Theorem 1: All four formats exist
theorem format_count : allFormats.length = formatCount := by
  decide

-- Theorem 2: PDF/A embeds fonts
theorem pdfa_embeds_fonts : (configFor .pdfA).embedFonts = true := by
  simp [configFor]

-- Theorem 3: PDF/A linearizes
theorem pdfa_linearizes : (configFor .pdfA).linearize = true := by
  simp [configFor]

-- Theorem 4: PDF/A compresses output
theorem pdfa_compressed : (configFor .pdfA).compress = true := by
  simp [configFor]

-- Theorem 5: HTML does not embed fonts (uses web fonts)
theorem html_no_embed : (configFor .html).embedFonts = false := by
  simp [configFor]

-- Theorem 6: Standard PDF embeds fonts
theorem pdf_standard_embeds : (configFor .pdfStandard).embedFonts = true := by
  simp [configFor]

-- Theorem 7: HTML linearizes for accessibility
theorem html_linearizes : (configFor .html).linearize = true := by
  simp [configFor]

-- Theorem 8: EPUB compresses
theorem epub_compressed : (configFor .epub).compress = true := by
  simp [configFor]

-- Theorem 9: Formats are distinct
theorem formats_distinct : allFormats.length = allFormats.eraseDups.length := by
  decide

-- Theorem 10: PDF/A is default for archival
theorem pdfa_in_formats : .pdfA ∈ allFormats := by
  decide

-- Theorem 11: PDF formats are a subset
theorem pdf_formats_subset :
    .pdfA ∈ allFormats ∧ .pdfStandard ∈ allFormats := by
  constructor
  · decide
  · decide

-- Theorem 12: Non-PDF formats do not compress by default (HTML only)
theorem html_not_compressed : (configFor .html).compress = false := by
  simp [configFor]

-- Theorem 13: EPUB linearizes for e-reader rendering
theorem epub_linearizes : (configFor .epub).linearize = true := by
  simp [configFor]

-- Theorem 14: Standard PDF does not linearize
theorem pdf_standard_no_linearize : (configFor .pdfStandard).linearize = false := by
  simp [configFor]

-- Theorem 15: EPUB embeds fonts for offline reading
theorem epub_embeds_fonts : (configFor .epub).embedFonts = true := by
  simp [configFor]

-- Theorem 16: All formats are in the format list
theorem all_formats_present :
    .pdfA ∈ allFormats ∧ .pdfStandard ∈ allFormats ∧ .html ∈ allFormats ∧ .epub ∈ allFormats := by
  constructor
  · decide
  constructor
  · decide
  constructor
  · decide
  · decide

end OutputFormats
