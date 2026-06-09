/** Generate a human-readable title from a slug. */
export function slugToTitle(slug: string): string {
  return slug
    .replace(/\.md$/, '')
    .split('/')
    .map(part => part.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()))
    .join(' / ');
}

/** Resolve the Astro base URL, ensuring a trailing slash. */
export function getBaseURL(): string {
  return '/';
}
