import type { Config } from 'jest';

const config: Config = {
  // Use ts-jest for TypeScript support
  preset: 'ts-jest',

  // Test environment
  testEnvironment: 'node',

  // Root directories to search for tests
  roots: ['<rootDir>/src'],

  // Test file patterns
  testMatch: [
    '**/*.test.ts',
    '**/*.spec.ts',
  ],

  // Files to ignore
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '.integration.test.ts',
    '.e2e.test.ts',
  ],

  // Module path aliases (match tsconfig paths)
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@test/(.*)$': '<rootDir>/test-utils/$1',
  },

  // Setup files to run after Jest is initialized
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],

  // Transform TypeScript files
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: 'tsconfig.json',
        // Enable faster transpilation
        isolatedModules: true,
      },
    ],
  },

  // Coverage configuration
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
    '!src/**/*.spec.ts',
    '!src/**/index.ts',
    '!src/types/**',
  ],

  coverageDirectory: 'coverage',

  coverageReporters: ['text', 'text-summary', 'lcov', 'html'],

  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },

  // Performance
  maxWorkers: '50%',

  // Clear mocks between tests
  clearMocks: true,

  // Restore mocks between tests
  restoreMocks: true,

  // Fail tests on console errors
  // errorOnDeprecated: true,

  // Verbose output
  verbose: true,

  // Test timeout (10 seconds)
  testTimeout: 10000,
};

export default config;
