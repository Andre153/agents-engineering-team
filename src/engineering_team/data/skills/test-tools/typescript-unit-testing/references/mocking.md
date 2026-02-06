# Mocking Patterns

## Table of Contents
- [Mock Functions](#mock-functions)
- [Module Mocking](#module-mocking)
- [Class Mocking](#class-mocking)
- [Dependency Injection](#dependency-injection)
- [Timer Mocks](#timer-mocks)
- [Spies](#spies)
- [Partial Mocks](#partial-mocks)

## Mock Functions

### Creating Mocks

```typescript
// Jest
const mockFn = jest.fn();
const mockFnTyped = jest.fn<ReturnType, [Arg1, Arg2]>();

// Vitest
const mockFn = vi.fn();
const mockFnTyped = vi.fn<[Arg1, Arg2], ReturnType>();
```

### Return Values

```typescript
const mock = jest.fn();

// Static return
mock.mockReturnValue(42);
mock.mockReturnValueOnce(1).mockReturnValueOnce(2);

// Resolved promise
mock.mockResolvedValue({ data: 'result' });
mock.mockResolvedValueOnce({ data: 'first' });

// Rejected promise
mock.mockRejectedValue(new Error('failed'));
mock.mockRejectedValueOnce(new Error('first fail'));
```

### Implementation

```typescript
const mock = jest.fn();

// Custom implementation
mock.mockImplementation((x: number) => x * 2);

// Once implementation
mock.mockImplementationOnce((x: number) => x * 3);

// Chained implementations
mock
  .mockImplementationOnce(() => 'first')
  .mockImplementationOnce(() => 'second')
  .mockImplementation(() => 'default');
```

### Assertions

```typescript
expect(mock).toHaveBeenCalled();
expect(mock).toHaveBeenCalledTimes(3);
expect(mock).toHaveBeenCalledWith(arg1, arg2);
expect(mock).toHaveBeenLastCalledWith(arg);
expect(mock).toHaveBeenNthCalledWith(2, arg);
expect(mock).toHaveReturnedWith(value);

// Access call history
mock.mock.calls;           // [[arg1, arg2], [arg3]]
mock.mock.results;         // [{ type: 'return', value: x }]
mock.mock.lastCall;        // [lastArg1, lastArg2]
```

## Module Mocking

### Full Module Mock

```typescript
// Jest
jest.mock('./user.repository', () => ({
  UserRepository: jest.fn().mockImplementation(() => ({
    findById: jest.fn(),
    save: jest.fn(),
  })),
}));

// Vitest
vi.mock('./user.repository', () => ({
  UserRepository: vi.fn().mockImplementation(() => ({
    findById: vi.fn(),
    save: vi.fn(),
  })),
}));

// Auto-mock (all exports become mock functions)
vi.mock('./user.repository');
```

### Partial Module Mock

```typescript
// Keep original, override specific exports
jest.mock('./utils', () => ({
  ...jest.requireActual('./utils'),
  formatDate: jest.fn().mockReturnValue('2024-01-01'),
}));

// Vitest
vi.mock('./utils', async () => ({
  ...(await vi.importActual('./utils')),
  formatDate: vi.fn().mockReturnValue('2024-01-01'),
}));
```

### Dynamic Mocks

```typescript
// Change mock per test
import { getUserById } from './user.repository';

jest.mock('./user.repository');
const mockedGetUserById = getUserById as jest.MockedFunction<typeof getUserById>;

describe('UserService', () => {
  beforeEach(() => {
    mockedGetUserById.mockReset();
  });

  it('should_return_user_when_found', async () => {
    mockedGetUserById.mockResolvedValue({ id: '1', name: 'Alice' });
    // test...
  });

  it('should_throw_when_not_found', async () => {
    mockedGetUserById.mockResolvedValue(null);
    // test...
  });
});
```

### External Module Mocks

```typescript
// Mock node_modules
jest.mock('axios');
import axios from 'axios';
const mockedAxios = axios as jest.Mocked<typeof axios>;

mockedAxios.get.mockResolvedValue({ data: { users: [] } });
```

## Class Mocking

### Mock Class Methods

```typescript
class UserService {
  constructor(private repo: UserRepository) {}

  async getUser(id: string): Promise<User> {
    return this.repo.findById(id);
  }
}

// Mock the dependency, not the class under test
const mockRepo = {
  findById: jest.fn(),
  save: jest.fn(),
};

const service = new UserService(mockRepo as UserRepository);
```

### Mock Static Methods

```typescript
class Analytics {
  static track(event: string): void { /* ... */ }
}

// Jest
const trackSpy = jest.spyOn(Analytics, 'track').mockImplementation();

// Vitest
const trackSpy = vi.spyOn(Analytics, 'track').mockImplementation();

// Assert
expect(Analytics.track).toHaveBeenCalledWith('user.created');
```

## Dependency Injection

### Constructor Injection Pattern

```typescript
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}

interface EmailService {
  send(to: string, template: string): Promise<void>;
}

class UserService {
  constructor(
    private readonly userRepo: UserRepository,
    private readonly email: EmailService,
  ) {}
}

// Test setup
function createUserService(overrides: {
  userRepo?: Partial<UserRepository>;
  email?: Partial<EmailService>;
} = {}) {
  const mockUserRepo: UserRepository = {
    findById: jest.fn(),
    save: jest.fn(),
    ...overrides.userRepo,
  };

  const mockEmail: EmailService = {
    send: jest.fn(),
    ...overrides.email,
  };

  return {
    service: new UserService(mockUserRepo, mockEmail),
    mocks: { userRepo: mockUserRepo, email: mockEmail },
  };
}

// Usage
test('should_send_welcome_email_when_user_created', async () => {
  const { service, mocks } = createUserService();
  mocks.userRepo.save.mockResolvedValue(undefined);

  await service.createUser({ email: 'test@test.com' });

  expect(mocks.email.send).toHaveBeenCalledWith(
    'test@test.com',
    'welcome'
  );
});
```

### Type-Safe Mock Factory

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
const mockRepo = createMock<UserRepository>();
mockRepo.findById.mockResolvedValue({ id: '1', name: 'Test' });
```

## Timer Mocks

### Basic Timer Control

```typescript
beforeEach(() => {
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
});

test('should_timeout_after_5_seconds', () => {
  const callback = jest.fn();

  setTimeout(callback, 5000);

  expect(callback).not.toHaveBeenCalled();

  jest.advanceTimersByTime(5000);

  expect(callback).toHaveBeenCalled();
});
```

### Run All Timers

```typescript
test('should_complete_all_timers', () => {
  const callback = jest.fn();

  setTimeout(callback, 1000);
  setTimeout(callback, 2000);
  setTimeout(callback, 3000);

  jest.runAllTimers();

  expect(callback).toHaveBeenCalledTimes(3);
});
```

### Pending Timers

```typescript
test('should_run_only_pending_timers', () => {
  const callback = jest.fn();

  setTimeout(() => {
    callback('first');
    setTimeout(() => callback('second'), 1000);
  }, 1000);

  jest.runOnlyPendingTimers();
  expect(callback).toHaveBeenCalledWith('first');
  expect(callback).not.toHaveBeenCalledWith('second');

  jest.runOnlyPendingTimers();
  expect(callback).toHaveBeenCalledWith('second');
});
```

### Mock Date

```typescript
// Jest
jest.useFakeTimers().setSystemTime(new Date('2024-01-15'));

// Vitest
vi.useFakeTimers();
vi.setSystemTime(new Date('2024-01-15'));

test('should_use_mocked_date', () => {
  expect(new Date().toISOString()).toBe('2024-01-15T00:00:00.000Z');
});
```

## Spies

### Spy on Methods

```typescript
const user = {
  getName() {
    return 'Alice';
  },
};

const spy = jest.spyOn(user, 'getName');

user.getName();

expect(spy).toHaveBeenCalled();
expect(spy).toHaveReturnedWith('Alice');
```

### Spy and Replace

```typescript
const spy = jest.spyOn(user, 'getName').mockReturnValue('Mocked');

expect(user.getName()).toBe('Mocked');

// Restore original
spy.mockRestore();
expect(user.getName()).toBe('Alice');
```

### Spy on Getters/Setters

```typescript
const obj = {
  get value() {
    return 42;
  },
  set value(v: number) {
    // setter
  },
};

jest.spyOn(obj, 'value', 'get').mockReturnValue(100);
jest.spyOn(obj, 'value', 'set');

expect(obj.value).toBe(100);
```

## Partial Mocks

### Mock Specific Methods

```typescript
class EmailService {
  async send(to: string, body: string): Promise<void> {
    await this.validate(to);
    await this.deliver(to, body);
  }

  private validate(email: string): void {
    if (!email.includes('@')) throw new Error('Invalid');
  }

  private async deliver(to: string, body: string): Promise<void> {
    // actual delivery
  }
}

test('should_call_validate_and_deliver', async () => {
  const service = new EmailService();

  // Mock private method via prototype
  const deliverSpy = jest.spyOn(service as any, 'deliver').mockResolvedValue(undefined);

  await service.send('test@test.com', 'Hello');

  expect(deliverSpy).toHaveBeenCalledWith('test@test.com', 'Hello');
});
```

### Fake Implementations

```typescript
class FakeEmailService implements EmailService {
  public sentEmails: Array<{ to: string; body: string }> = [];

  async send(to: string, body: string): Promise<void> {
    this.sentEmails.push({ to, body });
  }
}

test('should_send_email_on_signup', async () => {
  const fakeEmail = new FakeEmailService();
  const userService = new UserService(fakeEmail);

  await userService.signup('test@test.com');

  expect(fakeEmail.sentEmails).toEqual([
    { to: 'test@test.com', body: expect.stringContaining('Welcome') },
  ]);
});
```
