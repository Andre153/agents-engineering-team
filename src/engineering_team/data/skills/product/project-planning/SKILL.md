---
name: project-planning
description: "Project planning and tracking with structured markdown. Use when breaking down large projects into phases and tasks, or tracking progress across multi-phase work."
---

# Project Planning

## Quick Reference

| Resource | Description | Location |
|----------|-------------|----------|
| Planning Methodology | When/how to plan, phase design, anti-patterns | [planning-methodology.md](references/planning-methodology.md) |
| Task Breakdown | Decomposition strategies, task writing guide | [task-breakdown.md](references/task-breakdown.md) |
| Summary Template | Template for project summary.md | [summary-template.md](assets/summary-template.md) |
| Phase Template | Template for phase-N.md files | [phase-template.md](assets/phase-template.md) |

## When to Use

Create a project plan when:
- The work spans multiple files or components
- The work will take more than one session to complete
- There are more than 5 distinct tasks to track
- Multiple phases or milestones are involved
- Coordination between different areas of the codebase is needed

Do **not** create a project plan for:
- Quick fixes or single-file changes
- Bug fixes with an obvious solution
- Small refactors contained in one module
- Tasks that can be completed in a few minutes

## Directory Convention

Place project plans at the repository root:

```
projects/
└── <project-name>/
    ├── summary.md
    ├── phase-1.md
    ├── phase-2.md
    └── phase-3.md
```

Naming rules:
- Use lowercase, hyphen-separated names for project directories (e.g., `user-auth`, `api-migration`)
- Summary file is always `summary.md`
- Phase files follow the pattern `phase-N.md` where N starts at 1

## Creating a Project Plan

1. **Create the project directory** at `projects/<project-name>/`
2. **Write `summary.md`** using the [summary template](assets/summary-template.md) — define the goal, scope, phases, risks, and key decisions
3. **Write `phase-N.md` files** for each phase using the [phase template](assets/phase-template.md) — define the objective, tasks, acceptance criteria, and dependencies

## Phase Design Principles

- **Each phase produces a testable increment.** At the end of a phase, something new should work that didn't before. Avoid phases that are purely preparatory with no observable output.
- **Sequence phases from foundation to polish:** foundation (data models, schemas) → core logic (business rules, APIs) → integration (connecting components) → polish (error handling, edge cases, UX).
- **Most projects need 2-5 phases.** Fewer than 2 means the work probably doesn't need a plan. More than 5 suggests the project should be broken into separate efforts.
- **Phases should be roughly similar in size.** If one phase has 12 tasks and another has 2, rebalance.

## Task Design Principles

Good tasks are:
- **Concrete** — specify files, functions, or components to change
- **Small** — completable in a single focused session (15 min to 2 hours)
- **Verifiable** — you can tell when they're done

### Task Format

```markdown
- [ ] **Task title** -- Description with specific files, functions, or components.
```

### Status Annotations

Add annotations inline when a task is in progress or blocked:

```markdown
- [ ] **Add user model** -- Define User schema in models/user.ts. [IN PROGRESS]
- [ ] **Add email service** -- Integrate SendGrid for verification emails. [BLOCKED: waiting on API key]
- [x] **Create database migration** -- Add users table with email, password_hash, created_at.
```

## Updating Project Plans

- **Mark progress** by checking off tasks (`- [x]`) and updating phase status
- **Status values** for phases: `Not Started` → `In Progress` → `Blocked` → `Complete`
- **Record decisions** in the summary's Key Decisions table with date and reasoning
- **Update scope** if requirements change — add notes explaining what changed and why

## Example

A minimal project for adding user authentication:

**`projects/user-auth/summary.md`:**

```markdown
# User Authentication

## Goal
Add email/password authentication so users can create accounts and log in.

## Scope
**Included:**
- User registration with email and password
- Login and session management
- Password hashing

**Excluded:**
- OAuth / social login
- Password reset flow
- Two-factor authentication

## Status: In Progress

## Phases
| Phase | Description | Status |
|-------|-------------|--------|
| [Phase 1](phase-1.md) | Data model and auth logic | Complete |
| [Phase 2](phase-2.md) | API endpoints and middleware | In Progress |

## Key Decisions
| Date | Decision | Reasoning |
|------|----------|-----------|
| 2025-01-15 | Use bcrypt for hashing | Industry standard, built-in salt |

## Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Session fixation | High | Regenerate session ID on login |
```

**`projects/user-auth/phase-1.md`:**

```markdown
# Phase 1: Data Model and Auth Logic

## Objective
Create the user data model and core authentication functions.

## Tasks
- [x] **Create User model** -- Define schema in src/models/user.ts with email, password_hash, created_at.
- [x] **Add password hashing** -- Implement hashPassword and verifyPassword in src/auth/passwords.ts using bcrypt.
- [x] **Write auth tests** -- Unit tests for hashing and verification in tests/auth.test.ts.

## Acceptance Criteria
- [x] User model passes schema validation
- [x] Passwords are hashed and verified correctly
- [x] All tests pass

## Dependencies
- None (first phase)
```
