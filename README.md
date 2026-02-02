# Claude Code Agents & Skills

A reusable collection of Claude Code agents and skills that can be pulled into any project.

## Installation

### Option 1: Git Submodule (Recommended)

```bash
git submodule add <repo-url> .claude/extensions
```

### Option 2: Symlink

```bash
git clone <repo-url> ~/claude-agents
ln -s ~/claude-agents/agents .claude/agents
ln -s ~/claude-agents/skills .claude/skills
```

### Option 3: Copy

Copy the `agents/` and `skills/` directories into your project's `.claude/` directory.

---

## Available Agents

### senior-backend-developer

A senior polyglot backend developer for implementation.

- **Backend Development**: RESTful/GraphQL APIs, microservices, event-driven architecture
- **Architecture**: Domain-Driven Design (DDD), Vertical Slice Architecture, CQRS
- **Databases**: Relational (PostgreSQL) and Document (MongoDB/Firestore)
- **Best Practices**: SOLID principles, clean code, security-first

**Usage:**
```
Use the senior-backend-developer agent to implement the order management API in TypeScript
```

---

### backend-architect

A senior backend architect for planning and design (read-only, doesn't write code).

- **System Design**: Service boundaries, data flow, infrastructure patterns
- **Feature Architecture**: Component design, API contracts, integration points
- **Documentation**: Technical plans with Mermaid diagrams
- **Handoff**: Creates implementation specs for developer agents

**Usage:**
```
Use the backend-architect agent to design the authentication system architecture
```

**Workflow**: Architect creates plan → hands off to developer agent for implementation.

---

### senior-mobile-developer

A senior mobile developer specializing in hybrid cross-platform solutions (iOS and Android).

- **Cross-Platform**: Flutter (primary), React Native
- **Architecture**: Vertical Slice Architecture, Domain-Driven Design, separation of concerns
- **State Management**: BLoC/Cubit patterns, unidirectional data flow
- **Philosophy**: Simplicity first, elegant and maintainable solutions

**Usage:**
```
Use the senior-mobile-developer agent to implement the user profile feature in Flutter
```

---

## Available Skills

### typescript

TypeScript development expertise for backend and full-stack applications. Covers type system patterns, async programming, error handling, testing, and project architecture.

---

### flutter

Flutter development with Material Design 3, BLoC/Cubit state management, and GoRouter navigation. Covers widget composition, state patterns, typed routing, theming, and testing.

---

### mermaid

Mermaid diagramming for architecture documentation and technical planning. Covers flowcharts, sequence diagrams, ERDs, class diagrams, and state diagrams.

---

### gcp-cloud-firebase

Google Cloud Platform and Firebase development. Covers Cloud Run, Authentication, Storage, Functions, and Hosting.

---

### database-firestore

Firestore database design, querying, and best practices. Covers data modeling, compound queries, pagination, indexing, and security rules.

---

## Using Skills with Agents

### Preload skills in agent frontmatter:

```yaml
---
name: senior-backend-developer
skills:
  - typescript
  - gcp-cloud-firebase
  - database-firestore
---
```

### Or mention in prompt:

```
Use the senior-backend-developer agent with the typescript and gcp-cloud-firebase skills to build the user API
```

---

## Creating New Agents

```markdown
---
name: my-agent
description: What this agent does and when to use it
tools: Read, Write, Edit, Glob, Grep, Bash
model: sonnet
skills:
  - typescript
---

Your agent instructions here...
```

## Creating New Skills

Each skill requires a `SKILL.md` file (under 500 lines) with optional `references/` for detailed docs and `assets/` for templates.

---

## Roadmap

### Planned Agents
- [ ] Frontend developer (React)
- [ ] DevOps engineer (Docker, CI/CD)

### Planned Skills
- [ ] Python
- [ ] NestJS
- [ ] PostgreSQL
- [ ] Docker

---

## License

MIT
