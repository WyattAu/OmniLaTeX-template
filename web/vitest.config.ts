import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['tests/**/*.{test,spec}.{ts,tsx}'],
    pool: 'forks',
    singleThread: true,
    server: {
      deps: {
        inline: ['solid-js', '@solidjs/testing-library'],
      },
    },
  },
  resolve: {
    conditions: ['browser', 'development'],
  },
});
