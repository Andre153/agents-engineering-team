# TypeScript Testing Patterns

## Table of Contents
- [Type-Safe Mocks](#type-safe-mocks)
- [Test Fixtures](#test-fixtures)
- [Dependency Injection for Testing](#dependency-injection-for-testing)
- [Async Testing](#async-testing)
- [Snapshot Testing](#snapshot-testing)
- [Test Organization](#test-organization)

## Type-Safe Mocks

### Auto-Mock Factory

```typescript
type MockOf<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R
    ? jest.Mock<R, A>
    : T[K];
};

function createMock<T extends object>(): MockOf<T> {
  return new Proxy({} as MockOf<T>, {
    get: (target, prop) => {
      if (!(prop in target)) {
        (target as Record<string | symbol, unknown>)[prop] = jest.fn();
      }
      return (target as Record<string | symbol, unknown>)[prop];
    },
  });
}

// Usage
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
  delete(id: string): Promise<boolean>;
}

const mockRepo = createMock<UserRepository>();
mockRepo.findById.mockResolvedValue({ id: '1', name: 'Test' });
mockRepo.save.mockResolvedValue(undefined);

// Type-safe - TypeScript knows the return types
const user = await mockRepo.findById('1'); // User | null
```

### Partial Mock with Defaults

```typescript
function createPartialMock<T extends object>(
  overrides: Partial<MockOf<T>> = {}
): MockOf<T> {
  const base = createMock<T>();
  return { ...base, ...overrides };
}

// Usage with specific implementations
const mockRepo = createPartialMock<UserRepository>({
  findById: jest.fn().mockImplementation(async (id) => {
    if (id === 'existing') return { id, name: 'Found' };
    return null;
  }),
});
```

### Spy Wrapper

```typescript
type SpyOf<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R
    ? jest.SpyInstance<R, A>
    : T[K];
};

function spyOnAll<T extends object>(obj: T): SpyOf<T> {
  const spied = {} as SpyOf<T>;

  for (const key of Object.keys(obj) as (keyof T)[]) {
    const value = obj[key];
    if (typeof value === 'function') {
      spied[key] = jest.spyOn(obj, key as any) as any;
    } else {
      spied[key] = value as any;
    }
  }

  return spied;
}
```

## Test Fixtures

### Factory Pattern

```typescript
// Base factory
function createUserFactory(defaults: Partial<User> = {}) {
  let counter = 0;

  return (overrides: Partial<User> = {}): User => {
    counter++;
    return {
      id: `user-${counter}`,
      name: `User ${counter}`,
      email: `user${counter}@test.com`,
      createdAt: new Date(),
      ...defaults,
      ...overrides,
    };
  };
}

const createUser = createUserFactory();
const createAdminUser = createUserFactory({ role: 'admin' });

// Usage
const user1 = createUser(); // user-1
const user2 = createUser({ name: 'Custom' }); // user-2 with custom name
const admin = createAdminUser(); // admin with role: 'admin'

// Builder pattern for complex objects
class UserBuilder {
  private user: Partial<User> = {};

  withId(id: string): this {
    this.user.id = id;
    return this;
  }

  withName(name: string): this {
    this.user.name = name;
    return this;
  }

  withEmail(email: string): this {
    this.user.email = email;
    return this;
  }

  withRole(role: 'admin' | 'user'): this {
    this.user.role = role;
    return this;
  }

  build(): User {
    return {
      id: this.user.id ?? `user-${Date.now()}`,
      name: this.user.name ?? 'Test User',
      email: this.user.email ?? 'test@test.com',
      role: this.user.role ?? 'user',
      createdAt: new Date(),
    };
  }
}

// Usage
const user = new UserBuilder()
  .withName('Alice')
  .withRole('admin')
  .build();
```

### Fixture Files

```typescript
// fixtures/users.ts
export const testUsers = {
  alice: {
    id: 'user-alice',
    name: 'Alice',
    email: 'alice@test.com',
    role: 'admin' as const,
  },
  bob: {
    id: 'user-bob',
    name: 'Bob',
    email: 'bob@test.com',
    role: 'user' as const,
  },
} as const;

// Type-safe fixture access
type TestUserKey = keyof typeof testUsers;
type TestUser = typeof testUsers[TestUserKey];

// Usage in tests
import { testUsers } from './fixtures/users';

test('admin can access dashboard', () => {
  const result = checkAccess(testUsers.alice, '/dashboard');
  expect(result).toBe(true);
});
```

## Dependency Injection for Testing

### Constructor Injection

```typescript
interface Dependencies {
  userRepository: UserRepository;
  emailService: EmailService;
  logger: Logger;
}

class UserService {
  constructor(private readonly deps: Dependencies) {}

  async createUser(dto: CreateUserDto): Promise<User> {
    const user = await this.deps.userRepository.save(dto);
    await this.deps.emailService.sendWelcome(user.email);
    this.deps.logger.info('User created', { userId: user.id });
    return user;
  }
}

// Test setup
function createTestService(overrides: Partial<Dependencies> = {}) {
  const defaults: Dependencies = {
    userRepository: createMock<UserRepository>(),
    emailService: createMock<EmailService>(),
    logger: createMock<Logger>(),
  };

  const deps = { ...defaults, ...overrides };
  return { service: new UserService(deps), deps };
}

// Usage
test('createUser sends welcome email', async () => {
  const { service, deps } = createTestService();
  deps.userRepository.save.mockResolvedValue({ id: '1', email: 'test@test.com' });

  await service.createUser({ email: 'test@test.com' });

  expect(deps.emailService.sendWelcome).toHaveBeenCalledWith('test@test.com');
});
```

### Context Pattern

```typescript
interface TestContext {
  userService: UserService;
  mocks: {
    userRepository: MockOf<UserRepository>;
    emailService: MockOf<EmailService>;
  };
}

function setupTest(): TestContext {
  const mocks = {
    userRepository: createMock<UserRepository>(),
    emailService: createMock<EmailService>(),
  };

  const userService = new UserService({
    userRepository: mocks.userRepository,
    emailService: mocks.emailService,
    logger: createMock<Logger>(),
  });

  return { userService, mocks };
}

describe('UserService', () => {
  let ctx: TestContext;

  beforeEach(() => {
    ctx = setupTest();
  });

  test('creates user', async () => {
    ctx.mocks.userRepository.save.mockResolvedValue({ id: '1' });
    const user = await ctx.userService.createUser({ email: 'test@test.com' });
    expect(user.id).toBe('1');
  });
});
```

## Async Testing

### Waiting for Conditions

```typescript
async function waitFor<T>(
  fn: () => T | Promise<T>,
  options: { timeout?: number; interval?: number } = {}
): Promise<T> {
  const { timeout = 5000, interval = 50 } = options;
  const start = Date.now();

  while (Date.now() - start < timeout) {
    try {
      const result = await fn();
      if (result) return result;
    } catch {
      // Continue waiting
    }
    await new Promise(resolve => setTimeout(resolve, interval));
  }

  throw new Error(`Timed out after ${timeout}ms`);
}

// Usage
test('eventually updates state', async () => {
  const service = new AsyncService();
  service.startProcessing();

  await waitFor(() => service.isComplete);
  expect(service.result).toBeDefined();
});
```

### Testing Event Emitters

```typescript
function waitForEvent<T>(
  emitter: EventEmitter,
  eventName: string,
  timeout = 5000
): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`Event ${eventName} not received within ${timeout}ms`));
    }, timeout);

    emitter.once(eventName, (data: T) => {
      clearTimeout(timer);
      resolve(data);
    });
  });
}

// Usage
test('emits completion event', async () => {
  const processor = new EventProcessor();
  const resultPromise = waitForEvent<ProcessResult>(processor, 'complete');

  processor.start();

  const result = await resultPromise;
  expect(result.status).toBe('success');
});
```

### Testing Streams

```typescript
async function collectStream<T>(stream: AsyncIterable<T>): Promise<T[]> {
  const items: T[] = [];
  for await (const item of stream) {
    items.push(item);
  }
  return items;
}

test('processes all items', async () => {
  const input = [1, 2, 3, 4, 5];
  const stream = processItems(asyncIterableFrom(input));

  const results = await collectStream(stream);

  expect(results).toHaveLength(5);
  expect(results.every(r => r.processed)).toBe(true);
});
```

## Snapshot Testing

### Custom Serializers

```typescript
// Custom serializer for dates
expect.addSnapshotSerializer({
  test: (val) => val instanceof Date,
  print: (val) => `Date(${(val as Date).toISOString()})`,
});

// Serializer for removing volatile fields
function removeVolatileFields<T extends object>(obj: T): Partial<T> {
  const { id, createdAt, updatedAt, ...rest } = obj as any;
  return rest;
}

test('user matches snapshot', () => {
  const user = createUser();
  expect(removeVolatileFields(user)).toMatchSnapshot();
});
```

### Inline Snapshots

```typescript
test('formats error message', () => {
  const error = new ValidationError('Invalid email', {
    email: ['must be valid email'],
  });

  expect(error.format()).toMatchInlineSnapshot(`
    "Validation Error: Invalid email
    - email: must be valid email"
  `);
});
```

## Test Organization

### Describe Blocks

```typescript
describe('UserService', () => {
  describe('createUser', () => {
    describe('with valid input', () => {
      test('creates user in repository', async () => {});
      test('sends welcome email', async () => {});
      test('logs creation event', async () => {});
    });

    describe('with invalid input', () => {
      test('throws ValidationError for missing email', async () => {});
      test('throws ValidationError for invalid email format', async () => {});
    });

    describe('when repository fails', () => {
      test('throws and does not send email', async () => {});
    });
  });
});
```

### Test Helpers

```typescript
// test-utils.ts
export function expectToThrowAsync(
  fn: () => Promise<unknown>,
  errorType?: new (...args: any[]) => Error
): Promise<void> {
  return expect(fn()).rejects.toThrow(errorType);
}

export function expectNotToThrowAsync(
  fn: () => Promise<unknown>
): Promise<void> {
  return expect(fn()).resolves.not.toThrow();
}

// Custom matchers
expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    return {
      pass,
      message: () =>
        `expected ${received} ${pass ? 'not ' : ''}to be within range ${floor} - ${ceiling}`,
    };
  },
});

declare global {
  namespace jest {
    interface Matchers<R> {
      toBeWithinRange(floor: number, ceiling: number): R;
    }
  }
}

// Usage
expect(result.latency).toBeWithinRange(0, 1000);
```

### Parameterized Tests

```typescript
describe.each([
  { input: 'test@example.com', valid: true },
  { input: 'invalid', valid: false },
  { input: '', valid: false },
  { input: 'user@domain', valid: false },
])('validateEmail($input)', ({ input, valid }) => {
  test(`returns ${valid}`, () => {
    expect(validateEmail(input)).toBe(valid);
  });
});

// Table-driven tests
const testCases: Array<{
  name: string;
  input: CreateUserDto;
  expected: User | null;
  shouldThrow?: boolean;
}> = [
  {
    name: 'valid user',
    input: { email: 'test@test.com', name: 'Test' },
    expected: { id: expect.any(String), email: 'test@test.com', name: 'Test' },
  },
  {
    name: 'missing email',
    input: { name: 'Test' } as any,
    expected: null,
    shouldThrow: true,
  },
];

test.each(testCases)('$name', async ({ input, expected, shouldThrow }) => {
  if (shouldThrow) {
    await expect(userService.create(input)).rejects.toThrow();
  } else {
    const result = await userService.create(input);
    expect(result).toMatchObject(expected!);
  }
});
```
