import { createI18nContext } from '@solid-primitives/i18n';

import en from './en.json';
import de from './de.json';
import zh from './zh.json';

const dict = { en, de, zh };

export type Locale = keyof typeof dict;

const STORAGE_KEY = 'omnilatex-locale';

function getInitialLocale(): Locale {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem(STORAGE_KEY) as Locale | null;
    if (stored && stored in dict) return stored;
    const nav = navigator.language.split('-')[0] as Locale;
    if (nav in dict) return nav;
  }
  return 'en';
}

export const i18nContext = createI18nContext(dict, getInitialLocale());

export function setLocale(locale: Locale) {
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, locale);
  }
  const [, { locale: set }] = i18nContext;
  set(locale);
}

export function getLocale(): Locale {
  const [, { locale: get }] = i18nContext;
  return get() as Locale;
}

export const LOCALES: { value: Locale; label: string }[] = [
  { value: 'en', label: 'English' },
  { value: 'de', label: 'Deutsch' },
  { value: 'zh', label: '中文' },
];
