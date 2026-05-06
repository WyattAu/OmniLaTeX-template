import Init

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
  | norwegian : PrimaryLanguage
  deriving DecidableEq, BEq, Repr

inductive SecondaryLanguage where
  | arabic : SecondaryLanguage
  | hebrew : SecondaryLanguage
  | persian : SecondaryLanguage
  | chineseSimplified : SecondaryLanguage
  | chineseTraditional : SecondaryLanguage
  | japanese : SecondaryLanguage
  | korean : SecondaryLanguage
  | ukrainian : SecondaryLanguage
  | serbian : SecondaryLanguage
  | croatian : SecondaryLanguage
  | bulgarian : SecondaryLanguage
  | romanian : SecondaryLanguage
  | hungarian : SecondaryLanguage
  | slovak : SecondaryLanguage
  | slovenian : SecondaryLanguage
  | latvian : SecondaryLanguage
  | lithuanian : SecondaryLanguage
  | estonian : SecondaryLanguage
  | thai : SecondaryLanguage
  | indonesian : SecondaryLanguage
  | malay : SecondaryLanguage
  | catalan : SecondaryLanguage
  | basque : SecondaryLanguage
  | galician : SecondaryLanguage
  | welsh : SecondaryLanguage
  | irish : SecondaryLanguage
  deriving DecidableEq, BEq, Repr

def allPrimary : List PrimaryLanguage := [
  .english, .german, .french, .spanish, .russian, .italian,
  .portuguese, .dutch, .polish, .czech, .greek, .turkish,
  .vietnamese, .hindi, .swedish, .finnish, .danish, .norwegian
]

def primary_count : Nat := 18

def secondary_count : Nat := 26

def fallback : PrimaryLanguage → PrimaryLanguage
  | .english => .english
  | _ => .english

theorem primary_count_eq : allPrimary.length = primary_count := by
  decide

theorem primary_no_duplicates : allPrimary.length = allPrimary.eraseDups.length := by
  decide

theorem english_is_fallback_root : fallback .english = .english := by
  decide

theorem fallback_terminates : ∀ l, fallback l = .english := by
  intro l; cases l <;> rfl

theorem fallback_stable : ∀ l, fallback (fallback l) = fallback l := by
  intro l; cases l <;> rfl

theorem total_language_coverage : primary_count + secondary_count = 44 := by
  simp [primary_count, secondary_count]
