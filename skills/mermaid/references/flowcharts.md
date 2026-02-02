# Mermaid Flowcharts

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Node Shapes](#node-shapes)
- [Links and Arrows](#links-and-arrows)
- [Subgraphs](#subgraphs)
- [Styling](#styling)
- [Architecture Patterns](#architecture-patterns)

## Basic Syntax

### Direction

```mermaid
graph TD
    A --> B
```

| Direction | Meaning |
|-----------|---------|
| `TD` / `TB` | Top to Down / Top to Bottom |
| `BT` | Bottom to Top |
| `LR` | Left to Right |
| `RL` | Right to Left |

### Node Declaration

```mermaid
graph LR
    id1[Text in box]
    id2(Text in rounded box)
    id3
```

Nodes without text use their ID as the label.

## Node Shapes

```mermaid
graph TD
    A[Rectangle - Default]
    B(Rounded Rectangle)
    C([Stadium Shape])
    D[[Subroutine]]
    E[(Database/Cylinder)]
    F((Circle))
    G{Diamond/Decision}
    H{{Hexagon}}
    I[/Parallelogram/]
    J[\Parallelogram Alt\]
    K[/Trapezoid\]
    L[\Trapezoid Alt/]
```

### When to Use Each Shape

| Shape | Use Case |
|-------|----------|
| Rectangle `[text]` | Process, action, service |
| Rounded `(text)` | Start/end, user action |
| Stadium `([text])` | Terminal, entry point |
| Subroutine `[[text]]` | Predefined process, external call |
| Database `[(text)]` | Data store, database, cache |
| Circle `((text))` | Connector, junction |
| Diamond `{text}` | Decision, condition |
| Hexagon `{{text}}` | Preparation, setup |

## Links and Arrows

### Arrow Types

```mermaid
graph LR
    A --> B
    C --- D
    E -.-> F
    G ==> H
    I --o J
    K --x L
    M o--o N
    O <--> P
```

| Syntax | Description |
|--------|-------------|
| `-->` | Arrow |
| `---` | Line without arrow |
| `-.->` | Dotted arrow |
| `-.-` | Dotted line |
| `==>` | Thick arrow |
| `===` | Thick line |
| `--o` | Circle end |
| `--x` | Cross end |
| `o--o` | Circle both ends |
| `<-->` | Arrow both ends |

### Labels on Links

```mermaid
graph LR
    A -- text --> B
    C -- "longer text" --> D
    E -->|inline text| F
    G -.->|dotted with text| H
```

### Link Length

```mermaid
graph LR
    A --> B
    C ---> D
    E ----> F
```

More dashes = longer link (works for all arrow types).

## Subgraphs

### Basic Subgraph

```mermaid
graph TB
    subgraph one
        A[A] --> B[B]
    end

    subgraph two
        C[C] --> D[D]
    end

    B --> C
```

### Nested Subgraphs

```mermaid
graph TB
    subgraph Cloud
        subgraph Region A
            A1[Service 1]
            A2[Service 2]
        end
        subgraph Region B
            B1[Service 1]
            B2[Service 2]
        end
    end

    A1 --> B1
    A2 --> B2
```

### Subgraph Direction

```mermaid
graph LR
    subgraph TOP
        direction TB
        A --> B
    end

    subgraph BOTTOM
        direction TB
        C --> D
    end

    TOP --> BOTTOM
```

## Styling

### Inline Styles

```mermaid
graph LR
    A[Start]:::green --> B[Process]:::blue --> C[End]:::red

    classDef green fill:#9f6,stroke:#333,stroke-width:2px
    classDef blue fill:#69f,stroke:#333,stroke-width:2px
    classDef red fill:#f66,stroke:#333,stroke-width:2px
```

### Style Definitions

```mermaid
graph LR
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px
    classDef primary fill:#326CE5,stroke:#fff,color:#fff
    classDef secondary fill:#6c757d,stroke:#fff,color:#fff
    classDef success fill:#28a745,stroke:#fff,color:#fff
    classDef warning fill:#ffc107,stroke:#333,color:#333
    classDef danger fill:#dc3545,stroke:#fff,color:#fff

    A[Default]:::default
    B[Primary]:::primary
    C[Secondary]:::secondary
    D[Success]:::success
    E[Warning]:::warning
    F[Danger]:::danger
```

### Link Styles

```mermaid
graph LR
    A --> B --> C

    linkStyle 0 stroke:#f00,stroke-width:2px
    linkStyle 1 stroke:#0f0,stroke-width:2px,stroke-dasharray:5
```

## Architecture Patterns

### Three-Tier Architecture

```mermaid
graph TB
    subgraph Presentation
        Web[Web App]
        Mobile[Mobile App]
        API[Public API]
    end

    subgraph Application
        Gateway[API Gateway]
        Auth[Auth Service]
        BL[Business Logic]
    end

    subgraph Data
        Primary[(Primary DB)]
        Replica[(Read Replica)]
        Cache[(Cache)]
    end

    Web --> Gateway
    Mobile --> Gateway
    API --> Gateway
    Gateway --> Auth
    Gateway --> BL
    BL --> Primary
    BL --> Replica
    BL --> Cache
    Primary --> Replica
```

### Event-Driven Architecture

```mermaid
graph LR
    subgraph Producers
        S1[Service A]
        S2[Service B]
    end

    subgraph Messaging
        Q[Message Queue]
        T1[Topic 1]
        T2[Topic 2]
    end

    subgraph Consumers
        C1[Consumer 1]
        C2[Consumer 2]
        C3[Consumer 3]
    end

    S1 --> T1
    S2 --> T2
    T1 --> Q
    T2 --> Q
    Q --> C1
    Q --> C2
    Q --> C3
```

### CI/CD Pipeline

```mermaid
graph LR
    A[Code Push] --> B[Build]
    B --> C{Tests Pass?}
    C -->|Yes| D[Deploy Staging]
    C -->|No| E[Notify Dev]
    D --> F{QA Approved?}
    F -->|Yes| G[Deploy Prod]
    F -->|No| E
    G --> H[Monitor]
```

### Decision Flow

```mermaid
graph TD
    Start([Start]) --> Input[/User Input/]
    Input --> Validate{Valid?}
    Validate -->|No| Error[Show Error]
    Error --> Input
    Validate -->|Yes| Auth{Authenticated?}
    Auth -->|No| Login[Login Page]
    Login --> Auth
    Auth -->|Yes| Authorize{Authorized?}
    Authorize -->|No| Deny[Access Denied]
    Authorize -->|Yes| Process[Process Request]
    Process --> End([End])
    Deny --> End
```
