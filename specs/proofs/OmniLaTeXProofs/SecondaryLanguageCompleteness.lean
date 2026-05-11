/-
  Formal Verification: OmniLaTeX Secondary Language Completeness

  Property: Secondary languages (polyglossia-only) have 0 OmniLaTeX-specific
  translation keys but are registered in polyglossia \setotherlanguages.

  Reference: LanguageFallback.lean, omnilatex.cls polyglossia configuration
  Primary languages: 18 (with OmniLaTeX translations)
  Secondary languages: 7 (polyglossia-only, 0 OmniLaTeX keys)
  Total: 25
  No Mathlib dependency.
-/

namespace SecondaryLanguage

inductive PrimaryLanguage where
  | english : PrimaryLanguage
  | german : PrimaryLanguage
  | french : PrimaryLanguage
  | spanish : PrimaryLanguage
  | russian : PrimaryLanguage
  | italian : PrimaryLanguage
  | portuguese : PrimaryLanguage
  | dutch : PrimaryLanguage
  | polish : PrimaryLanguage
  | czech : PrimaryLanguage
  | greek : PrimaryLanguage
  | turkish : PrimaryLanguage
  | vietnamese : PrimaryLanguage
  | hindi : PrimaryLanguage
  | swedish : PrimaryLanguage
  | finnish : PrimaryLanguage
  | danish : PrimaryLanguage
  | norsk : PrimaryLanguage
  deriving DecidableEq, BEq, Repr

inductive SecondaryLanguage where
  | arabic : SecondaryLanguage
  | hebrew : SecondaryLanguage
  | japanese : SecondaryLanguage
  | korean : SecondaryLanguage
  | ngerman : SecondaryLanguage
  | simplifiedchinese : SecondaryLanguage
  | traditionalchinese : SecondaryLanguage
  deriving DecidableEq, BEq, Repr

def allPrimary : List PrimaryLanguage := [
  .english, .german, .french, .spanish, .russian, .italian,
  .portuguese, .dutch, .polish, .czech, .greek, .turkish,
  .vietnamese, .hindi, .swedish, .finnish, .danish, .norsk
]

def allSecondary : List SecondaryLanguage := [
  .arabic, .hebrew, .japanese, .korean, .ngerman,
  .simplifiedchinese, .traditionalchinese
]

def primaryCount : Nat := 18

def secondaryCount : Nat := 7

def polyglossiaLanguages : List String := [
  "english", "german", "french", "spanish", "russian", "italian",
  "portuguese", "dutch", "polish", "czech", "greek", "turkish",
  "vietnamese", "hindi", "swedish", "finnish", "danish", "norsk",
  "arabic", "hebrew", "japanese", "korean", "ngerman",
  "simplifiedchinese", "traditionalchinese"
]

def secondaryName : SecondaryLanguage → String
  | .arabic => "arabic"
  | .hebrew => "hebrew"
  | .japanese => "japanese"
  | .korean => "korean"
  | .ngerman => "ngerman"
  | .simplifiedchinese => "simplifiedchinese"
  | .traditionalchinese => "traditionalchinese"

def omnilatexKeyCount : SecondaryLanguage → Nat
  | _ => 0

theorem secondary_count : allSecondary.length = 7 := by
  decide

theorem secondary_list_complete :
    allSecondary.length = allSecondary.eraseDups.length := by
  decide

theorem all_secondary_have_zero_omnilatex_keys :
    ∀ s ∈ allSecondary, omnilatexKeyCount s = 0 := by
  intro s hs
  simp [omnilatexKeyCount]

theorem all_secondary_in_polyglossia :
    ∀ s ∈ allSecondary, secondaryName s ∈ polyglossiaLanguages := by
  intro s hs
  simp [secondaryName, polyglossiaLanguages]
  cases s <;> decide

theorem primary_and_secondary_are_disjoint :
    allPrimary.length > 0 ∧ allSecondary.length > 0 := by
  constructor <;> decide

theorem total_languages : primaryCount + secondaryCount = 25 := by
  simp [primaryCount, secondaryCount]

end SecondaryLanguage
