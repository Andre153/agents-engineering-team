# TypeScript Project Architecture

## Table of Contents
- [Project Structure](#project-structure)
- [Module Patterns](#module-patterns)
- [Dependency Injection](#dependency-injection)
- [Configuration Management](#configuration-management)
- [Path Aliases](#path-aliases)

## Project Structure

### Feature-Based (Vertical Slice)

Organize by feature/domain rather than technical layer:

```
src/
├── features/
│   ├── users/
│   │   ├── index.ts              # Barrel export
│   │   ├── user.types.ts         # Types and interfaces
│   │   ├── user.service.ts       # Business logic
│   │   ├── user.repository.ts    # Data access
│   │   ├── user.controller.ts    # HTTP handlers
│   │   ├── user.routes.ts        # Route definitions
│   │   ├── user.validation.ts    # Input validation
│   │   └── __tests__/
│   │       ├── user.service.test.ts
│   │       └── user.repository.test.ts
│   ├── orders/
│   │   └── ... (same structure)
│   └── products/
│       └── ... (same structure)
├── shared/
│   ├── database/
│   │   ├── client.ts
│   │   └── migrations/
│   ├── middleware/
│   │   ├── auth.ts
│   │   ├── error-handler.ts
│   │   └── validation.ts
│   ├── utils/
│   │   ├── date.ts
│   │   └── string.ts
│   └── types/
│       ├── common.ts
│       └── http.ts
├── config/
│   ├── index.ts
│   ├── database.ts
│   └── app.ts
├── app.ts                        # Application setup
└── main.ts                       # Entry point
```

### DDD with CQRS

For complex domains with command/query separation:

```
src/
├── modules/
│   └── orders/
│       ├── domain/
│       │   ├── order.entity.ts
│       │   ├── order-item.value-object.ts
│       │   ├── order.aggregate.ts
│       │   ├── order.events.ts
│       │   └── order.repository.ts      # Interface only
│       ├── application/
│       │   ├── commands/
│       │   │   ├── create-order.command.ts
│       │   │   └── create-order.handler.ts
│       │   ├── queries/
│       │   │   ├── get-order.query.ts
│       │   │   └── get-order.handler.ts
│       │   └── services/
│       │       └── order-pricing.service.ts
│       ├── infrastructure/
│       │   ├── order.repository.impl.ts  # Implementation
│       │   ├── order.mapper.ts
│       │   └── order.schema.ts
│       ├── presentation/
│       │   ├── order.controller.ts
│       │   └── order.dto.ts
│       └── index.ts
├── shared-kernel/
│   ├── domain/
│   │   ├── entity.base.ts
│   │   ├── value-object.base.ts
│   │   ├── aggregate-root.base.ts
│   │   └── domain-event.base.ts
│   └── infrastructure/
│       ├── event-bus.ts
│       └── unit-of-work.ts
└── main.ts
```

## Module Patterns

### Barrel Exports

```typescript
// features/users/index.ts
// Export public API only

// Types
export type { User, CreateUserDto, UpdateUserDto } from './user.types';

// Services
export { UserService } from './user.service';

// Repository interface (not implementation)
export type { UserRepository } from './user.repository';

// Controller for route setup
export { UserController } from './user.controller';
export { userRoutes } from './user.routes';
```

### Internal vs External Modules

```typescript
// features/users/internal/password-hasher.ts
// Not exported from index.ts - internal implementation detail

export function hashPassword(password: string): Promise<string> {
  // ...
}

// features/users/user.service.ts
// Uses internal module
import { hashPassword } from './internal/password-hasher';

export class UserService {
  async createUser(dto: CreateUserDto): Promise<User> {
    const hashedPassword = await hashPassword(dto.password);
    // ...
  }
}
```

### Circular Dependency Prevention

```typescript
// BAD: Circular dependency
// user.service.ts imports order.service.ts
// order.service.ts imports user.service.ts

// GOOD: Use events or interfaces

// shared/events/user-created.event.ts
export interface UserCreatedEvent {
  userId: string;
  email: string;
}

// features/users/user.service.ts
export class UserService {
  constructor(private eventBus: EventBus) {}

  async createUser(dto: CreateUserDto): Promise<User> {
    const user = await this.repository.save(dto);
    this.eventBus.publish<UserCreatedEvent>('user.created', {
      userId: user.id,
      email: user.email,
    });
    return user;
  }
}

// features/orders/order.service.ts
export class OrderService {
  constructor(eventBus: EventBus) {
    eventBus.subscribe<UserCreatedEvent>('user.created', this.onUserCreated);
  }

  private onUserCreated = async (event: UserCreatedEvent) => {
    // Handle user creation
  };
}
```

## Dependency Injection

### Manual DI Container

```typescript
// container.ts
interface Container {
  userRepository: UserRepository;
  orderRepository: OrderRepository;
  emailService: EmailService;
  userService: UserService;
  orderService: OrderService;
}

export function createContainer(config: Config): Container {
  // Infrastructure
  const db = createDatabaseClient(config.database);

  // Repositories
  const userRepository = new UserRepositoryImpl(db);
  const orderRepository = new OrderRepositoryImpl(db);

  // External services
  const emailService = new EmailServiceImpl(config.email);

  // Application services
  const userService = new UserService({
    userRepository,
    emailService,
  });

  const orderService = new OrderService({
    orderRepository,
    userRepository,
  });

  return {
    userRepository,
    orderRepository,
    emailService,
    userService,
    orderService,
  };
}

// main.ts
const container = createContainer(config);
const app = createApp(container);
```

### Factory Pattern

```typescript
// factories/user-service.factory.ts
export function createUserService(deps: {
  db: Database;
  emailConfig: EmailConfig;
}): UserService {
  const userRepository = new UserRepositoryImpl(deps.db);
  const emailService = new EmailServiceImpl(deps.emailConfig);

  return new UserService({ userRepository, emailService });
}
```

### Interface-Based DI

```typescript
// Define interfaces for all dependencies
interface UserServiceDeps {
  userRepository: UserRepository;
  emailService: EmailService;
  logger: Logger;
}

class UserService {
  constructor(private readonly deps: UserServiceDeps) {}

  async createUser(dto: CreateUserDto): Promise<User> {
    this.deps.logger.info('Creating user', { email: dto.email });
    const user = await this.deps.userRepository.save(dto);
    await this.deps.emailService.sendWelcome(user.email);
    return user;
  }
}

// Easy to test with mocks
const mockDeps: UserServiceDeps = {
  userRepository: createMock<UserRepository>(),
  emailService: createMock<EmailService>(),
  logger: createMock<Logger>(),
};

const service = new UserService(mockDeps);
```

## Configuration Management

### Type-Safe Config

```typescript
// config/schema.ts
import { z } from 'zod';

const configSchema = z.object({
  nodeEnv: z.enum(['development', 'test', 'production']),
  port: z.number().min(1).max(65535),
  database: z.object({
    host: z.string(),
    port: z.number(),
    name: z.string(),
    user: z.string(),
    password: z.string(),
    ssl: z.boolean().default(false),
  }),
  redis: z.object({
    url: z.string().url(),
    ttl: z.number().default(3600),
  }),
  jwt: z.object({
    secret: z.string().min(32),
    expiresIn: z.string().default('1h'),
  }),
  email: z.object({
    from: z.string().email(),
    apiKey: z.string(),
  }),
});

export type Config = z.infer<typeof configSchema>;

// config/index.ts
export function loadConfig(): Config {
  const config = {
    nodeEnv: process.env.NODE_ENV ?? 'development',
    port: parseInt(process.env.PORT ?? '3000', 10),
    database: {
      host: process.env.DB_HOST ?? 'localhost',
      port: parseInt(process.env.DB_PORT ?? '5432', 10),
      name: process.env.DB_NAME ?? 'app',
      user: process.env.DB_USER ?? 'postgres',
      password: process.env.DB_PASSWORD ?? '',
      ssl: process.env.DB_SSL === 'true',
    },
    redis: {
      url: process.env.REDIS_URL ?? 'redis://localhost:6379',
      ttl: parseInt(process.env.REDIS_TTL ?? '3600', 10),
    },
    jwt: {
      secret: process.env.JWT_SECRET ?? '',
      expiresIn: process.env.JWT_EXPIRES_IN ?? '1h',
    },
    email: {
      from: process.env.EMAIL_FROM ?? '',
      apiKey: process.env.EMAIL_API_KEY ?? '',
    },
  };

  return configSchema.parse(config);
}
```

### Environment-Specific Config

```typescript
// config/environments/development.ts
export const developmentConfig = {
  logLevel: 'debug',
  database: {
    logging: true,
    synchronize: true,
  },
};

// config/environments/production.ts
export const productionConfig = {
  logLevel: 'warn',
  database: {
    logging: false,
    synchronize: false,
  },
};

// config/index.ts
import { developmentConfig } from './environments/development';
import { productionConfig } from './environments/production';

export function getEnvironmentConfig() {
  switch (process.env.NODE_ENV) {
    case 'production':
      return productionConfig;
    case 'development':
    default:
      return developmentConfig;
  }
}
```

## Path Aliases

### tsconfig.json

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@features/*": ["src/features/*"],
      "@shared/*": ["src/shared/*"],
      "@config/*": ["src/config/*"],
      "@test/*": ["test/*"]
    }
  }
}
```

### Usage

```typescript
// Instead of relative paths
import { UserService } from '../../../features/users';
import { logger } from '../../shared/utils/logger';

// Use aliases
import { UserService } from '@features/users';
import { logger } from '@shared/utils/logger';
import { createTestUser } from '@test/fixtures/users';
```

### Runtime Resolution

For Node.js, use `tsconfig-paths` or configure module resolution:

```json
// package.json
{
  "scripts": {
    "start": "node -r tsconfig-paths/register dist/main.js",
    "dev": "ts-node -r tsconfig-paths/register src/main.ts"
  }
}
```

Or use `tsc-alias` to resolve paths at build time:

```json
{
  "scripts": {
    "build": "tsc && tsc-alias"
  }
}
```
