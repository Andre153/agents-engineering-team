# Planning Methodology

## When to Plan

A project needs a plan when the work is large enough that you can't hold it all in your head, or when progress needs to be tracked across sessions.

**Signals that warrant a plan:**
- Multiple components or files need coordinated changes
- The work will span more than one session
- There are more than 5 distinct tasks
- Other people need visibility into progress
- The order of operations matters (some tasks depend on others)

**When planning is overhead:**
- The fix is obvious and localized
- The entire change fits in one file
- You can describe the work in a single sentence
- The task will take less than 30 minutes

## Project Sizing

Use the number of components affected and the scope of changes to estimate project size:

### Small (1-2 phases)
- Affects 1-3 files or modules
- Single area of the codebase
- Can be completed in 1-2 sessions
- Example: add a new API endpoint with tests

### Medium (2-3 phases)
- Affects 3-8 files across 2-3 areas
- Requires some sequencing (data model before API before UI)
- Takes 2-5 sessions
- Example: add a new feature with data model, API, and basic UI

### Large (3-5 phases)
- Affects 8+ files across multiple areas
- Significant sequencing dependencies
- Takes a week or more
- Example: migrate authentication system, add multi-tenant support

If a project seems to need more than 5 phases, consider breaking it into separate projects that can be planned and executed independently.

## Phase Design

### The Vertical Slice Principle

Each phase should produce a **testable increment** — something that works end-to-end, even if narrowly. This is better than horizontal slices (all models, then all APIs, then all UI) because:

- You get feedback earlier
- Bugs surface when components integrate, not at the end
- Each phase has clear acceptance criteria
- Progress is visible and demonstrable

**Good phase boundary:** "After this phase, users can register and log in" (testable)

**Bad phase boundary:** "After this phase, all database models are defined" (not independently testable)

### Ordering Strategy

When deciding phase order, prioritize:

1. **Riskiest first** — tackle the most uncertain or technically challenging work early, when there's still time to adjust the plan
2. **Data before API before UI** — downstream components depend on upstream contracts, so stabilize those first
3. **Core before edge cases** — get the happy path working, then handle errors and edge cases
4. **Shared before specific** — build reusable foundations before the features that use them

### Phase Size

Aim for **4-7 tasks per phase**. This keeps phases focused and completable in a reasonable time.

- Fewer than 3 tasks: the phase may be too thin — consider merging with an adjacent phase
- More than 8 tasks: the phase may be too large — look for a natural split point

## Iterative Refinement

Plans are living documents. They should be updated as you learn more.

### When to Update the Plan

- A task turns out to be more complex than expected — split it or add a phase
- Requirements change — update scope, add/remove tasks, note the change and reasoning
- A risk materializes — update the risk table, adjust affected phases
- A phase is complete — update status, record any decisions made during implementation

### Progress Check Rhythm

At the start of each session:
1. Read the project summary to recall context
2. Check the current phase for the next incomplete task
3. Update any status annotations from the previous session

At the end of each session:
1. Mark completed tasks
2. Add `[IN PROGRESS]` or `[BLOCKED]` annotations as needed
3. Update the phase status in the summary if a phase was completed

## Common Anti-Patterns

### Vague Tasks
**Bad:** `- [ ] **Handle errors** -- Add error handling.`
**Good:** `- [ ] **Add validation to /users endpoint** -- Return 400 for missing email, 409 for duplicate email in src/routes/users.ts.`

Why: vague tasks can't be verified and tend to expand in scope.

### Unclear Phase Boundaries
**Bad:** Phase 1 is "Backend" and Phase 2 is "Frontend" with no integration testing.
**Good:** Phase 1 is "User registration end-to-end" including the minimal backend and frontend needed.

Why: horizontal slices defer integration risk to the end, where it's most expensive.

### Over-Planning
**Bad:** Spending two hours writing a plan for a task that takes one hour.
**Good:** Matching plan detail to project complexity — a 2-phase project needs a brief summary, not a 10-page document.

Why: the plan is a tool to reduce risk, not an end in itself. If the planning takes longer than the work, skip the plan.

### Under-Specified Acceptance Criteria
**Bad:** `- [ ] It works`
**Good:** `- [ ] POST /users returns 201 with user ID; - [ ] Duplicate email returns 409; - [ ] All tests pass`

Why: vague criteria make it impossible to tell when a phase is actually done, leading to scope creep and rework.

### Not Recording Decisions
**Bad:** Changing approach mid-project without noting why.
**Good:** Adding to the Key Decisions table: "Switched from JWT to session cookies because we need server-side revocation."

Why: future readers (including future you) need context on why choices were made to avoid re-litigating them.
