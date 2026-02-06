# Test Organization

## Table of Contents
- [File Naming](#file-naming)
- [Directory Structure](#directory-structure)
- [Describe Blocks](#describe-blocks)
- [Shared Fixtures](#shared-fixtures)
- [Test Utilities](#test-utilities)
- [Test Tags](#test-tags)

## File Naming

### Conventions

```
# Unit tests - colocated with source
src/
├── features/
│   └── orders/
│       ├── order.service.ts
│       ├── order.service.test.ts      # Unit tests
│       └── order.service.spec.ts      # Alternative naming
├── utils/
│   ├── validation.ts
│   └── validation.test.ts

# Integration tests - separate directory
tests/
├── integration/
│   ├── orders.integration.test.ts
│   └── users.integration.test.ts
└── e2e/
    └── checkout.e2e.test.ts
```

### Naming Patterns

| Pattern | Use Case |
|---------|----------|
| `*.test.ts` | Unit tests (Jest default) |
| `*.spec.ts` | Alternative for unit tests |
| `*.integration.test.ts` | Integration tests |
| `*.e2e.test.ts` | End-to-end tests |
| `*.contract.test.ts` | Contract tests |

### Test File Content

```typescript
// order.service.test.ts
import { OrderService } from './order.service';
import { createMock } from '@/test-utils';
import { createOrder } from '@/test-utils/factories';

describe('OrderService', () => {
  // Test setup and cases...
});
```

## Directory Structure

### Colocated Tests (Recommended)

```
src/
├── features/
│   ├── orders/
│   │   ├── __tests__/                    # Alternative: tests in subfolder
│   │   │   ├── order.service.test.ts
│   │   │   └── fixtures/
│   │   │       └── orders.json
│   │   ├── order.service.ts
│   │   ├── order.repository.ts
│   │   └── index.ts
│   └── users/
│       ├── user.service.ts
│       ├── user.service.test.ts          # Or colocated
│       └── index.ts
├── shared/
│   └── utils/
│       ├── validation.ts
│       └── validation.test.ts
└── test-utils/                           # Shared test utilities
    ├── index.ts
    ├── mocks.ts
    ├── factories/
    │   ├── index.ts
    │   ├── order.factory.ts
    │   └── user.factory.ts
    └── helpers/
        ├── async.ts
        └── assertions.ts
```

### Separate Test Directory

```
src/
└── features/
    └── orders/
        └── order.service.ts

tests/
├── unit/
│   └── features/
│       └── orders/
│           └── order.service.test.ts
├── integration/
│   └── orders.integration.test.ts
├── e2e/
│   └── checkout.e2e.test.ts
├── fixtures/
│   ├── orders.json
│   └── users.json
└── utils/
    └── test-helpers.ts
```

## Describe Blocks

### Behavioral Organization

```typescript
describe('OrderService', () => {
  describe('createOrder', () => {
    describe('when_customer_is_valid', () => {
      it('should_create_order_with_pending_status', async () => {});
      it('should_calculate_total_with_tax', async () => {});
      it('should_emit_order_created_event', async () => {});
    });

    describe('when_customer_is_premium', () => {
      it('should_apply_discount', async () => {});
      it('should_skip_fraud_check', async () => {});
    });

    describe('when_inventory_insufficient', () => {
      it('should_reject_with_InsufficientInventoryError', async () => {});
      it('should_not_charge_customer', async () => {});
    });

    describe('when_payment_fails', () => {
      it('should_rollback_inventory_reservation', async () => {});
      it('should_notify_customer', async () => {});
    });
  });

  describe('cancelOrder', () => {
    // Similar structure...
  });
});
```

### Context Pattern

```typescript
describe('OrderService', () => {
  let service: OrderService;
  let mocks: { repo: MockOf<OrderRepository>; email: MockOf<EmailService> };

  beforeEach(() => {
    mocks = {
      repo: createMock<OrderRepository>(),
      email: createMock<EmailService>(),
    };
    service = new OrderService(mocks.repo, mocks.email);
  });

  context('with valid order', () => {
    let order: Order;

    beforeEach(() => {
      order = createOrder({ status: 'pending' });
      mocks.repo.findById.mockResolvedValue(order);
    });

    it('should_process_order', async () => {
      await service.processOrder(order.id);
      expect(mocks.repo.save).toHaveBeenCalled();
    });
  });

  context('with cancelled order', () => {
    beforeEach(() => {
      mocks.repo.findById.mockResolvedValue(createOrder({ status: 'cancelled' }));
    });

    it('should_throw_OrderAlreadyCancelledError', async () => {
      await expect(service.processOrder('1')).rejects.toThrow(OrderAlreadyCancelledError);
    });
  });
});

// Helper to make 'context' available (Jest doesn't have it built-in)
const context = describe;
```

## Shared Fixtures

### Factory Functions

```typescript
// test-utils/factories/order.factory.ts
import { Order, OrderStatus } from '@/features/orders';

interface OrderFactoryOptions {
  id?: string;
  customerId?: string;
  status?: OrderStatus;
  items?: OrderItem[];
  total?: number;
}

let counter = 0;

export function createOrder(options: OrderFactoryOptions = {}): Order {
  counter++;
  return {
    id: options.id ?? `order-${counter}`,
    customerId: options.customerId ?? `customer-${counter}`,
    status: options.status ?? 'pending',
    items: options.items ?? [createOrderItem()],
    total: options.total ?? 99.99,
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-01-15'),
  };
}

export function createOrderItem(options: Partial<OrderItem> = {}): OrderItem {
  counter++;
  return {
    id: options.id ?? `item-${counter}`,
    productId: options.productId ?? `product-${counter}`,
    quantity: options.quantity ?? 1,
    price: options.price ?? 29.99,
  };
}

// Reset counter between test files
export function resetOrderFactory(): void {
  counter = 0;
}
```

### Builder Pattern

```typescript
// test-utils/factories/order.builder.ts
export class OrderBuilder {
  private order: Partial<Order> = {};

  withId(id: string): this {
    this.order.id = id;
    return this;
  }

  withCustomer(customerId: string): this {
    this.order.customerId = customerId;
    return this;
  }

  withStatus(status: OrderStatus): this {
    this.order.status = status;
    return this;
  }

  withItems(items: OrderItem[]): this {
    this.order.items = items;
    return this;
  }

  withTotal(total: number): this {
    this.order.total = total;
    return this;
  }

  asPending(): this {
    return this.withStatus('pending');
  }

  asShipped(): this {
    return this.withStatus('shipped');
  }

  asCancelled(): this {
    return this.withStatus('cancelled');
  }

  build(): Order {
    return {
      id: this.order.id ?? `order-${Date.now()}`,
      customerId: this.order.customerId ?? 'customer-1',
      status: this.order.status ?? 'pending',
      items: this.order.items ?? [],
      total: this.order.total ?? 0,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }
}

// Usage
const order = new OrderBuilder()
  .withCustomer('premium-customer')
  .asShipped()
  .withTotal(150)
  .build();
```

### JSON Fixtures

```typescript
// test-utils/fixtures/orders.ts
export const orderFixtures = {
  pendingOrder: {
    id: 'order-pending-1',
    customerId: 'customer-1',
    status: 'pending' as const,
    items: [{ productId: 'product-1', quantity: 2, price: 25 }],
    total: 50,
  },
  shippedOrder: {
    id: 'order-shipped-1',
    customerId: 'customer-2',
    status: 'shipped' as const,
    items: [{ productId: 'product-2', quantity: 1, price: 100 }],
    total: 100,
  },
} as const;

// Type-safe access
type OrderFixtureKey = keyof typeof orderFixtures;
```

## Test Utilities

### Mock Helpers

```typescript
// test-utils/mocks.ts
type MockOf<T> = {
  [K in keyof T]: T[K] extends (...args: infer A) => infer R
    ? jest.Mock<R, A>
    : T[K];
};

export function createMock<T extends object>(): MockOf<T> {
  return new Proxy({} as MockOf<T>, {
    get: (target, prop) => {
      if (!(prop in target)) {
        (target as any)[prop] = jest.fn();
      }
      return (target as any)[prop];
    },
  });
}
```

### Async Helpers

```typescript
// test-utils/helpers/async.ts
export async function waitFor<T>(
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
    await sleep(interval);
  }

  throw new Error(`Condition not met within ${timeout}ms`);
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function flushPromises(): Promise<void> {
  return new Promise(resolve => setImmediate(resolve));
}
```

### Custom Matchers

```typescript
// test-utils/matchers.ts
expect.extend({
  toBeWithinRange(received: number, floor: number, ceiling: number) {
    const pass = received >= floor && received <= ceiling;
    return {
      pass,
      message: () =>
        `expected ${received} ${pass ? 'not ' : ''}to be within ${floor}-${ceiling}`,
    };
  },

  toContainObject(received: unknown[], expected: object) {
    const pass = received.some(item =>
      Object.entries(expected).every(([key, value]) =>
        (item as any)[key] === value
      )
    );
    return {
      pass,
      message: () =>
        `expected array ${pass ? 'not ' : ''}to contain object matching ${JSON.stringify(expected)}`,
    };
  },
});

// Types
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeWithinRange(floor: number, ceiling: number): R;
      toContainObject(expected: object): R;
    }
  }
}
```

## Test Tags

### Using Comments for Filtering

```typescript
// @slow
test('should_process_large_dataset', async () => {
  // Long-running test
});

// @integration
test('should_connect_to_database', async () => {
  // Integration test
});
```

### Jest Projects for Test Types

```typescript
// jest.config.ts
const config: Config = {
  projects: [
    {
      displayName: 'unit',
      testMatch: ['<rootDir>/src/**/*.test.ts'],
      testPathIgnorePatterns: ['.integration.', '.e2e.'],
    },
    {
      displayName: 'integration',
      testMatch: ['<rootDir>/tests/integration/**/*.test.ts'],
      setupFilesAfterEnv: ['<rootDir>/tests/integration/setup.ts'],
    },
  ],
};
```

### Running by Tag

```bash
# Run only unit tests
jest --selectProjects=unit

# Run only integration tests
jest --selectProjects=integration

# Run tests matching pattern
jest --testNamePattern="should_create"
```
