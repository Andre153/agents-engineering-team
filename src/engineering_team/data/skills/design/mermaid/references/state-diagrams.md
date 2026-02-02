# Mermaid State Diagrams

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [States](#states)
- [Transitions](#transitions)
- [Composite States](#composite-states)
- [Common Patterns](#common-patterns)

## Basic Syntax

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing : start
    Processing --> Complete : success
    Processing --> Failed : error
    Complete --> [*]
    Failed --> [*]
```

## States

### Simple States

```mermaid
stateDiagram-v2
    state "Waiting for Input" as waiting
    state "Processing Request" as processing
    state "Request Complete" as complete

    [*] --> waiting
    waiting --> processing
    processing --> complete
    complete --> [*]
```

### State Descriptions

```mermaid
stateDiagram-v2
    state Active {
        [*] --> Running
        Running --> Paused : pause
        Paused --> Running : resume
    }

    note right of Active : System is operational
```

## Transitions

### Labeled Transitions

```mermaid
stateDiagram-v2
    Idle --> Active : activate()
    Active --> Idle : deactivate()
    Active --> Error : onError
    Error --> Idle : reset()
```

### Conditional Transitions

```mermaid
stateDiagram-v2
    state check <<choice>>

    [*] --> Validating
    Validating --> check
    check --> Approved : valid
    check --> Rejected : invalid
    Approved --> [*]
    Rejected --> [*]
```

### Fork and Join

```mermaid
stateDiagram-v2
    state fork_state <<fork>>
    state join_state <<join>>

    [*] --> fork_state
    fork_state --> TaskA
    fork_state --> TaskB
    fork_state --> TaskC
    TaskA --> join_state
    TaskB --> join_state
    TaskC --> join_state
    join_state --> Complete
    Complete --> [*]
```

## Composite States

### Nested States

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Idle
        Idle --> Working : start
        Working --> Idle : complete

        state Working {
            [*] --> Fetching
            Fetching --> Processing
            Processing --> Saving
            Saving --> [*]
        }
    }

    Active --> Inactive : disable
    Inactive --> Active : enable
```

### Concurrent States

```mermaid
stateDiagram-v2
    [*] --> Active

    state Active {
        [*] --> Running

        state Running {
            --
            state "UI Thread" as ui {
                [*] --> Rendering
                Rendering --> Updating
                Updating --> Rendering
            }
            --
            state "Background" as bg {
                [*] --> Polling
                Polling --> Processing
                Processing --> Polling
            }
        }
    }
```

## Common Patterns

### Order Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Draft

    Draft --> Submitted : submit()
    Submitted --> Confirmed : confirm()
    Submitted --> Cancelled : cancel()

    Confirmed --> Processing : process()
    Confirmed --> Cancelled : cancel()

    Processing --> Shipped : ship()
    Processing --> Cancelled : cancel()

    Shipped --> Delivered : deliver()
    Shipped --> Returned : return()

    Delivered --> Returned : return()
    Delivered --> [*]

    Returned --> Refunded : refund()
    Refunded --> [*]

    Cancelled --> [*]
```

### Authentication Flow

```mermaid
stateDiagram-v2
    [*] --> Unauthenticated

    state Unauthenticated {
        [*] --> Idle
        Idle --> LoggingIn : login()
        LoggingIn --> Idle : failed
    }

    state Authenticated {
        [*] --> Active
        Active --> Refreshing : tokenExpiring
        Refreshing --> Active : refreshed
        Refreshing --> Expired : refreshFailed
    }

    Unauthenticated --> Authenticated : loginSuccess
    Authenticated --> Unauthenticated : logout
    Authenticated --> Unauthenticated : expired
```

### Request Processing

```mermaid
stateDiagram-v2
    [*] --> Pending

    state Pending {
        [*] --> Queued
        Queued --> Validating : dequeue
    }

    state Processing {
        [*] --> Executing
        Executing --> Retrying : transientError
        Retrying --> Executing : retry
        Retrying --> Failed : maxRetries
        Executing --> Completed : success
    }

    Pending --> Processing : validated
    Pending --> Rejected : invalid

    Completed --> [*]
    Failed --> [*]
    Rejected --> [*]
```

### WebSocket Connection

```mermaid
stateDiagram-v2
    [*] --> Disconnected

    state Disconnected {
        [*] --> Idle
        Idle --> Connecting : connect()
    }

    state Connected {
        [*] --> Ready
        Ready --> Sending : send()
        Sending --> Ready : sent
        Ready --> Receiving : messageReceived
        Receiving --> Ready : processed
    }

    state Reconnecting {
        [*] --> Waiting
        Waiting --> Attempting : timeout
        Attempting --> Waiting : failed
    }

    Disconnected --> Connected : connected
    Connected --> Reconnecting : connectionLost
    Connected --> Disconnected : disconnect()
    Reconnecting --> Connected : reconnected
    Reconnecting --> Disconnected : maxAttempts
```

### Payment State Machine

```mermaid
stateDiagram-v2
    [*] --> Created

    state check <<choice>>

    Created --> Authorizing : authorize()
    Authorizing --> check

    check --> Authorized : approved
    check --> Declined : declined
    check --> RequiresAction : requires3DS

    RequiresAction --> Authorizing : complete3DS
    RequiresAction --> Cancelled : abandon

    Authorized --> Capturing : capture()
    Authorized --> Cancelled : cancel()

    Capturing --> Captured : success
    Capturing --> CaptureFailed : error

    Captured --> Refunding : refund()
    Refunding --> Refunded : success
    Refunding --> RefundFailed : error

    Captured --> [*]
    Refunded --> [*]
    Cancelled --> [*]
    Declined --> [*]
```
