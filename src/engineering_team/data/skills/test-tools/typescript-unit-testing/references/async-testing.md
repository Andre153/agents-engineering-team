# Async Testing Patterns

## Table of Contents
- [Testing Promises](#testing-promises)
- [Testing Events](#testing-events)
- [Testing Streams](#testing-streams)
- [Testing Timeouts](#testing-timeouts)
- [Testing Retries](#testing-retries)
- [Race Conditions](#race-conditions)

## Testing Promises

### Basic Async Tests

```typescript
// Return the promise
test('should_fetch_user', () => {
  return userService.getUser('1').then(user => {
    expect(user.name).toBe('Alice');
  });
});

// Async/await (preferred)
test('should_fetch_user', async () => {
  const user = await userService.getUser('1');
  expect(user.name).toBe('Alice');
});

// .resolves matcher
test('should_fetch_user', () => {
  return expect(userService.getUser('1')).resolves.toMatchObject({
    name: 'Alice',
  });
});
```

### Testing Rejections

```typescript
// Async/await with try-catch
test('should_throw_when_not_found', async () => {
  await expect(userService.getUser('999')).rejects.toThrow('Not found');
});

// Check error type
test('should_throw_NotFoundError', async () => {
  await expect(userService.getUser('999')).rejects.toBeInstanceOf(NotFoundError);
});

// Check error properties
test('should_throw_with_code', async () => {
  await expect(userService.getUser('999')).rejects.toMatchObject({
    code: 'USER_NOT_FOUND',
    message: expect.stringContaining('999'),
  });
});
```

### Promise.all Testing

```typescript
test('should_fetch_all_users_concurrently', async () => {
  const ids = ['1', '2', '3'];

  const users = await Promise.all(
    ids.map(id => userService.getUser(id))
  );

  expect(users).toHaveLength(3);
  expect(users.map(u => u.id)).toEqual(['1', '2', '3']);
});
```

### Promise.allSettled Testing

```typescript
test('should_handle_partial_failures', async () => {
  mockRepo.findById
    .mockResolvedValueOnce({ id: '1', name: 'Alice' })
    .mockRejectedValueOnce(new Error('Not found'))
    .mockResolvedValueOnce({ id: '3', name: 'Charlie' });

  const results = await Promise.allSettled([
    userService.getUser('1'),
    userService.getUser('2'),
    userService.getUser('3'),
  ]);

  expect(results[0]).toMatchObject({ status: 'fulfilled', value: { id: '1' } });
  expect(results[1]).toMatchObject({ status: 'rejected' });
  expect(results[2]).toMatchObject({ status: 'fulfilled', value: { id: '3' } });
});
```

## Testing Events

### EventEmitter Testing

```typescript
import { EventEmitter } from 'events';

function waitForEvent<T>(
  emitter: EventEmitter,
  event: string,
  timeout = 5000
): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(new Error(`Event '${event}' not emitted within ${timeout}ms`));
    }, timeout);

    emitter.once(event, (data: T) => {
      clearTimeout(timer);
      resolve(data);
    });
  });
}

test('should_emit_complete_when_done', async () => {
  const processor = new DataProcessor();
  const resultPromise = waitForEvent<ProcessResult>(processor, 'complete');

  processor.start();

  const result = await resultPromise;
  expect(result.status).toBe('success');
});
```

### Multiple Events

```typescript
function collectEvents<T>(
  emitter: EventEmitter,
  event: string,
  count: number,
  timeout = 5000
): Promise<T[]> {
  return new Promise((resolve, reject) => {
    const events: T[] = [];
    const timer = setTimeout(() => {
      reject(new Error(`Only received ${events.length}/${count} events`));
    }, timeout);

    const handler = (data: T) => {
      events.push(data);
      if (events.length === count) {
        clearTimeout(timer);
        emitter.off(event, handler);
        resolve(events);
      }
    };

    emitter.on(event, handler);
  });
}

test('should_emit_progress_events', async () => {
  const processor = new DataProcessor();
  const progressPromise = collectEvents<number>(processor, 'progress', 3);

  processor.process([1, 2, 3]);

  const progress = await progressPromise;
  expect(progress).toEqual([33, 66, 100]);
});
```

### Event Spy

```typescript
test('should_emit_events_in_order', async () => {
  const processor = new DataProcessor();
  const events: string[] = [];

  processor.on('start', () => events.push('start'));
  processor.on('progress', () => events.push('progress'));
  processor.on('complete', () => events.push('complete'));

  await processor.process([1, 2, 3]);

  expect(events).toEqual(['start', 'progress', 'progress', 'progress', 'complete']);
});
```

## Testing Streams

### Readable Streams

```typescript
async function collectStream<T>(stream: AsyncIterable<T>): Promise<T[]> {
  const items: T[] = [];
  for await (const item of stream) {
    items.push(item);
  }
  return items;
}

test('should_stream_all_records', async () => {
  const stream = dataService.streamRecords();
  const records = await collectStream(stream);

  expect(records).toHaveLength(100);
});
```

### Transform Streams

```typescript
test('should_transform_data', async () => {
  const input = [
    { id: 1, value: 'a' },
    { id: 2, value: 'b' },
  ];

  const transform = new UppercaseTransform();
  const results: any[] = [];

  for (const item of input) {
    transform.write(item);
  }
  transform.end();

  for await (const chunk of transform) {
    results.push(chunk);
  }

  expect(results).toEqual([
    { id: 1, value: 'A' },
    { id: 2, value: 'B' },
  ]);
});
```

### Node.js Stream Testing

```typescript
import { Readable, Writable } from 'stream';
import { pipeline } from 'stream/promises';

test('should_process_stream_pipeline', async () => {
  const input = Readable.from(['hello', 'world']);
  const chunks: string[] = [];

  const output = new Writable({
    write(chunk, encoding, callback) {
      chunks.push(chunk.toString());
      callback();
    },
  });

  await pipeline(input, transformer, output);

  expect(chunks).toEqual(['HELLO', 'WORLD']);
});
```

## Testing Timeouts

### Fake Timers with Async

```typescript
test('should_timeout_after_delay', async () => {
  jest.useFakeTimers();

  const callback = jest.fn();
  const promise = delayedOperation(callback, 5000);

  // Fast-forward time
  jest.advanceTimersByTime(5000);

  // Wait for promises to resolve
  await promise;

  expect(callback).toHaveBeenCalled();

  jest.useRealTimers();
});
```

### Testing Debounce

```typescript
test('should_debounce_calls', () => {
  jest.useFakeTimers();

  const callback = jest.fn();
  const debounced = debounce(callback, 300);

  debounced('a');
  debounced('b');
  debounced('c');

  expect(callback).not.toHaveBeenCalled();

  jest.advanceTimersByTime(300);

  expect(callback).toHaveBeenCalledTimes(1);
  expect(callback).toHaveBeenCalledWith('c');

  jest.useRealTimers();
});
```

### Testing Throttle

```typescript
test('should_throttle_calls', () => {
  jest.useFakeTimers();

  const callback = jest.fn();
  const throttled = throttle(callback, 100);

  throttled('a');  // Executes immediately
  throttled('b');  // Ignored
  throttled('c');  // Ignored

  expect(callback).toHaveBeenCalledTimes(1);

  jest.advanceTimersByTime(100);
  throttled('d');  // Executes

  expect(callback).toHaveBeenCalledTimes(2);
  expect(callback).toHaveBeenLastCalledWith('d');

  jest.useRealTimers();
});
```

## Testing Retries

### Retry Logic

```typescript
test('should_retry_on_failure', async () => {
  const operation = jest.fn()
    .mockRejectedValueOnce(new Error('Fail 1'))
    .mockRejectedValueOnce(new Error('Fail 2'))
    .mockResolvedValueOnce({ success: true });

  const result = await retry(operation, { maxAttempts: 3, delay: 100 });

  expect(operation).toHaveBeenCalledTimes(3);
  expect(result).toEqual({ success: true });
});

test('should_fail_after_max_retries', async () => {
  const operation = jest.fn().mockRejectedValue(new Error('Always fails'));

  await expect(
    retry(operation, { maxAttempts: 3, delay: 100 })
  ).rejects.toThrow('Always fails');

  expect(operation).toHaveBeenCalledTimes(3);
});
```

### Exponential Backoff

```typescript
test('should_use_exponential_backoff', async () => {
  jest.useFakeTimers();

  const operation = jest.fn()
    .mockRejectedValueOnce(new Error('Fail'))
    .mockRejectedValueOnce(new Error('Fail'))
    .mockResolvedValueOnce({ success: true });

  const promise = retryWithBackoff(operation, {
    maxAttempts: 3,
    baseDelay: 100,
  });

  // First call immediate
  expect(operation).toHaveBeenCalledTimes(1);

  // Second call after 100ms
  await jest.advanceTimersByTimeAsync(100);
  expect(operation).toHaveBeenCalledTimes(2);

  // Third call after 200ms (exponential)
  await jest.advanceTimersByTimeAsync(200);
  expect(operation).toHaveBeenCalledTimes(3);

  const result = await promise;
  expect(result).toEqual({ success: true });

  jest.useRealTimers();
});
```

## Race Conditions

### Testing Concurrent Access

```typescript
test('should_handle_concurrent_updates', async () => {
  const counter = new AtomicCounter();

  // Simulate concurrent increments
  await Promise.all([
    counter.increment(),
    counter.increment(),
    counter.increment(),
  ]);

  expect(counter.value).toBe(3);
});
```

### Testing Lock Mechanisms

```typescript
test('should_prevent_double_processing', async () => {
  const processor = new ExclusiveProcessor();
  const results: string[] = [];

  const process1 = processor.process('a').then(() => results.push('a'));
  const process2 = processor.process('b').then(() => results.push('b'));

  await Promise.all([process1, process2]);

  // Should process sequentially, not concurrently
  expect(results).toEqual(['a', 'b']);
});
```

### Wait For Condition

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

  throw new Error(`Condition not met within ${timeout}ms`);
}

test('should_eventually_be_ready', async () => {
  const service = new AsyncService();
  service.initialize();

  await waitFor(() => service.isReady);

  expect(service.status).toBe('ready');
});
```

### Flush Promises

```typescript
// Helper to flush all pending promises
function flushPromises(): Promise<void> {
  return new Promise(resolve => setImmediate(resolve));
}

test('should_process_all_microtasks', async () => {
  const results: number[] = [];

  Promise.resolve().then(() => results.push(1));
  Promise.resolve().then(() => results.push(2));

  expect(results).toEqual([]);

  await flushPromises();

  expect(results).toEqual([1, 2]);
});
```
