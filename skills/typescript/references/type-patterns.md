# TypeScript Type Patterns

## Table of Contents
- [Utility Types](#utility-types)
- [Branded Types](#branded-types)
- [Discriminated Unions](#discriminated-unions)
- [Template Literal Types](#template-literal-types)
- [Conditional Types](#conditional-types)
- [Mapped Types](#mapped-types)
- [Type Guards](#type-guards)
- [Variance](#variance)

## Utility Types

### Built-in Utility Types

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  password: string;
  createdAt: Date;
}

// Partial<T> - All properties optional
type UpdateUserDto = Partial<User>;
// { id?: string; name?: string; ... }

// Required<T> - All properties required
type CompleteUser = Required<Partial<User>>;

// Readonly<T> - All properties readonly
type ImmutableUser = Readonly<User>;

// Pick<T, K> - Select properties
type UserCredentials = Pick<User, 'email' | 'password'>;
// { email: string; password: string }

// Omit<T, K> - Exclude properties
type PublicUser = Omit<User, 'password'>;
// { id: string; name: string; email: string; createdAt: Date }

// Record<K, V> - Dictionary type
type UserRoles = Record<string, 'admin' | 'user' | 'guest'>;

// Exclude<T, U> - Remove types from union
type NonNullableStatus = Exclude<Status | null | undefined, null | undefined>;

// Extract<T, U> - Keep matching types from union
type StringStatus = Extract<Status | number, string>;

// NonNullable<T> - Remove null and undefined
type DefiniteUser = NonNullable<User | null | undefined>;

// ReturnType<T> - Extract function return type
type ApiResponse = ReturnType<typeof fetchUser>;

// Parameters<T> - Extract function parameters as tuple
type FetchParams = Parameters<typeof fetchUser>;
// [userId: string, options?: FetchOptions]

// Awaited<T> - Unwrap Promise type
type ResolvedUser = Awaited<Promise<User>>;
// User

// ConstructorParameters<T> - Extract constructor params
type UserParams = ConstructorParameters<typeof UserClass>;
```

### Custom Utility Types

```typescript
// DeepPartial - Recursive partial
type DeepPartial<T> = T extends object
  ? { [P in keyof T]?: DeepPartial<T[P]> }
  : T;

// DeepReadonly - Recursive readonly
type DeepReadonly<T> = T extends object
  ? { readonly [P in keyof T]: DeepReadonly<T[P]> }
  : T;

// Mutable - Remove readonly
type Mutable<T> = { -readonly [P in keyof T]: T[P] };

// RequiredKeys - Get required property keys
type RequiredKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? never : K;
}[keyof T];

// OptionalKeys - Get optional property keys
type OptionalKeys<T> = {
  [K in keyof T]-?: {} extends Pick<T, K> ? K : never;
}[keyof T];

// PickByType - Pick properties by value type
type PickByType<T, U> = {
  [P in keyof T as T[P] extends U ? P : never]: T[P];
};

// Example: Pick all string properties
type StringProps = PickByType<User, string>;
// { id: string; name: string; email: string; password: string }
```

## Branded Types

Branded types create distinct types from primitives to prevent mixing them up:

```typescript
// Brand utility type
type Brand<T, B> = T & { readonly __brand: B };

// Define branded types
type UserId = Brand<string, 'UserId'>;
type OrderId = Brand<string, 'OrderId'>;
type Email = Brand<string, 'Email'>;
type PositiveNumber = Brand<number, 'PositiveNumber'>;

// Constructor functions with validation
function createUserId(id: string): UserId {
  if (!id.startsWith('usr_')) {
    throw new Error('Invalid user ID format');
  }
  return id as UserId;
}

function createEmail(value: string): Email {
  if (!value.includes('@')) {
    throw new Error('Invalid email format');
  }
  return value as Email;
}

function createPositiveNumber(n: number): PositiveNumber {
  if (n <= 0) {
    throw new Error('Number must be positive');
  }
  return n as PositiveNumber;
}

// Type-safe functions that can't be called with wrong ID type
function getUser(id: UserId): Promise<User> { /* ... */ }
function getOrder(id: OrderId): Promise<Order> { /* ... */ }
function sendEmail(to: Email, subject: string): void { /* ... */ }

// Usage
const userId = createUserId('usr_123');
const orderId = createOrderId('ord_456');

getUser(userId);  // OK
getUser(orderId); // Type error: OrderId is not assignable to UserId
```

### Opaque Types Alternative

```typescript
// Using unique symbol for truly opaque types
declare const userIdSymbol: unique symbol;
type UserId = string & { readonly [userIdSymbol]: never };

// This provides even stronger type safety as the brand
// cannot be accidentally created
```

## Discriminated Unions

Use a common literal property to discriminate between variants:

```typescript
// State machine pattern
type RequestState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T; timestamp: Date }
  | { status: 'error'; error: Error; retryCount: number };

function handleRequest<T>(state: RequestState<T>): string {
  switch (state.status) {
    case 'idle':
      return 'Ready to fetch';
    case 'loading':
      return 'Loading...';
    case 'success':
      // TypeScript knows data and timestamp exist
      return `Loaded ${state.data} at ${state.timestamp}`;
    case 'error':
      // TypeScript knows error and retryCount exist
      return `Error: ${state.error.message} (retry ${state.retryCount})`;
  }
}

// Event pattern
type AppEvent =
  | { type: 'USER_LOGIN'; userId: string; timestamp: Date }
  | { type: 'USER_LOGOUT'; userId: string }
  | { type: 'PAGE_VIEW'; path: string; referrer?: string }
  | { type: 'ERROR'; error: Error; context: Record<string, unknown> };

function logEvent(event: AppEvent): void {
  switch (event.type) {
    case 'USER_LOGIN':
      console.log(`User ${event.userId} logged in at ${event.timestamp}`);
      break;
    case 'USER_LOGOUT':
      console.log(`User ${event.userId} logged out`);
      break;
    case 'PAGE_VIEW':
      console.log(`Page view: ${event.path}`);
      break;
    case 'ERROR':
      console.error(`Error: ${event.error.message}`, event.context);
      break;
  }
}

// Exhaustiveness checking
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${x}`);
}

function handleEventStrict(event: AppEvent): void {
  switch (event.type) {
    case 'USER_LOGIN': /* ... */ break;
    case 'USER_LOGOUT': /* ... */ break;
    case 'PAGE_VIEW': /* ... */ break;
    case 'ERROR': /* ... */ break;
    default:
      assertNever(event); // Compile error if a case is missing
  }
}
```

## Template Literal Types

Create type-safe string patterns:

```typescript
// HTTP methods
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

// API versions
type ApiVersion = 'v1' | 'v2' | 'v3';

// Route pattern
type Route = `/${ApiVersion}/${string}`;
type FullRoute = `${HttpMethod} ${Route}`;

const route: FullRoute = 'GET /v1/users'; // OK
const bad: FullRoute = 'FETCH /v1/users'; // Error

// Event names
type EventName<T extends string> = `on${Capitalize<T>}`;
type ClickEvent = EventName<'click'>; // 'onClick'

// CSS units
type CSSUnit = 'px' | 'em' | 'rem' | '%' | 'vh' | 'vw';
type CSSValue = `${number}${CSSUnit}`;

const width: CSSValue = '100px'; // OK
const height: CSSValue = '50vh'; // OK

// Environment variables
type EnvVar = `${Uppercase<string>}_${Uppercase<string>}`;
const dbHost: EnvVar = 'DATABASE_HOST'; // OK

// Parsing template literals
type ExtractRouteParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ExtractRouteParams<Rest>
    : T extends `${string}:${infer Param}`
    ? Param
    : never;

type Params = ExtractRouteParams<'/users/:userId/posts/:postId'>;
// 'userId' | 'postId'
```

## Conditional Types

```typescript
// Basic conditional
type IsString<T> = T extends string ? true : false;

type A = IsString<string>; // true
type B = IsString<number>; // false

// Infer keyword - extract types
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type UnwrapArray<T> = T extends (infer U)[] ? U : T;

type X = UnwrapPromise<Promise<string>>; // string
type Y = UnwrapArray<number[]>; // number

// Extract function return type manually
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

// Distributive conditional types
type ToArray<T> = T extends any ? T[] : never;

type Distributed = ToArray<string | number>;
// string[] | number[] (not (string | number)[])

// Prevent distribution with tuple
type ToArrayNonDistributive<T> = [T] extends [any] ? T[] : never;
type NonDistributed = ToArrayNonDistributive<string | number>;
// (string | number)[]

// Filter union types
type FilterString<T> = T extends string ? T : never;
type OnlyStrings = FilterString<string | number | boolean>;
// string
```

## Mapped Types

```typescript
// Basic mapped type
type Readonly<T> = { readonly [P in keyof T]: T[P] };
type Optional<T> = { [P in keyof T]?: T[P] };

// Key remapping with 'as'
type Getters<T> = {
  [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P];
};

interface Person {
  name: string;
  age: number;
}

type PersonGetters = Getters<Person>;
// { getName: () => string; getAge: () => number }

// Filter keys
type FilteredKeys<T, U> = {
  [P in keyof T as T[P] extends U ? P : never]: T[P];
};

type StringPropsOnly = FilteredKeys<Person, string>;
// { name: string }

// Combine with template literals
type EventHandlers<T> = {
  [P in keyof T as `on${Capitalize<string & P>}Change`]: (value: T[P]) => void;
};

type PersonHandlers = EventHandlers<Person>;
// { onNameChange: (value: string) => void; onAgeChange: (value: number) => void }
```

## Type Guards

### User-Defined Type Guards

```typescript
// Type predicate
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

// Object type guard
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'email' in value &&
    typeof (value as User).id === 'string' &&
    typeof (value as User).email === 'string'
  );
}

// Discriminated union guard
function isSuccessState<T>(
  state: RequestState<T>
): state is { status: 'success'; data: T; timestamp: Date } {
  return state.status === 'success';
}

// Assertion function
function assertDefined<T>(
  value: T | null | undefined,
  message?: string
): asserts value is T {
  if (value === null || value === undefined) {
    throw new Error(message ?? 'Value is not defined');
  }
}

// Usage
function processUser(data: unknown) {
  if (isUser(data)) {
    // data is User here
    console.log(data.email);
  }
}

function processValue(value: string | null) {
  assertDefined(value, 'Value must be defined');
  // value is string here (not null)
  console.log(value.toUpperCase());
}
```

### Narrowing with `in` Operator

```typescript
type Admin = { role: 'admin'; permissions: string[] };
type Guest = { role: 'guest'; expiresAt: Date };
type User = Admin | Guest;

function handleUser(user: User) {
  if ('permissions' in user) {
    // TypeScript knows this is Admin
    console.log(user.permissions);
  } else {
    // TypeScript knows this is Guest
    console.log(user.expiresAt);
  }
}
```

## Variance

Understanding variance helps with generic type relationships:

```typescript
// Covariance (output positions) - use 'out'
interface Producer<out T> {
  produce(): T;
}

// Contravariance (input positions) - use 'in'
interface Consumer<in T> {
  consume(value: T): void;
}

// Invariance (both positions)
interface Handler<T> {
  get(): T;
  set(value: T): void;
}

// Practical example
class Animal {}
class Dog extends Animal {}

type AnimalProducer = Producer<Animal>;
type DogProducer = Producer<Dog>;

// DogProducer is assignable to AnimalProducer (covariant)
const dogProducer: DogProducer = { produce: () => new Dog() };
const animalProducer: AnimalProducer = dogProducer; // OK

type AnimalConsumer = Consumer<Animal>;
type DogConsumer = Consumer<Dog>;

// AnimalConsumer is assignable to DogConsumer (contravariant)
const animalConsumer: AnimalConsumer = { consume: (a) => {} };
const dogConsumer: DogConsumer = animalConsumer; // OK
```
