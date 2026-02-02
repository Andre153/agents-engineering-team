# TypeScript Async Patterns

## Table of Contents
- [Promise Combinators](#promise-combinators)
- [Async Generators](#async-generators)
- [Error Handling](#error-handling)
- [Cancellation](#cancellation)
- [Rate Limiting](#rate-limiting)
- [Retry Patterns](#retry-patterns)
- [Streams](#streams)

## Promise Combinators

### Promise.all - Fail Fast

All promises must succeed, fails on first rejection:

```typescript
async function fetchUserData(userId: string) {
  const [user, orders, preferences] = await Promise.all([
    fetchUser(userId),
    fetchOrders(userId),
    fetchPreferences(userId),
  ]);
  return { user, orders, preferences };
}

// With type annotations
async function fetchMultipleResources(): Promise<[User, Order[], Settings]> {
  return Promise.all([
    fetchUser('123'),
    fetchOrders('123'),
    fetchSettings('123'),
  ]);
}
```

### Promise.allSettled - Always Resolves

Returns results for all promises, regardless of success/failure:

```typescript
async function fetchMultipleUsers(ids: string[]): Promise<{
  users: User[];
  errors: Error[];
}> {
  const results = await Promise.allSettled(ids.map(id => fetchUser(id)));

  const users = results
    .filter((r): r is PromiseFulfilledResult<User> => r.status === 'fulfilled')
    .map(r => r.value);

  const errors = results
    .filter((r): r is PromiseRejectedResult => r.status === 'rejected')
    .map(r => r.reason as Error);

  return { users, errors };
}

// Generic helper
function partitionResults<T>(
  results: PromiseSettledResult<T>[]
): { fulfilled: T[]; rejected: unknown[] } {
  const fulfilled: T[] = [];
  const rejected: unknown[] = [];

  for (const result of results) {
    if (result.status === 'fulfilled') {
      fulfilled.push(result.value);
    } else {
      rejected.push(result.reason);
    }
  }

  return { fulfilled, rejected };
}
```

### Promise.race - First to Complete

Returns the first promise to settle (resolve or reject):

```typescript
async function fetchWithTimeout<T>(
  promise: Promise<T>,
  timeoutMs: number
): Promise<T> {
  const timeout = new Promise<never>((_, reject) => {
    setTimeout(() => reject(new Error('Timeout')), timeoutMs);
  });

  return Promise.race([promise, timeout]);
}

// Usage
const user = await fetchWithTimeout(fetchUser('123'), 5000);
```

### Promise.any - First to Succeed

Returns the first promise to fulfill, ignores rejections:

```typescript
async function fetchFromMultipleSources<T>(
  sources: (() => Promise<T>)[]
): Promise<T> {
  return Promise.any(sources.map(fn => fn()));
}

// Fallback pattern
async function fetchWithFallback(userId: string): Promise<User> {
  return Promise.any([
    fetchFromPrimaryApi(userId),
    fetchFromSecondaryApi(userId),
    fetchFromCache(userId),
  ]);
}
```

## Async Generators

### Pagination

```typescript
async function* paginate<T>(
  fetchPage: (cursor?: string) => Promise<{ data: T[]; nextCursor?: string }>
): AsyncGenerator<T> {
  let cursor: string | undefined;

  do {
    const { data, nextCursor } = await fetchPage(cursor);
    for (const item of data) {
      yield item;
    }
    cursor = nextCursor;
  } while (cursor);
}

// Usage
async function processAllUsers() {
  for await (const user of paginate(fetchUsersPage)) {
    await processUser(user);
  }
}

// Collect all items
async function collectAll<T>(generator: AsyncGenerator<T>): Promise<T[]> {
  const items: T[] = [];
  for await (const item of generator) {
    items.push(item);
  }
  return items;
}
```

### Batching

```typescript
async function* batch<T>(
  items: AsyncIterable<T>,
  size: number
): AsyncGenerator<T[]> {
  let batch: T[] = [];

  for await (const item of items) {
    batch.push(item);
    if (batch.length >= size) {
      yield batch;
      batch = [];
    }
  }

  if (batch.length > 0) {
    yield batch;
  }
}

// Usage
for await (const userBatch of batch(paginate(fetchUsersPage), 100)) {
  await bulkUpdateUsers(userBatch);
}
```

### Concurrent Processing with Limit

```typescript
async function* mapConcurrent<T, R>(
  items: AsyncIterable<T>,
  fn: (item: T) => Promise<R>,
  concurrency: number
): AsyncGenerator<R> {
  const pending = new Set<Promise<R>>();
  const results: R[] = [];

  for await (const item of items) {
    const promise = fn(item).then(result => {
      pending.delete(promise);
      return result;
    });
    pending.add(promise);

    if (pending.size >= concurrency) {
      const result = await Promise.race(pending);
      yield result;
    }
  }

  // Drain remaining
  while (pending.size > 0) {
    const result = await Promise.race(pending);
    yield result;
  }
}
```

## Error Handling

### Result Type Pattern

```typescript
type Result<T, E = Error> =
  | { success: true; data: T }
  | { success: false; error: E };

// Async result wrapper
async function tryCatch<T, E = Error>(
  promise: Promise<T>
): Promise<Result<T, E>> {
  try {
    const data = await promise;
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error as E };
  }
}

// Usage
const result = await tryCatch(fetchUser('123'));
if (result.success) {
  console.log(result.data);
} else {
  console.error(result.error.message);
}

// Chain results
function mapResult<T, U, E>(
  result: Result<T, E>,
  fn: (data: T) => U
): Result<U, E> {
  if (result.success) {
    return { success: true, data: fn(result.data) };
  }
  return result;
}

async function flatMapResult<T, U, E>(
  result: Result<T, E>,
  fn: (data: T) => Promise<Result<U, E>>
): Promise<Result<U, E>> {
  if (result.success) {
    return fn(result.data);
  }
  return result;
}
```

### Error Aggregation

```typescript
class AggregateError extends Error {
  constructor(
    public readonly errors: Error[],
    message?: string
  ) {
    super(message ?? `${errors.length} errors occurred`);
    this.name = 'AggregateError';
  }
}

async function executeAll<T>(
  tasks: (() => Promise<T>)[]
): Promise<{ results: T[]; errors: Error[] }> {
  const settled = await Promise.allSettled(tasks.map(fn => fn()));

  const results: T[] = [];
  const errors: Error[] = [];

  for (const result of settled) {
    if (result.status === 'fulfilled') {
      results.push(result.value);
    } else {
      errors.push(result.reason as Error);
    }
  }

  return { results, errors };
}
```

## Cancellation

### AbortController Pattern

```typescript
async function fetchWithAbort<T>(
  url: string,
  signal?: AbortSignal
): Promise<T> {
  const response = await fetch(url, { signal });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

// Usage with timeout
async function fetchWithTimeout<T>(url: string, timeoutMs: number): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetchWithAbort<T>(url, controller.signal);
  } finally {
    clearTimeout(timeoutId);
  }
}

// Cancellable async generator
async function* fetchAllPages<T>(
  fetchPage: (page: number, signal: AbortSignal) => Promise<T[]>,
  signal: AbortSignal
): AsyncGenerator<T> {
  let page = 1;

  while (!signal.aborted) {
    const items = await fetchPage(page, signal);
    if (items.length === 0) break;

    for (const item of items) {
      yield item;
    }
    page++;
  }
}
```

### Cancellation Token

```typescript
class CancellationToken {
  private cancelled = false;
  private callbacks: (() => void)[] = [];

  get isCancelled(): boolean {
    return this.cancelled;
  }

  cancel(): void {
    if (this.cancelled) return;
    this.cancelled = true;
    this.callbacks.forEach(cb => cb());
  }

  onCancel(callback: () => void): void {
    if (this.cancelled) {
      callback();
    } else {
      this.callbacks.push(callback);
    }
  }

  throwIfCancelled(): void {
    if (this.cancelled) {
      throw new Error('Operation cancelled');
    }
  }
}

async function longRunningTask(token: CancellationToken): Promise<void> {
  for (let i = 0; i < 100; i++) {
    token.throwIfCancelled();
    await processChunk(i);
  }
}
```

## Rate Limiting

### Token Bucket

```typescript
class RateLimiter {
  private tokens: number;
  private lastRefill: number;

  constructor(
    private readonly maxTokens: number,
    private readonly refillRate: number, // tokens per second
  ) {
    this.tokens = maxTokens;
    this.lastRefill = Date.now();
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.maxTokens, this.tokens + elapsed * this.refillRate);
    this.lastRefill = now;
  }

  async acquire(): Promise<void> {
    this.refill();

    if (this.tokens < 1) {
      const waitTime = ((1 - this.tokens) / this.refillRate) * 1000;
      await new Promise(resolve => setTimeout(resolve, waitTime));
      this.refill();
    }

    this.tokens -= 1;
  }
}

// Usage
const limiter = new RateLimiter(10, 2); // 10 tokens, 2/sec refill

async function rateLimitedFetch<T>(url: string): Promise<T> {
  await limiter.acquire();
  return fetch(url).then(r => r.json());
}
```

### Throttle and Debounce

```typescript
function throttle<T extends (...args: any[]) => any>(
  fn: T,
  waitMs: number
): T {
  let lastCall = 0;

  return ((...args: Parameters<T>) => {
    const now = Date.now();
    if (now - lastCall >= waitMs) {
      lastCall = now;
      return fn(...args);
    }
  }) as T;
}

function debounce<T extends (...args: any[]) => any>(
  fn: T,
  waitMs: number
): T {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;

  return ((...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), waitMs);
  }) as T;
}

// Async debounce with result
function debounceAsync<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  waitMs: number
): (...args: Parameters<T>) => Promise<Awaited<ReturnType<T>>> {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  let pendingPromise: Promise<Awaited<ReturnType<T>>> | undefined;

  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);

    pendingPromise = new Promise((resolve, reject) => {
      timeoutId = setTimeout(async () => {
        try {
          const result = await fn(...args);
          resolve(result);
        } catch (error) {
          reject(error);
        }
      }, waitMs);
    });

    return pendingPromise;
  };
}
```

## Retry Patterns

### Exponential Backoff

```typescript
interface RetryOptions {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
  shouldRetry?: (error: unknown) => boolean;
}

async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions
): Promise<T> {
  const { maxRetries, baseDelayMs, maxDelayMs, shouldRetry = () => true } = options;

  let lastError: unknown;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      if (attempt === maxRetries || !shouldRetry(error)) {
        throw error;
      }

      const delay = Math.min(
        baseDelayMs * Math.pow(2, attempt) + Math.random() * 100,
        maxDelayMs
      );

      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
}

// Usage
const user = await withRetry(
  () => fetchUser('123'),
  {
    maxRetries: 3,
    baseDelayMs: 1000,
    maxDelayMs: 10000,
    shouldRetry: (error) => {
      if (error instanceof Error && error.message.includes('rate limit')) {
        return true;
      }
      return false;
    },
  }
);
```

## Streams

### Transform Stream

```typescript
async function* transformStream<T, U>(
  input: AsyncIterable<T>,
  transform: (item: T) => U | Promise<U>
): AsyncGenerator<U> {
  for await (const item of input) {
    yield await transform(item);
  }
}

// Filter stream
async function* filterStream<T>(
  input: AsyncIterable<T>,
  predicate: (item: T) => boolean | Promise<boolean>
): AsyncGenerator<T> {
  for await (const item of input) {
    if (await predicate(item)) {
      yield item;
    }
  }
}

// Take while
async function* takeWhile<T>(
  input: AsyncIterable<T>,
  predicate: (item: T) => boolean
): AsyncGenerator<T> {
  for await (const item of input) {
    if (!predicate(item)) break;
    yield item;
  }
}

// Pipeline composition
async function pipeline<T>(source: AsyncIterable<T>) {
  return {
    map: <U>(fn: (item: T) => U | Promise<U>) =>
      pipeline(transformStream(source, fn)),
    filter: (fn: (item: T) => boolean | Promise<boolean>) =>
      pipeline(filterStream(source, fn)),
    take: (n: number) =>
      pipeline(takeWhile(source, (_, i = { count: 0 }) => ++i.count <= n)),
    collect: () => collectAll(source),
    forEach: async (fn: (item: T) => void | Promise<void>) => {
      for await (const item of source) {
        await fn(item);
      }
    },
  };
}
```
