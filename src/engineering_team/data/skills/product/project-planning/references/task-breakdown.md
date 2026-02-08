# Task Breakdown

## Decomposition Strategies

### Top-Down Decomposition

Start with the end goal and break it into major pieces, then break each piece into tasks.

```
Add user authentication
├── Phase 1: Data model and auth logic
│   ├── Create User model
│   ├── Add password hashing
│   └── Write auth unit tests
├── Phase 2: API endpoints
│   ├── Add registration endpoint
│   ├── Add login endpoint
│   ├── Add auth middleware
│   └── Write integration tests
└── Phase 3: Session management
    ├── Add session store
    ├── Add logout endpoint
    └── Write session tests
```

Best for: well-understood domains where the structure is clear upfront.

### Component-Based Decomposition

Identify the components that need to change, then list what changes each component needs.

```
Shopping cart feature
├── Database (Phase 1)
│   ├── Cart table migration
│   └── CartItem table migration
├── API layer (Phase 1)
│   ├── POST /cart/items endpoint
│   ├── DELETE /cart/items/:id endpoint
│   └── GET /cart endpoint
├── Business logic (Phase 2)
│   ├── Cart total calculation
│   ├── Stock validation
│   └── Price computation
└── UI (Phase 2)
    ├── Cart page component
    ├── Add-to-cart button
    └── Cart badge in header
```

Best for: full-stack features that touch multiple layers.

### Risk-First Decomposition

Identify the riskiest or most uncertain parts first, and tackle those in early phases.

```
Third-party API integration
├── Phase 1: Prove feasibility (riskiest)
│   ├── API client prototype
│   ├── Test authentication flow
│   └── Verify rate limits are acceptable
├── Phase 2: Build integration (moderate risk)
│   ├── Production API client with retry logic
│   ├── Error handling and fallbacks
│   └── Integration tests with mocked API
└── Phase 3: Production readiness (low risk)
    ├── Monitoring and alerting
    ├── Rate limit management
    └── Documentation
```

Best for: projects with significant unknowns or external dependencies.

## Task Writing Guide

### Anatomy of a Good Task

```markdown
- [ ] **Action verb + what** -- Where (specific files/functions) and how (approach if non-obvious).
```

Components:
1. **Checkbox** (`- [ ]`) — for tracking completion
2. **Bold title** — starts with an action verb, describes the deliverable
3. **Description** — specifies files, functions, or components; explains the approach if not obvious

### Action Verbs

Use precise verbs that describe the type of work:

| Verb | When to use |
|------|------------|
| Create | New file, component, or module from scratch |
| Add | New function, field, or capability to existing code |
| Update | Change existing behavior or implementation |
| Remove | Delete code, files, or features |
| Refactor | Restructure without changing behavior |
| Extract | Pull code into a new function, module, or component |
| Replace | Swap one implementation for another |
| Configure | Set up tooling, environment, or settings |
| Write | Tests, documentation, or scripts |
| Fix | Correct a specific bug or issue |

### Examples by Type

**Data model task:**
```markdown
- [ ] **Create Order model** -- Define Order schema in src/models/order.ts with fields: id (uuid), userId (fk), items (OrderItem[]), total (decimal), status (enum: pending/paid/shipped), createdAt, updatedAt.
```

**API endpoint task:**
```markdown
- [ ] **Add POST /orders endpoint** -- In src/routes/orders.ts, accept { items: [{productId, quantity}] }, validate stock, calculate total, create order. Return 201 with order ID or 400 for validation errors.
```

**Refactoring task:**
```markdown
- [ ] **Extract auth middleware** -- Move token validation from src/routes/users.ts inline handler into src/middleware/auth.ts as reusable middleware. Update users and orders routes to use it.
```

**Test task:**
```markdown
- [ ] **Write Order model tests** -- In tests/models/order.test.ts, test: creation with valid data, validation rejects negative total, status transitions follow allowed paths, timestamps are set automatically.
```

**Configuration task:**
```markdown
- [ ] **Configure CI pipeline** -- Add .github/workflows/ci.yml: run lint, type-check, and tests on push to main and on PRs. Use Node 20, cache node_modules.
```

## Common Task Patterns

### CRUD Feature Template

For a typical create/read/update/delete feature:

```markdown
- [ ] **Create [Resource] model** -- Define schema in src/models/[resource].ts with fields: [list fields].
- [ ] **Add database migration** -- Create migration for [resource] table with columns matching the model.
- [ ] **Add [Resource] repository** -- Implement create, findById, findAll, update, delete in src/repositories/[resource].ts.
- [ ] **Add [Resource] validation** -- Input validation for create/update in src/validation/[resource].ts.
- [ ] **Add CRUD endpoints** -- In src/routes/[resource].ts: POST, GET /:id, GET / (list), PUT /:id, DELETE /:id.
- [ ] **Write [Resource] tests** -- Unit tests for model and repository, integration tests for endpoints.
```

### Migration / Refactoring Template

For moving from one approach to another:

```markdown
- [ ] **Create new implementation** -- Build [new approach] in [location] alongside existing code.
- [ ] **Add adapter layer** -- Create adapter in [location] that supports both old and new implementations.
- [ ] **Migrate consumers** -- Update [list of files] to use the new implementation via the adapter.
- [ ] **Write migration tests** -- Verify old and new implementations produce identical results for [key scenarios].
- [ ] **Remove old implementation** -- Delete [old files] and remove the adapter layer.
```

### Bug Fix Template

For structured bug fixes:

```markdown
- [ ] **Write failing test** -- In [test file], add test that reproduces the bug: [describe scenario and expected vs actual behavior].
- [ ] **Fix [the issue]** -- In [file:function], [describe the fix].
- [ ] **Add regression tests** -- Test edge cases related to the fix: [list cases].
```

## Task Sizing

Tasks should be small enough to complete in a single focused session but large enough to be meaningful.

| Size | Time | Description | Action |
|------|------|-------------|--------|
| Tiny | < 15 min | Single-line change, config tweak | Consider grouping with related tasks |
| Small | 15-45 min | Add a function, write a few tests | Ideal size |
| Medium | 45 min - 2 hours | New component, several related changes | Acceptable |
| Large | 2-4 hours | Multiple files, complex logic | Consider splitting |
| Too large | > 4 hours | Essentially a phase unto itself | Must be split |

When splitting a large task, look for natural boundaries:
- Separate the data layer from the API layer
- Separate the implementation from the tests
- Separate the core logic from error handling
- Separate creation from update/delete

## Dependency Management

### Explicit Dependencies

Note dependencies in the phase's Dependencies section, not on individual tasks. Tasks within a phase are assumed to be loosely ordered (top to bottom) but not strictly dependent.

Cross-phase dependencies are captured by the phase ordering itself — Phase 2 depends on Phase 1 being complete.

### Reducing Dependencies

To make phases more parallelizable:
- Define interfaces and contracts early, so downstream work can proceed against the interface
- Use mocks or stubs when the real implementation isn't ready
- Prefer thin vertical slices (one feature end-to-end) over thick horizontal slices (all models, then all APIs)

### Phase Dependencies

If phases have non-linear dependencies (e.g., Phase 3 depends on Phase 1 but not Phase 2), note this explicitly in the Dependencies section of the phase file:

```markdown
## Dependencies
- Phase 1 must be complete (provides the User model)
- Phase 2 is independent and can proceed in parallel
```
