# Jest Patterns

## Table of Contents
- [Configuration](#configuration)
- [Lifecycle Hooks](#lifecycle-hooks)
- [Assertions](#assertions)
- [Parameterized Tests](#parameterized-tests)
- [Test Filtering](#test-filtering)
- [Coverage](#coverage)

## Configuration

### Basic Setup

```bash
npm install -D jest @types/jest ts-jest
```

### TypeScript Configuration

See [assets/jest.config.ts](../assets/jest.config.ts) for a complete config.

Key settings:

```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/*.test.ts', '**/*.spec.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/index.ts',
  ],
};

export default config;
```

### Setup File

```typescript
// jest.setup.ts
import { jest } from '@jest/globals';

// Extend expect with custom matchers
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

// Global test timeout
jest.setTimeout(10000);

// Reset mocks between tests
beforeEach(() => {
  jest.clearAllMocks();
});
```

## Lifecycle Hooks

### Execution Order

```typescript
describe('outer', () => {
  beforeAll(() => console.log('1. outer beforeAll'));
  afterAll(() => console.log('6. outer afterAll'));
  beforeEach(() => console.log('2. outer beforeEach'));
  afterEach(() => console.log('4. outer afterEach'));

  describe('inner', () => {
    beforeEach(() => console.log('3. inner beforeEach'));
    afterEach(() => console.log('3.5. inner afterEach'));

    it('test', () => console.log('3.25. test'));
  });
});

// Output:
// 1. outer beforeAll
// 2. outer beforeEach
// 3. inner beforeEach
// 3.25. test
// 3.5. inner afterEach
// 4. outer afterEach
// 6. outer afterAll
```

### Shared Test Context

```typescript
describe('UserService', () => {
  let userService: UserService;
  let mockRepo: MockOf<UserRepository>;

  beforeEach(() => {
    mockRepo = createMock<UserRepository>();
    userService = new UserService(mockRepo);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('should_find_user_when_exists', async () => {
    mockRepo.findById.mockResolvedValue(createUser());
    const user = await userService.getUser('1');
    expect(user).toBeDefined();
  });
});
```

### Async Lifecycle

```typescript
describe('Database tests', () => {
  let connection: DatabaseConnection;

  beforeAll(async () => {
    connection = await createTestDatabase();
    await connection.migrate();
  });

  afterAll(async () => {
    await connection.close();
  });

  beforeEach(async () => {
    await connection.truncateAll();
  });
});
```

## Assertions

### Basic Assertions

```typescript
// Equality
expect(2 + 2).toBe(4);                    // ===
expect({ a: 1 }).toEqual({ a: 1 });       // Deep equality
expect(obj).toStrictEqual(expected);      // Deep + type check

// Truthiness
expect(true).toBeTruthy();
expect(false).toBeFalsy();
expect(null).toBeNull();
expect(undefined).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeGreaterThanOrEqual(3);
expect(value).toBeLessThan(5);
expect(0.1 + 0.2).toBeCloseTo(0.3);

// Strings
expect('hello world').toMatch(/world/);
expect(str).toContain('substring');
expect(str).toHaveLength(5);

// Arrays
expect([1, 2, 3]).toContain(2);
expect(arr).toHaveLength(3);
expect(arr).toEqual(expect.arrayContaining([1, 2]));

// Objects
expect(obj).toHaveProperty('key');
expect(obj).toHaveProperty('nested.key', 'value');
expect(obj).toMatchObject({ partial: 'match' });
```

### Asymmetric Matchers

```typescript
expect(obj).toEqual({
  id: expect.any(String),
  count: expect.any(Number),
  items: expect.arrayContaining([
    expect.objectContaining({ name: 'test' })
  ]),
  createdAt: expect.any(Date),
});

expect(callback).toHaveBeenCalledWith(
  expect.stringContaining('error'),
  expect.objectContaining({ code: 'ERR_001' })
);
```

### Error Assertions

```typescript
// Sync errors
expect(() => {
  throw new Error('fail');
}).toThrow('fail');

expect(() => fn()).toThrow(ValidationError);
expect(() => fn()).toThrow(/invalid/i);

// Async errors
await expect(asyncFn()).rejects.toThrow('message');
await expect(asyncFn()).rejects.toBeInstanceOf(NotFoundError);

// Detailed error checking
await expect(asyncFn()).rejects.toMatchObject({
  message: 'Not found',
  code: 'NOT_FOUND',
});
```

### Negation

```typescript
expect(value).not.toBe(5);
expect(arr).not.toContain(item);
expect(fn).not.toHaveBeenCalled();
```

## Parameterized Tests

### test.each

```typescript
// Array format
test.each([
  [1, 1, 2],
  [1, 2, 3],
  [2, 1, 3],
])('add(%i, %i) = %i', (a, b, expected) => {
  expect(add(a, b)).toBe(expected);
});

// Object format (preferred for readability)
test.each([
  { input: 'test@example.com', valid: true },
  { input: 'invalid', valid: false },
  { input: '', valid: false },
])('validateEmail($input) returns $valid', ({ input, valid }) => {
  expect(validateEmail(input)).toBe(valid);
});

// Template literal format
test.each`
  a    | b    | expected
  ${1} | ${1} | ${2}
  ${1} | ${2} | ${3}
  ${2} | ${1} | ${3}
`('add($a, $b) = $expected', ({ a, b, expected }) => {
  expect(add(a, b)).toBe(expected);
});
```

### describe.each

```typescript
describe.each([
  { role: 'admin', canDelete: true },
  { role: 'user', canDelete: false },
  { role: 'guest', canDelete: false },
])('$role permissions', ({ role, canDelete }) => {
  it(`should ${canDelete ? 'allow' : 'deny'} delete`, () => {
    const user = createUser({ role });
    expect(userService.canDelete(user)).toBe(canDelete);
  });
});
```

### Table-Driven Tests

```typescript
interface TestCase {
  name: string;
  input: CreateOrderDto;
  expected?: Order;
  shouldThrow?: new (...args: any[]) => Error;
}

const testCases: TestCase[] = [
  {
    name: 'should_create_order_when_valid_input',
    input: { customerId: '1', items: [{ productId: 'p1', quantity: 1 }] },
    expected: expect.objectContaining({ status: 'pending' }),
  },
  {
    name: 'should_throw_when_no_items',
    input: { customerId: '1', items: [] },
    shouldThrow: ValidationError,
  },
];

describe('OrderService.createOrder', () => {
  test.each(testCases)('$name', async ({ input, expected, shouldThrow }) => {
    if (shouldThrow) {
      await expect(orderService.createOrder(input)).rejects.toThrow(shouldThrow);
    } else {
      const result = await orderService.createOrder(input);
      expect(result).toEqual(expected);
    }
  });
});
```

## Test Filtering

### Running Specific Tests

```bash
# Run tests matching pattern
jest --testNamePattern="should_create"
jest -t "should_create"

# Run specific file
jest user.service.test.ts

# Run tests in directory
jest src/features/orders/
```

### Skip and Focus

```typescript
// Skip tests
it.skip('should_skip_this_test', () => {});
describe.skip('skipped suite', () => {});

// Focus on specific tests (runs only these)
it.only('should_run_only_this', () => {});
describe.only('focused suite', () => {});

// Conditional skip
const isCI = process.env.CI === 'true';
(isCI ? it.skip : it)('should_skip_on_ci', () => {});
```

### Todo Tests

```typescript
it.todo('should_implement_later');
```

## Coverage

### Configuration

```typescript
// jest.config.ts
const config: Config = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.d.ts',
    '!src/**/*.test.ts',
    '!src/**/index.ts',
    '!src/types/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
    './src/features/orders/': {
      branches: 90,
      lines: 90,
    },
  },
};
```

### Running with Coverage

```bash
# Generate coverage report
jest --coverage

# Watch mode without coverage (faster)
jest --watch --coverage=false
```

### Coverage Comments

```typescript
// Ignore specific lines
/* istanbul ignore next */
if (process.env.DEBUG) {
  console.log('debug info');
}

// Ignore branch
/* istanbul ignore else */
if (condition) {
  doSomething();
}
```
