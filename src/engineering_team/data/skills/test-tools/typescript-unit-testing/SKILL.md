---
name: typescript-unit-testing
description: "TypeScript unit testing expertise with Jest and Vitest. Use when writing unit tests, setting up test infrastructure, implementing mocks, or testing async code. Emphasizes business-readable tests with BDD-style naming."
---

# TypeScript Unit Testing

## Quick Reference

| Task | Guide |
|------|-------|
| Jest setup, assertions, lifecycle hooks | See [jest-patterns.md](references/jest-patterns.md) |
| Vitest setup, Jest migration, features | See [vitest-patterns.md](references/vitest-patterns.md) |
| Module mocking, DI, spies, timer mocks | See [mocking.md](references/mocking.md) |
| Promises, events, streams, timeouts | See [async-testing.md](references/async-testing.md) |
| File naming, structure, shared fixtures | See [test-organization.md](references/test-organization.md) |
| Jest config template | See [assets/jest.config.ts](assets/jest.config.ts) |
| Vitest config template | See [assets/vitest.config.ts](assets/vitest.config.ts) |

## Core Philosophy

### Tests as Documentation

Tests should describe system behavior in business language. A non-technical stakeholder should understand what the system does by reading test names.

### Business-Readable Naming

Use the `should_<behavior>_when_<condition>` pattern:

```typescript
describe('OrderService', () => {
  describe('submitOrder', () => {
    it('should_apply_discount_when_customer_is_premium', async () => {
      // Arrange
      const customer = createCustomer({ tier: 'premium' });
      const order = createOrder({ customerId: customer.id, total: 100 });

      // Act
      const result = await orderService.submitOrder(order);

      // Assert
      expect(result.total).toBe(90); // 10% premium discount
    });

    it('should_reject_order_when_inventory_insufficient', async () => {
      // Arrange
      const order = createOrder({ quantity: 100 });
      mockInventory.getAvailable.mockResolvedValue(50);

      // Act & Assert
      await expect(orderService.submitOrder(order))
        .rejects.toThrow(InsufficientInventoryError);
    });

    it('should_send_confirmation_email_when_order_successful', async () => {
      // Arrange
      const order = createOrder();

      // Act
      await orderService.submitOrder(order);

      // Assert
      expect(mockEmailService.send).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'order-confirmation' })
      );
    });
  });
});
```

## AAA Pattern

Every test follows **Arrange-Act-Assert**:

```typescript
it('should_calculate_tax_when_region_is_california', () => {
  // Arrange - Set up test data and dependencies
  const order = createOrder({
    subtotal: 100,
    shippingAddress: { state: 'CA' }
  });

  // Act - Execute the behavior under test
  const result = taxService.calculateTax(order);

  // Assert - Verify the expected outcome
  expect(result.taxAmount).toBe(7.25);
  expect(result.taxRate).toBe(0.0725);
});
```

## Type-Safe Test Fixtures

### Factory Pattern

```typescript
// factories/order.factory.ts
interface OrderFactoryOptions {
  id?: string;
  customerId?: string;
  items?: OrderItem[];
  status?: OrderStatus;
  total?: number;
}

let orderCounter = 0;

export function createOrder(options: OrderFactoryOptions = {}): Order {
  orderCounter++;
  return {
    id: options.id ?? `order-${orderCounter}`,
    customerId: options.customerId ?? `customer-${orderCounter}`,
    items: options.items ?? [createOrderItem()],
    status: options.status ?? 'pending',
    total: options.total ?? 99.99,
    createdAt: new Date(),
  };
}

// Usage in tests
const order = createOrder({ status: 'shipped', total: 150 });
```

### Type-Safe Mocks

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
const mockRepo = createMock<OrderRepository>();
mockRepo.findById.mockResolvedValue(createOrder());
```

## Test Categories

| Type | Purpose | Speed | Isolation |
|------|---------|-------|-----------|
| Unit | Test single function/class in isolation | Fast (ms) | Complete - mock all dependencies |
| Integration | Test component interactions | Medium (100ms-1s) | Partial - use real DB, mock external |
| Contract | Verify API contracts | Medium | Test against contract spec |
| E2E | Test full user flows | Slow (seconds) | None - full system |

### When to Use Unit Tests

- Pure functions and business logic
- State machines and algorithms
- Data transformations
- Validation logic
- Error handling paths

### When to Use Integration Tests

- Database queries and transactions
- API endpoint behavior
- Message queue interactions
- Cache invalidation logic

## Mocking Philosophy

### Mock at Boundaries

Mock external systems, not internal collaborators:

```typescript
// Good - mock the external boundary
const mockPaymentGateway = createMock<PaymentGateway>();
mockPaymentGateway.charge.mockResolvedValue({ success: true });

// Avoid - mocking internal details
const mockInternalValidator = createMock<InternalValidator>(); // Too coupled
```

### Prefer Fakes Over Mocks

For complex dependencies, use fakes that implement the interface:

```typescript
class FakeUserRepository implements UserRepository {
  private users = new Map<string, User>();

  async findById(id: string): Promise<User | null> {
    return this.users.get(id) ?? null;
  }

  async save(user: User): Promise<void> {
    this.users.set(user.id, user);
  }

  // Test helper
  seed(users: User[]): void {
    users.forEach(u => this.users.set(u.id, u));
  }
}
```

## Common Assertions

```typescript
// Equality
expect(result).toBe(expected);           // Strict equality
expect(result).toEqual(expected);        // Deep equality
expect(result).toMatchObject(partial);   // Partial match

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeDefined();

// Numbers
expect(num).toBeGreaterThan(5);
expect(num).toBeCloseTo(0.3, 5);         // Floating point

// Arrays
expect(array).toContain(item);
expect(array).toHaveLength(3);
expect(array).toEqual(expect.arrayContaining([1, 2]));

// Objects
expect(obj).toHaveProperty('key', 'value');
expect(obj).toMatchObject({ partial: 'match' });

// Errors
expect(() => fn()).toThrow(ErrorType);
await expect(asyncFn()).rejects.toThrow('message');

// Mock calls
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith(arg1, arg2);
expect(mockFn).toHaveBeenCalledTimes(3);
```
