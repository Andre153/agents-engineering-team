---
name: mermaid
description: "Mermaid diagramming for architecture documentation, system design, and technical planning. Use when creating flowcharts, sequence diagrams, entity-relationship diagrams, class diagrams, or any visual documentation in Markdown."
---

# Mermaid Diagramming

## Quick Reference

| Diagram Type | Use Case | Reference |
|--------------|----------|-----------|
| Flowchart | System architecture, data flow, decision trees | See [flowcharts.md](references/flowcharts.md) |
| Sequence | API interactions, request flows, protocols | See [sequence.md](references/sequence.md) |
| Entity Relationship | Database schemas, data models | See [entity-relationship.md](references/entity-relationship.md) |
| Class | Object models, domain models, interfaces | See [class-diagrams.md](references/class-diagrams.md) |
| State | State machines, workflows, lifecycles | See [state-diagrams.md](references/state-diagrams.md) |

## Core Syntax

All Mermaid diagrams start with a diagram type declaration:

```mermaid
graph TD
    A[Start] --> B[End]
```

### Diagram Types

| Declaration | Type |
|-------------|------|
| `graph TD` / `graph LR` | Flowchart (top-down / left-right) |
| `sequenceDiagram` | Sequence diagram |
| `erDiagram` | Entity-relationship |
| `classDiagram` | Class diagram |
| `stateDiagram-v2` | State diagram |
| `flowchart TD` | Enhanced flowchart |

## Flowchart Essentials

### Direction
- `TD` / `TB` - Top to bottom
- `LR` - Left to right
- `RL` - Right to left
- `BT` - Bottom to top

### Node Shapes
```mermaid
graph LR
    A[Rectangle] --> B(Rounded)
    B --> C([Stadium])
    C --> D[[Subroutine]]
    D --> E[(Database)]
    E --> F((Circle))
    F --> G{Diamond}
    G --> H{{Hexagon}}
```

### Connections
```
A --> B       Solid arrow
A --- B       Solid line
A -.-> B      Dotted arrow
A -.- B       Dotted line
A ==> B       Thick arrow
A === B       Thick line
A --text--> B Labeled arrow
```

### Subgraphs
```mermaid
graph TB
    subgraph Frontend
        A[React App]
        B[Mobile App]
    end

    subgraph Backend
        C[API Gateway]
        D[Auth Service]
        E[Core Service]
    end

    subgraph Data
        F[(PostgreSQL)]
        G[(Redis)]
    end

    A --> C
    B --> C
    C --> D
    C --> E
    E --> F
    E --> G
```

## Sequence Diagram Essentials

```mermaid
sequenceDiagram
    participant C as Client
    participant A as API
    participant D as Database

    C->>A: POST /users
    activate A
    A->>D: INSERT user
    D-->>A: user_id
    A-->>C: 201 Created
    deactivate A
```

### Message Types
```
->>   Solid arrow (sync request)
-->>  Dashed arrow (response)
-)    Open arrow (async)
--)   Dashed open arrow (async response)
-x    Cross (failed)
--x   Dashed cross (failed response)
```

### Control Flow
```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    alt is authenticated
        C->>S: Request data
        S-->>C: Data response
    else not authenticated
        C->>S: Request data
        S-->>C: 401 Unauthorized
    end

    opt cache available
        S-->>C: Cached data
    end

    loop every minute
        S->>S: Health check
    end
```

## Entity Relationship Essentials

```mermaid
erDiagram
    User ||--o{ Order : places
    Order ||--|{ OrderItem : contains
    OrderItem }o--|| Product : references
    Product }o--o{ Category : "belongs to"
```

### Relationship Types
```
||--||   One to one
||--o{   One to many
}o--o{   Many to many
||--|{   One to one or more
}o--||   Many to one
```

### Attributes
```mermaid
erDiagram
    User {
        string id PK
        string email UK
        string name
        datetime created_at
    }

    Order {
        string id PK
        string user_id FK
        decimal total
        string status
    }

    User ||--o{ Order : places
```

## Best Practices

### Clarity
- Keep diagrams focused on one concept
- Use meaningful node labels
- Group related items in subgraphs
- Use consistent naming conventions

### Layout
- Choose direction based on reading flow (LR for processes, TD for hierarchies)
- Use subgraphs to organize complex diagrams
- Limit crossing lines where possible

### Styling
```mermaid
graph LR
    A[Normal]:::default --> B[Highlighted]:::highlight
    B --> C[Warning]:::warning

    classDef default fill:#f9f9f9,stroke:#333
    classDef highlight fill:#bbf,stroke:#33f
    classDef warning fill:#fbb,stroke:#f33
```

## Common Patterns

### Microservices Architecture
```mermaid
graph TB
    subgraph Clients
        Web[Web App]
        Mobile[Mobile App]
    end

    subgraph Gateway
        AG[API Gateway]
        Auth[Auth]
    end

    subgraph Services
        US[User Service]
        OS[Order Service]
        PS[Product Service]
    end

    subgraph Data
        UDB[(Users DB)]
        ODB[(Orders DB)]
        PDB[(Products DB)]
        Cache[(Redis)]
    end

    subgraph Messaging
        MQ[Message Queue]
    end

    Web --> AG
    Mobile --> AG
    AG --> Auth
    AG --> US
    AG --> OS
    AG --> PS
    US --> UDB
    OS --> ODB
    PS --> PDB
    US --> Cache
    OS --> MQ
    PS --> MQ
```

### Request Flow
```mermaid
sequenceDiagram
    participant C as Client
    participant G as Gateway
    participant A as Auth
    participant S as Service
    participant D as Database
    participant Q as Queue

    C->>G: Request + Token
    G->>A: Validate token
    A-->>G: Valid
    G->>S: Authorized request
    S->>D: Query data
    D-->>S: Result
    S->>Q: Emit event
    S-->>G: Response
    G-->>C: Response
```

For detailed syntax and advanced patterns, see the reference files.
