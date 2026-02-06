# Vitest Patterns

## Table of Contents
- [Why Vitest](#why-vitest)
- [Configuration](#configuration)
- [Jest Migration](#jest-migration)
- [Vitest-Specific Features](#vitest-specific-features)
- [Inline Tests](#inline-tests)
- [Workspaces](#workspaces)

## Why Vitest

Vitest is a fast unit test framework powered by Vite. Choose Vitest when:

- Your project already uses Vite
- You want faster test execution (native ESM, no compilation)
- You need first-class TypeScript support without ts-jest
- You want a modern, Jest-compatible API

## Configuration

### Basic Setup

```bash
npm install -D vitest
```

### Configuration File

See [assets/vitest.config.ts](../assets/vitest.config.ts) for a complete config.

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.{test,spec}.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['**/*.d.ts', '**/index.ts', '**/*.test.ts'],
    },
    setupFiles: ['./vitest.setup.ts'],
  },
  resolve: {
    alias: {
      '@': './src',
    },
  },
});
```

### Setup File

```typescript
// vitest.setup.ts
import { beforeEach, vi } from 'vitest';

// Reset mocks between tests
beforeEach(() => {
  vi.clearAllMocks();
});

// Custom matchers
expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    return {
      pass,
      message: () =>
        `expected ${received} ${pass ? 'not ' : ''}to be within ${floor}-${ceiling}`,
    };
  },
});
```

### TypeScript Types

```typescript
// vitest.d.ts
import 'vitest';

interface CustomMatchers<R = unknown> {
  toBeWithinRange(floor: number, ceiling: number): R;
}

declare module 'vitest' {
  interface Assertion<T = any> extends CustomMatchers<T> {}
  interface AsymmetricMatchersContaining extends CustomMatchers {}
}
```

## Jest Migration

### API Differences

| Jest | Vitest |
|------|--------|
| `jest.fn()` | `vi.fn()` |
| `jest.mock()` | `vi.mock()` |
| `jest.spyOn()` | `vi.spyOn()` |
| `jest.useFakeTimers()` | `vi.useFakeTimers()` |
| `jest.clearAllMocks()` | `vi.clearAllMocks()` |
| `jest.setTimeout()` | `vi.setConfig({ testTimeout: n })` |

### Import Changes

```typescript
// Jest
import { jest } from '@jest/globals';

// Vitest
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Or with globals: true in config, no imports needed
```

### Mock Differences

```typescript
// Jest
jest.mock('./module', () => ({
  default: jest.fn(),
  namedExport: jest.fn(),
}));

// Vitest
vi.mock('./module', () => ({
  default: vi.fn(),
  namedExport: vi.fn(),
}));

// Vitest auto-mocking
vi.mock('./module'); // Auto-mocks all exports
```

### Snapshot Differences

```typescript
// Jest - inline snapshots require Prettier
expect(value).toMatchInlineSnapshot();

// Vitest - works without Prettier, uses native formatting
expect(value).toMatchInlineSnapshot();
```

## Vitest-Specific Features

### Type Testing

```typescript
import { expectTypeOf, assertType } from 'vitest';

test('type assertions', () => {
  expectTypeOf({ a: 1 }).toMatchTypeOf<{ a: number }>();
  expectTypeOf<string>().toBeString();

  const fn = (x: number) => String(x);
  expectTypeOf(fn).parameters.toEqualTypeOf<[number]>();
  expectTypeOf(fn).returns.toEqualTypeOf<string>();
});

test('assert type', () => {
  const value = getValue();
  assertType<string>(value); // Fails compilation if wrong
});
```

### Concurrent Tests

```typescript
// Run tests in parallel
describe.concurrent('parallel tests', () => {
  it('test 1', async () => { /* ... */ });
  it('test 2', async () => { /* ... */ });
  it('test 3', async () => { /* ... */ });
});

// Or individual tests
it.concurrent('parallel test', async () => { /* ... */ });
```

### Test Context

```typescript
import { test } from 'vitest';

test('access test context', ({ expect, task }) => {
  console.log(task.name); // Test name
  expect(true).toBe(true);
});

// Extend context
interface CustomContext {
  db: Database;
}

const myTest = test.extend<CustomContext>({
  db: async ({}, use) => {
    const db = await createTestDatabase();
    await use(db);
    await db.close();
  },
});

myTest('with db context', async ({ db }) => {
  const users = await db.query('SELECT * FROM users');
  expect(users).toHaveLength(0);
});
```

### Benchmarking

```typescript
import { bench, describe } from 'vitest';

describe('array methods', () => {
  const array = Array.from({ length: 1000 }, (_, i) => i);

  bench('map', () => {
    array.map(x => x * 2);
  });

  bench('for loop', () => {
    const result = [];
    for (const x of array) {
      result.push(x * 2);
    }
  });
});
```

### Source Code Coverage

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',        // or 'istanbul'
      reporter: ['text', 'json', 'html'],
      include: ['src/**/*.ts'],
      exclude: ['**/*.test.ts'],
      all: true,             // Include uncovered files
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80,
      },
    },
  },
});
```

## Inline Tests

Vitest allows tests in source files (dev only):

```typescript
// math.ts
export function add(a: number, b: number): number {
  return a + b;
}

// In-source tests
if (import.meta.vitest) {
  const { describe, it, expect } = import.meta.vitest;

  describe('add', () => {
    it('should add two numbers', () => {
      expect(add(1, 2)).toBe(3);
    });
  });
}
```

Enable in config:

```typescript
// vitest.config.ts
export default defineConfig({
  define: {
    'import.meta.vitest': 'undefined', // Remove in production
  },
  test: {
    includeSource: ['src/**/*.ts'],
  },
});
```

## Workspaces

For monorepos with different test configurations:

```typescript
// vitest.workspace.ts
import { defineWorkspace } from 'vitest/config';

export default defineWorkspace([
  {
    test: {
      name: 'unit',
      include: ['src/**/*.test.ts'],
      environment: 'node',
    },
  },
  {
    test: {
      name: 'integration',
      include: ['tests/integration/**/*.test.ts'],
      environment: 'node',
      setupFiles: ['./tests/integration/setup.ts'],
    },
  },
  {
    test: {
      name: 'browser',
      include: ['src/**/*.browser.test.ts'],
      browser: {
        enabled: true,
        name: 'chromium',
      },
    },
  },
]);
```

Run specific workspace:

```bash
vitest --project=unit
vitest --project=integration
```

## Watch Mode

```bash
# Watch mode (default)
vitest

# Run once
vitest run

# Watch specific files
vitest --watch src/features/

# UI mode
vitest --ui
```

## Filtering Tests

```bash
# By name pattern
vitest -t "should_create"

# By file pattern
vitest user.service

# Skip tests
vitest --exclude "**/integration/**"
```
