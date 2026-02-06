import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    // Enable global test APIs (describe, it, expect)
    globals: true,

    // Test environment
    environment: 'node',

    // Test file patterns
    include: ['src/**/*.{test,spec}.ts'],

    // Files to exclude
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/*.integration.test.ts',
      '**/*.e2e.test.ts',
    ],

    // Setup files
    setupFiles: ['./vitest.setup.ts'],

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'text-summary', 'lcov', 'html'],
      reportsDirectory: './coverage',
      include: ['src/**/*.ts'],
      exclude: [
        '**/*.d.ts',
        '**/*.test.ts',
        '**/*.spec.ts',
        '**/index.ts',
        '**/types/**',
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },

    // Test timeout (10 seconds)
    testTimeout: 10000,

    // Hook timeout (10 seconds)
    hookTimeout: 10000,

    // Fail on console errors
    // onConsoleLog: () => false,

    // Watch mode exclude
    watchExclude: ['**/node_modules/**', '**/dist/**'],

    // Pool options for parallel execution
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
      },
    },

    // Retry failed tests
    retry: 0,

    // Reporter
    reporters: ['verbose'],
  },

  // Path aliases (match tsconfig paths)
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@test': path.resolve(__dirname, './test-utils'),
    },
  },
});
