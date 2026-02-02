# Mermaid Entity-Relationship Diagrams

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Relationships](#relationships)
- [Attributes](#attributes)
- [Keys and Constraints](#keys-and-constraints)
- [Common Patterns](#common-patterns)

## Basic Syntax

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    PRODUCT ||--o{ LINE-ITEM : "ordered in"
```

## Relationships

### Cardinality Notation

```
||    Exactly one
|o    Zero or one
}|    One or more
}o    Zero or more
```

### Relationship Types

```mermaid
erDiagram
    A ||--|| B : "one to one"
    C ||--o{ D : "one to many"
    E }o--o{ F : "many to many"
    G ||--|{ H : "one to one or more"
    I }o--|| J : "many to one"
    K |o--o| L : "zero or one to zero or one"
```

### Relationship Labels

```mermaid
erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ COMMENT : writes
    POST ||--o{ COMMENT : has
    USER }o--o{ USER : follows
```

## Attributes

### Basic Attributes

```mermaid
erDiagram
    USER {
        string id
        string email
        string name
        datetime created_at
    }
```

### Data Types

Common attribute types:
- `string` - Text data
- `int` / `integer` - Whole numbers
- `float` / `decimal` - Decimal numbers
- `boolean` / `bool` - True/false
- `datetime` / `timestamp` - Date and time
- `date` - Date only
- `uuid` - UUID identifiers
- `json` / `jsonb` - JSON data
- `text` - Long text
- `blob` - Binary data

### Full Example with Types

```mermaid
erDiagram
    USER {
        uuid id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    PROFILE {
        uuid id PK
        uuid user_id FK
        string avatar_url
        text bio
        json preferences
    }

    USER ||--|| PROFILE : has
```

## Keys and Constraints

### Key Types

```mermaid
erDiagram
    ENTITY {
        type attribute_name PK "Primary Key"
        type attribute_name FK "Foreign Key"
        type attribute_name UK "Unique Key"
    }
```

### Composite Keys

```mermaid
erDiagram
    ORDER_ITEM {
        uuid order_id PK,FK
        uuid product_id PK,FK
        int quantity
        decimal unit_price
    }

    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : "included in"
```

## Common Patterns

### User Authentication System

```mermaid
erDiagram
    USER {
        uuid id PK
        string email UK
        string password_hash
        boolean email_verified
        datetime created_at
        datetime last_login
    }

    SESSION {
        uuid id PK
        uuid user_id FK
        string token UK
        string ip_address
        string user_agent
        datetime expires_at
        datetime created_at
    }

    PASSWORD_RESET {
        uuid id PK
        uuid user_id FK
        string token UK
        datetime expires_at
        boolean used
    }

    ROLE {
        uuid id PK
        string name UK
        string description
    }

    USER_ROLE {
        uuid user_id PK,FK
        uuid role_id PK,FK
        datetime assigned_at
    }

    USER ||--o{ SESSION : has
    USER ||--o{ PASSWORD_RESET : requests
    USER ||--o{ USER_ROLE : assigned
    ROLE ||--o{ USER_ROLE : includes
```

### E-Commerce Domain

```mermaid
erDiagram
    CUSTOMER {
        uuid id PK
        string email UK
        string name
        datetime created_at
    }

    ADDRESS {
        uuid id PK
        uuid customer_id FK
        string street
        string city
        string state
        string postal_code
        string country
        boolean is_default
    }

    ORDER {
        uuid id PK
        uuid customer_id FK
        uuid shipping_address_id FK
        string status
        decimal subtotal
        decimal tax
        decimal shipping
        decimal total
        datetime created_at
    }

    ORDER_ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        decimal unit_price
        decimal total
    }

    PRODUCT {
        uuid id PK
        uuid category_id FK
        string sku UK
        string name
        text description
        decimal price
        int stock_quantity
        boolean is_active
    }

    CATEGORY {
        uuid id PK
        uuid parent_id FK
        string name
        string slug UK
    }

    CUSTOMER ||--o{ ADDRESS : has
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER }o--|| ADDRESS : "shipped to"
    PRODUCT ||--o{ ORDER_ITEM : "ordered as"
    CATEGORY ||--o{ PRODUCT : contains
    CATEGORY |o--o{ CATEGORY : "parent of"
```

### Content Management System

```mermaid
erDiagram
    USER {
        uuid id PK
        string email UK
        string name
        string role
    }

    POST {
        uuid id PK
        uuid author_id FK
        string title
        string slug UK
        text content
        string status
        datetime published_at
        datetime created_at
    }

    CATEGORY {
        uuid id PK
        string name UK
        string slug UK
    }

    TAG {
        uuid id PK
        string name UK
        string slug UK
    }

    POST_CATEGORY {
        uuid post_id PK,FK
        uuid category_id PK,FK
    }

    POST_TAG {
        uuid post_id PK,FK
        uuid tag_id PK,FK
    }

    COMMENT {
        uuid id PK
        uuid post_id FK
        uuid user_id FK
        uuid parent_id FK
        text content
        datetime created_at
    }

    USER ||--o{ POST : authors
    USER ||--o{ COMMENT : writes
    POST ||--o{ COMMENT : has
    POST ||--o{ POST_CATEGORY : "belongs to"
    POST ||--o{ POST_TAG : "tagged with"
    CATEGORY ||--o{ POST_CATEGORY : includes
    TAG ||--o{ POST_TAG : includes
    COMMENT |o--o{ COMMENT : "reply to"
```

### Multi-Tenant SaaS

```mermaid
erDiagram
    ORGANIZATION {
        uuid id PK
        string name
        string slug UK
        string plan
        datetime created_at
    }

    USER {
        uuid id PK
        string email UK
        string name
        datetime created_at
    }

    MEMBERSHIP {
        uuid id PK
        uuid org_id FK
        uuid user_id FK
        string role
        datetime joined_at
    }

    PROJECT {
        uuid id PK
        uuid org_id FK
        string name
        datetime created_at
    }

    RESOURCE {
        uuid id PK
        uuid project_id FK
        string type
        json data
    }

    ORGANIZATION ||--o{ MEMBERSHIP : has
    USER ||--o{ MEMBERSHIP : "member of"
    ORGANIZATION ||--o{ PROJECT : owns
    PROJECT ||--o{ RESOURCE : contains
```

### Audit Trail Pattern

```mermaid
erDiagram
    ENTITY {
        uuid id PK
        string name
        datetime created_at
        datetime updated_at
    }

    AUDIT_LOG {
        uuid id PK
        uuid entity_id FK
        string entity_type
        uuid user_id FK
        string action
        json old_values
        json new_values
        string ip_address
        datetime created_at
    }

    USER {
        uuid id PK
        string email
    }

    ENTITY ||--o{ AUDIT_LOG : "tracked by"
    USER ||--o{ AUDIT_LOG : performs
```
