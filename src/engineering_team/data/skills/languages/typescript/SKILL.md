---
name: typescript
description: "TypeScript development expertise for backend and full-stack applications. Use when writing TypeScript code, configuring TypeScript projects, implementing type-safe patterns, or reviewing TypeScript for best practices. Covers: type system patterns, async programming, error handling, testing, and project architecture."
---

# TypeScript Development

## Quick Reference

| Task | Guide |
|------|-------|
| Type patterns (utility types, branded types, discriminated unions) | See [type-patterns.md](references/type-patterns.md) |
| Async programming (promises, generators, error handling) | See [async-patterns.md](references/async-patterns.md) |
| Testing patterns (mocks, fixtures, type-safe testing) | See [testing.md](references/testing.md) |
| Project structure and architecture | See [architecture.md](references/architecture.md) |
| Strict tsconfig template | See [assets/tsconfig.strict.json](assets/tsconfig.strict.json) |

## Core Principles

### Strict Configuration

Always enable strict mode. Use the template in `assets/tsconfig.strict.json` as a starting point:

```bash
cp assets/tsconfig.strict.json tsconfig.json
```

Key settings that catch bugs:
- `strict: true` - Enables all strict checks
- `noUncheckedIndexedAccess: true` - Array/object access returns `T | undefined`
- `exactOptionalPropertyTypes: true` - Distinguishes `undefined` from missing

### Type Inference

Let TypeScript infer when obvious, be explicit at boundaries:

```typescript
// Let inference work for local variables
const users = [{ name: 'Alice', age: 30 }];
const names = users.map(u => u.name); // string[]

// Explicit types at function boundaries
function createUser(name: string, age: number): User {
  return { id: generateId(), name, age };
}

// Explicit types for exports and public APIs
export interface UserService {
  findById(id: UserId): Promise<User | null>;
}
```

### Prefer Interfaces for Objects

```typescript
// Use interface for object shapes
interface User {
  id: string;
  name: string;
  email: string;
}

// Use type for unions, primitives, tuples
type Status = 'active' | 'inactive' | 'pending';
type Coordinates = [number, number];
type StringOrNumber = string | number;
```

## Essential Patterns

### Result Type for Expected Failures

Avoid throwing errors for expected failures:

```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

function parseJson<T>(json: string): Result<T, SyntaxError> {
  try {
    return { success: true, data: JSON.parse(json) };
  } catch (error) {
    return { success: false, error: error as SyntaxError };
  }
}

// Usage - forces error handling
const result = parseJson<User>(jsonString);
if (result.success) {
  console.log(result.data.name);
} else {
  console.error('Parse failed:', result.error.message);
}
```

### Discriminated Unions for State

```typescript
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function handleState<T>(state: AsyncState<T>) {
  switch (state.status) {
    case 'idle': return 'Not started';
    case 'loading': return 'Loading...';
    case 'success': return state.data; // TypeScript knows data exists
    case 'error': return state.error.message;
  }
}
```

### Branded Types for Type-Safe IDs

```typescript
type Brand<T, B> = T & { readonly __brand: B };

type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;

function createUserId(id: string): UserId {
  return id as UserId;
}

// Prevents mixing up IDs
function getUser(id: UserId): User { /* ... */ }
function getOrder(id: OrderId): Order { /* ... */ }

const userId = createUserId('u123');
const orderId = createOrderId('o456');
getUser(userId);  // OK
getUser(orderId); // Type error
```

### Type Guards

```typescript
// Custom type guard
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'email' in value
  );
}

// Assertion function
function assertUser(value: unknown): asserts value is User {
  if (!isUser(value)) {
    throw new Error('Value is not a valid User');
  }
}

// Usage
if (isUser(data)) {
  console.log(data.email); // TypeScript knows it's User
}
```

## Common Utility Types

```typescript
// Make all properties optional
type UpdateDto = Partial<User>;

// Make all properties required
type Complete = Required<User>;

// Pick specific properties
type Credentials = Pick<User, 'email' | 'password'>;

// Exclude specific properties
type PublicUser = Omit<User, 'password' | 'salt'>;

// Create a dictionary type
type UserMap = Record<UserId, User>;

// Extract return type
type Response = ReturnType<typeof fetchUser>;

// Extract parameter types
type Params = Parameters<typeof fetchUser>;
```

## Code Style

### Naming Conventions
- `PascalCase`: Types, interfaces, classes, enums
- `camelCase`: Variables, functions, methods, properties
- `SCREAMING_SNAKE_CASE`: Constants
- `kebab-case`: File names

### Import Order
1. Node.js built-in modules (`node:fs`, `node:path`)
2. External dependencies
3. Internal modules (absolute paths with `@/`)
4. Relative imports
5. Type-only imports last

```typescript
import { readFile } from 'node:fs/promises';

import express from 'express';
import { z } from 'zod';

import { UserService } from '@/features/users';
import { logger } from '@/shared/logger';

import { validateRequest } from './middleware';

import type { Request, Response } from 'express';
```

### Const Assertions

```typescript
// Create literal types from arrays
const ROLES = ['admin', 'user', 'guest'] as const;
type Role = typeof ROLES[number]; // 'admin' | 'user' | 'guest'

// Preserve object literal types
const config = {
  apiUrl: 'https://api.example.com',
  timeout: 5000,
} as const;
// { readonly apiUrl: 'https://api.example.com'; readonly timeout: 5000 }
```

## Error Handling

### Custom Error Classes

```typescript
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500,
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id ${id} not found`, 'NOT_FOUND', 404);
  }
}

class ValidationError extends AppError {
  constructor(
    message: string,
    public readonly fields: Record<string, string[]>,
  ) {
    super(message, 'VALIDATION_ERROR', 400);
  }
}
```

## Module Patterns

### Barrel Exports

```typescript
// features/users/index.ts
export { UserService } from './user.service';
export { UserRepository } from './user.repository';
export type { User, CreateUserDto, UpdateUserDto } from './user.types';
```

### Dependency Injection

```typescript
interface UserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}

class UserService {
  constructor(
    private readonly userRepository: UserRepository,
    private readonly emailService: EmailService,
  ) {}

  async createUser(dto: CreateUserDto): Promise<User> {
    const user = User.create(dto);
    await this.userRepository.save(user);
    await this.emailService.sendWelcome(user.email);
    return user;
  }
}
```

## Async Best Practices

### Parallel Operations

```typescript
// Use Promise.all for concurrent independent operations
async function fetchUserData(userId: string) {
  const [user, orders, prefs] = await Promise.all([
    fetchUser(userId),
    fetchOrders(userId),
    fetchPreferences(userId),
  ]);
  return { user, orders, prefs };
}

// Use Promise.allSettled when some can fail
async function fetchMultiple(ids: string[]) {
  const results = await Promise.allSettled(ids.map(fetchUser));

  const users = results
    .filter((r): r is PromiseFulfilledResult<User> => r.status === 'fulfilled')
    .map(r => r.value);

  return users;
}
```

For more async patterns including generators and streams, see [async-patterns.md](references/async-patterns.md).
