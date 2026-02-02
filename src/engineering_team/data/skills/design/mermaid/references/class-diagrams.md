# Mermaid Class Diagrams

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Class Members](#class-members)
- [Relationships](#relationships)
- [Annotations](#annotations)
- [Common Patterns](#common-patterns)

## Basic Syntax

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
    }
```

## Class Members

### Visibility

```mermaid
classDiagram
    class Example {
        +publicAttribute
        -privateAttribute
        #protectedAttribute
        ~packageAttribute
        +publicMethod()
        -privateMethod()
    }
```

| Symbol | Visibility |
|--------|------------|
| `+` | Public |
| `-` | Private |
| `#` | Protected |
| `~` | Package/Internal |

### Methods with Parameters

```mermaid
classDiagram
    class UserService {
        +findById(id: string) User
        +create(dto: CreateUserDto) User
        +update(id: string, dto: UpdateUserDto) User
        +delete(id: string) boolean
    }
```

### Static and Abstract

```mermaid
classDiagram
    class Utils {
        +getInstance()$ Utils
        +parse(input: string)$ Result
    }

    class AbstractHandler {
        <<abstract>>
        +handle(request)* Response
        #validate(request) boolean
    }
```

## Relationships

### Relationship Types

```mermaid
classDiagram
    A <|-- B : Inheritance
    C *-- D : Composition
    E o-- F : Aggregation
    G --> H : Association
    I -- J : Link
    K ..> L : Dependency
    M ..|> N : Realization
```

| Syntax | Type | Meaning |
|--------|------|---------|
| `<\|--` | Inheritance | B extends A |
| `*--` | Composition | D is part of C (lifecycle bound) |
| `o--` | Aggregation | F belongs to E (independent lifecycle) |
| `-->` | Association | G uses H |
| `--` | Link | Simple association |
| `..>` | Dependency | I depends on J |
| `..\|>` | Realization | K implements L |

### Cardinality

```mermaid
classDiagram
    Customer "1" --> "*" Order : places
    Order "1" --> "1..*" OrderItem : contains
    Product "1" --> "0..*" OrderItem : appears in
```

## Annotations

```mermaid
classDiagram
    class UserRepository {
        <<interface>>
        +findById(id) User
        +save(user) void
    }

    class AbstractEntity {
        <<abstract>>
        #id: string
        #createdAt: Date
    }

    class UserService {
        <<service>>
        -repository: UserRepository
        +createUser(dto) User
    }

    class PaymentType {
        <<enumeration>>
        CREDIT_CARD
        DEBIT_CARD
        BANK_TRANSFER
    }
```

Common annotations:
- `<<interface>>`
- `<<abstract>>`
- `<<service>>`
- `<<enumeration>>`
- `<<entity>>`
- `<<repository>>`

## Common Patterns

### Repository Pattern

```mermaid
classDiagram
    class Repository~T~ {
        <<interface>>
        +findById(id: string) T
        +findAll() List~T~
        +save(entity: T) T
        +delete(id: string) void
    }

    class UserRepository {
        <<interface>>
        +findByEmail(email: string) User
    }

    class UserRepositoryImpl {
        -db: Database
        +findById(id: string) User
        +findByEmail(email: string) User
        +save(user: User) User
    }

    Repository <|-- UserRepository
    UserRepository <|.. UserRepositoryImpl
```

### Domain Model

```mermaid
classDiagram
    class Entity~ID~ {
        <<abstract>>
        #id: ID
        +equals(other: Entity) boolean
    }

    class AggregateRoot~ID~ {
        <<abstract>>
        -domainEvents: List~DomainEvent~
        +addEvent(event: DomainEvent) void
        +clearEvents() List~DomainEvent~
    }

    class ValueObject {
        <<abstract>>
        +equals(other: ValueObject) boolean
    }

    class Order {
        -id: OrderId
        -customerId: CustomerId
        -items: List~OrderItem~
        -status: OrderStatus
        +addItem(item: OrderItem) void
        +submit() void
        +cancel() void
    }

    class OrderItem {
        -productId: ProductId
        -quantity: Quantity
        -price: Money
    }

    class Money {
        -amount: Decimal
        -currency: Currency
        +add(other: Money) Money
    }

    Entity <|-- AggregateRoot
    AggregateRoot <|-- Order
    ValueObject <|-- OrderItem
    ValueObject <|-- Money
    Order *-- OrderItem
    OrderItem *-- Money
```

### Service Layer

```mermaid
classDiagram
    class UserController {
        -userService: UserService
        +createUser(req: Request) Response
        +getUser(req: Request) Response
    }

    class UserService {
        -userRepo: UserRepository
        -emailService: EmailService
        +createUser(dto: CreateUserDto) User
        +getUserById(id: string) User
    }

    class UserRepository {
        <<interface>>
        +findById(id: string) User
        +save(user: User) User
    }

    class EmailService {
        <<interface>>
        +sendWelcome(email: string) void
    }

    UserController --> UserService
    UserService --> UserRepository
    UserService --> EmailService
```

### State Pattern

```mermaid
classDiagram
    class Order {
        -state: OrderState
        +submit() void
        +pay() void
        +ship() void
        +cancel() void
    }

    class OrderState {
        <<interface>>
        +submit(order: Order) void
        +pay(order: Order) void
        +ship(order: Order) void
        +cancel(order: Order) void
    }

    class DraftState {
        +submit(order: Order) void
    }

    class PendingState {
        +pay(order: Order) void
        +cancel(order: Order) void
    }

    class PaidState {
        +ship(order: Order) void
    }

    class ShippedState
    class CancelledState

    Order --> OrderState
    OrderState <|.. DraftState
    OrderState <|.. PendingState
    OrderState <|.. PaidState
    OrderState <|.. ShippedState
    OrderState <|.. CancelledState
```
